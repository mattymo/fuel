require 'pathname'
require Pathname.new(__FILE__).dirname.dirname.expand_path + 'corosync_service'
require 'rexml/document'
require 'open3'

include REXML

Puppet::Type.type(:service).provide :pacemaker, :parent => Puppet::Provider::Corosync_service do

  commands :crm => 'crm'
  commands :cibadmin => 'cibadmin'
  commands :crm_attribute => 'crm_attribute'

  desc "Pacemaker service management."

  has_feature :refreshable
  has_feature :enableable
  has_feature :ensurable
  def self.get_cib
    raw, _status = dump_cib
    @@cib=REXML::Document.new(raw)
  end

  # List all services of this type.
  def self.instances
    get_services
  end

  #Return list of pacemaker resources
  def self.get_resources
    @@resources = @@cib.root.elements['configuration'].elements['resources']
  end

  #Get services list
  def self.get_services
    get_cib
    get_resources
    instances = []
    XPath.match(@@resources, '//primitive').each do |element|
      if !element.nil?
        instances << new(:name => element.attributes['id'], :hasstatus => true, :hasrestart => false)
      end
    end
    instances
  end

  def get_service_hash
    self.class.get_cib
    self.class.get_resources
    @service={}
    default_start_timeout = 30
    default_stop_timeout = 30
    resource = XPath.first(@@resources, "//primitive[@id='#{@resource[:name]}']")
    @service[:msname] = ['master','clone'].include?(resource.parent.name) ? resource.parent.attributes['id'] : nil
    @service[:name] = @resource[:name]
    @service[:class] = resource.attributes['class']
    @service[:provider] = resource.attributes['provider']
    @service[:type] = resource.attributes['type']
    @service[:metadata] = {}
    if !resource.elements['meta_attributes'].nil?
      resource.elements['meta_attributes'].each_element do |m|
        @service[:metadata][m.attributes['name'].to_sym] = m.attributes['value']
      end
    end
    if @service[:class] == 'ocf'
      stdin, stdout, stderr =  Open3.popen3("/bin/bash -c 'OCF_ROOT=/usr/lib/ocf /usr/lib/ocf/resource.d/#{@service[:provider]}/#{@service[:type]} meta-data'")
      metadata = REXML::Document.new(stdout)
      default_start_timeout = XPath.first(metadata, "//actions/action[@name=\'start\']").attributes['timeout'].to_i
      default_stop_timeout = XPath.first(metadata, "//actions/action[@name=\'stop\']").attributes['timeout'].to_i
    end
    op_start=XPath.first(resource,"//operations/op[@name=\'start\']")
    op_stop=XPath.first(resource,"//operations/op[@name=\'stop\']")
    @service[:start_timeout] =  default_start_timeout
    @service[:stop_timeout] =  default_stop_timeout
    if !op_start.nil?
      @service[:start_timeout] = op_start.attributes['timeout'].to_i
    end
    if !op_stop.nil?
      @service[:stop_timeout] = op_stop.attributes['timeout'].to_i
    end
  end

  def get_service_name
    get_service_hash
    service_name = @service[:msname] ? @service[:msname] : @service[:name]
  end

  def self.get_stonith
    get_cib
    stonith = XPath.first(@@cib,"crm_config/nvpair[@name='stonith-enabled']")
    @@stonith = stonith == "true"
  end

  def self.get_node_state_stonith(ha_state,in_ccm,crmd,join,expected,shutdown)
    if (in_ccm == "true") && (ha_state == 'active') && (crmd == 'online')
      case join
      when 'member'
        state = :online
      when 'expected'
        state = :offline
      when 'pending'
        state = :pending
      when 'banned'
        state = :standby
      else
        state = :unclean
      end
    elsif !(in_ccm == "true") && (ha_state =='dead') && (crmd == 'offline') && !(shutdown == 0)
      state = :offline
    elsif shutdown == 0
      state = :unclean
    else
      state = :offline
    end
    state
  end

  def self.get_node_state_no_stonith(ha_state,in_ccm,crmd,join,expected,shutdown)
    state = :unclean
    if !(in_ccm == "true") || (ha_state == 'dead')
      state = :offline
    elsif crmd == 'online'
      if join == 'member'
        state = :online
      else
        state = :offline
      end
    elsif !(shutdown == "0")
      state = :offline
    else
      state = :unclean
    end
    state
  end

  def self.get_node_state(*args)
    get_stonith
    if @@stonith
      return get_node_state_stonith(*args)
    else
      return get_node_state_no_stonith(*args)
    end
  end

  def self.get_nodes
    @@nodes = []
    get_cib
    nodes = XPath.match(@@cib,'cib/configuration/nodes/node')
    nodes.each do |node|
      state = :unclean
      uname = node.attributes['uname']
      node_state = XPath.first(@@cib,"cib/status/node_state[@uname='#{uname}']")
      if node_state
        ha_state = node_state.attributes['ha'] == 'dead' ? 'dead' : 'active'
        in_ccm  = node_state.attributes['in_ccm']
        crmd = node_state.attributes['crmd']
        join = node_state.attributes['join']
        expected = node_state.attributes['expected']
        shutdown = node_state.attributes['shutdown'].nil? ? 0 : node_state.attributes['shutdown']
        state = get_node_state(ha_state,in_ccm,crmd,join,expected,shutdown)
        if state == :online
          standby = node.elements["instance_attributes/nvpair[@name='standby']"]
          if standby && ['true', 'yes', '1', 'on'].include?(standby.attributes['value'])
            state = :standby
          end
        end
      end
      @@nodes << {:uname => uname, :state => state}
    end
  end

  def get_last_successful_operations
    self.class.get_cib
    self.class.get_nodes
    @last_successful_operations = []
    @@nodes.each do |node|
      next unless node[:state] == :online
      debug("getting last ops on #{node[:uname]} for #{@resource[:name]}")
      all_operations =  XPath.match(@@cib,"cib/status/node_state[@uname='#{node[:uname]}']/lrm/lrm_resources/lrm_resource/lrm_rsc_op[starts-with(@id,'#{@resource[:name]}')]")
      next if all_operations.nil?
      completed_ops = all_operations.select{|op| op.attributes['op-status'].to_i != -1 }
      next if completed_ops.nil?
      start_stop_ops = completed_ops.select{|op| ["start","stop","monitor"].include? op.attributes['operation']}
      next if start_stop_ops.nil?
      sorted_operations = start_stop_ops.sort do
        |a,b| a.attributes['call-id'] <=> b.attributes['call-id']
      end
      good_operations = sorted_operations.select do |op|
        op.attributes['rc-code'] == '0' or
        op.attributes['operation'] == 'monitor'
      end
      next if good_operations.nil?
      last_op = good_operations.last
      next if last_op.nil?
      last_successful_op = nil
      if ['start','stop'].include?(last_op.attributes['operation'])
        last_successful_op = last_op.attributes['operation']
      else
        if last_op.attributes['rc-code'].to_i == 7
          last_successful_op = 'stop'
        elsif last_op.attributes['rc-code'].to_i == 0
          last_successful_op = 'start'
        elsif  last_op.attributes['rc-code'].to_i == 8
          last_successful_op = 'start'
        end
      end
      @last_successful_operations << last_successful_op if !last_successful_op.nil?
    end
    @last_successful_operations
  end

  #  def get_operations
  #     XPath.match(@@operations,"lrm_rsc_op")
  #  end

  def enable
    crm('resource','manage', @resource[:name])
  end

  def enabled?
    get_service_hash
    @service[:metadata][:'is-managed'] != 'false'
  end

  def disable
    crm('resource','unmanage',@resource[:name])
  end

  #TODO: think about per-node start/stop/restart of services

  def start
    get_service_hash
    enable
    crm('resource', 'start', get_service_name)
    debug("Starting countdown for resource start")
    debug("Start timeout is #{@service[:start_timeout]}")
    Timeout::timeout(@service[:start_timeout],Puppet::Error) do
      loop do
        break if status == :running
        sleep 1
      end
    end
  end

  def stop
    get_service_hash
    enable
    crm('resource', 'stop', get_service_name)
    debug("Starting countdown for resource stop")
    debug("Stop timeout is #{@service[:stop_timeout]}")
    Timeout::timeout(@service[:stop_timeout],Puppet::Error) do
      loop do
        break if status == :stopped
        sleep 1
      end
    end
  end

  def restart
    stop
    start
  end

  def status
    debug("getting last operations")
    get_last_successful_operations
    if @last_successful_operations.any? {|op| op == 'start'}
      return :running
    elsif @last_successful_operations.all? {|op| op == 'stop'} or @last_successful_operations.empty?
      return :stopped
    else
      raise(Puppet::Error,"resource #{@resource[:name]} in unknown state")
    end
  end

end

