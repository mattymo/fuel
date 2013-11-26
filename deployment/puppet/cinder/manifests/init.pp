#
# == Parameters
#
# [sql_idle_timeout]
#   Timeout when db connections should be reaped.
#   (Optional) Defaults to 3600.
#
# [use_syslog]
#   Use syslog for logging.
#   (Optional) Defaults to false.
#
# [log_facility]
#   Syslog facility to receive log lines.
#   (Optional) Defaults to LOG_USER.
#
# parameters that may need to be added
# $state_path = /opt/stack/data/cinder
# $osapi_volume_extension = cinder.api.openstack.volume.contrib.standard_extensions
# $root_helper = sudo /usr/local/bin/cinder-rootwrap /etc/cinder/rootwrap.conf
# $use_syslog = Rather or not service should log to syslog. Optional.
# $syslog_log_facility = Facility for syslog, if used. Optional.
# $syslog_log_level = logging level for non verbose and non debug mode. Optional.

class cinder (
  $sql_connection,
  $sql_idle_timeout            = '3600',
  $rpc_backend                 = 'cinder.openstack.common.rpc.impl_kombu',
  $control_exchange            = 'openstack',
  $rabbit_host                 = '127.0.0.1',
  $rabbit_port                 = 5672,
  $rabbit_hosts                = false,
  $rabbit_virtual_host         = '/',
  $rabbit_userid               = 'guest',
  $rabbit_password             = false,
  $qpid_hostname               = 'localhost',
  $qpid_hosts                  = false,
  $qpid_port                   = '5672',
  $qpid_username               = 'guest',
  $qpid_password               = false,
  $qpid_reconnect              = true,
  $qpid_reconnect_timeout      = 0,
  $qpid_reconnect_limit        = 0,
  $qpid_reconnect_interval_min = 0,
  $qpid_reconnect_interval_max = 0,
  $qpid_reconnect_interval     = 0,
  $qpid_heartbeat              = 60,
  $qpid_protocol               = 'tcp',
  $qpid_tcp_nodelay            = true,
  $package_ensure              = 'present',
  $api_paste_config            = '/etc/cinder/api-paste.ini',
  $use_syslog                  = false,
  $log_facility                = 'LOG_USER',
  $syslog_log_level            = 'WARNING',
  $log_dir                     = '/var/log/cinder',
  $verbose                     = false,
  $debug                       = false,
) {
  #######$syslog_log_facility    = "LOGUSER3",

  include cinder::params

  if !defined(Package[$::cinder::params::qemuimg_package_name])
  {
    package {$::cinder::params::qemuimg_package_name:}
  }

  Package['cinder'] -> Cinder_config<||>
  Package['cinder'] -> Cinder_api_paste_ini<||>

  # this anchor is used to simplify the graph between cinder components by
  # allowing a resource to serve as a point where the configuration of cinder
  # begins
  anchor { 'cinder-start': }

  package { 'cinder':
    ensure  => $package_ensure,
    name    => $::cinder::params::package_name,
    require => Anchor['cinder-start'],
  }

  file { $::cinder::params::cinder_conf:
    ensure  => present,
    owner   => 'cinder',
    group   => 'cinder',
    mode    => '0600',
    require => Package['cinder'],
  }

  file { $::cinder::params::cinder_paste_api_ini:
    ensure  => present,
    owner   => 'cinder',
    group   => 'cinder',
    mode    => '0600',
    require => Package['cinder'],
  }
  if $use_syslog and !$debug =~ /(?i)(true|yes)/ {
    cinder_config {
      'DEFAULT/log_config': value => "/etc/cinder/logging.conf";
      'DEFAULT/log_file':   ensure=> absent;
      'DEFAULT/log_dir':    ensure=> absent;
      'DEFAULT/logfile':   ensure=> absent;
      'DEFAULT/logdir':    ensure=> absent;
      'DEFAULT/use_stderr': ensure=> absent;
      'DEFAULT/use_syslog': value => true;
      'DEFAULT/syslog_log_facility': value =>  $log_facility;
    }
    file { "cinder-logging.conf":
      content => template('cinder/logging.conf.erb'),
      path    => "/etc/cinder/logging.conf",
      require => File[$::cinder::params::cinder_conf],
    }
  }
  else {
    cinder_config {
      'DEFAULT/log_config': ensure => absent;
      'DEFAULT/use_syslog': value => false;
      'DEFAULT/syslog_log_facility': ensure => absent;
      'DEFAULT/use_stderr': ensure => absent;
      'DEFAULT/logdir':value => $log_dir;
      'DEFAULT/logging_context_format_string':
        value => '%(asctime)s %(levelname)s %(name)s [%(request_id)s %(user_id)s %(project_id)s] %(instance)s %(message)s';
      'DEFAULT/logging_default_format_string':
        value => '%(asctime)s %(levelname)s %(name)s [-] %(instance)s %(message)s';
    }
    # might be used for stdout logging instead, if configured
    file { "cinder-logging.conf":
      content => template('cinder/logging.conf-nosyslog.erb'),
      path    => "/etc/cinder/logging.conf",
      require => File[$::cinder::params::cinder_conf],
    }
  }
  # We must notify services to apply new logging rules
  File['cinder-logging.conf'] ~> Service<| title == "$::cinder::params::api_service" |>
  File['cinder-logging.conf'] ~> Service<| title == "$::cinder::params::volume_service" |>
  File['cinder-logging.conf'] ~> Service<| title == "$::cinder::params::scheduler_service" |>


  # Temporary fixes
  file { ['/var/log/cinder', '/var/lib/cinder']:
    ensure => directory,
    owner  => 'cinder',
    group  => 'cinder',
  }

  if $rpc_backend == 'cinder.openstack.common.rpc.impl_kombu' {

    if ! $rabbit_password {
      fail('Please specify a rabbit_password parameter.')
    }

    cinder_config {
      'DEFAULT/rabbit_password':     value => $rabbit_password, secret => true;
      'DEFAULT/rabbit_userid':       value => $rabbit_userid;
      'DEFAULT/rabbit_virtual_host': value => $rabbit_virtual_host;
      'DEFAULT/control_exchange':    value => $control_exchange;
    }

    if $rabbit_hosts {
      cinder_config { 'DEFAULT/rabbit_hosts':     value => join($rabbit_hosts,
',') }
      cinder_config { 'DEFAULT/rabbit_ha_queues': value => true }
    } else {
      cinder_config { 'DEFAULT/rabbit_host':      value => $rabbit_host }
      cinder_config { 'DEFAULT/rabbit_port':      value => $rabbit_port }
      cinder_config { 'DEFAULT/rabbit_hosts':     value =>
"${rabbit_host}:${rabbit_port}" }
      cinder_config { 'DEFAULT/rabbit_ha_queues': value => false }
    }
  }

  if $rpc_backend == 'cinder.openstack.common.rpc.impl_qpid' {

    if ! $qpid_password {
      fail('Please specify a qpid_password parameter.')
    }
    if $qpid_hosts {
      cinder_config { 'DEFAULT/qpid_hosts':     value => join($qpid_hosts,',') }
    } else {
      cinder_config { 'DEFAULT/qpid_hostname':     value => $qpid_hostname }
    }
    cinder_config {
      'DEFAULT/qpid_port':                   value => $qpid_port;
      'DEFAULT/qpid_username':               value => $qpid_username;
      'DEFAULT/qpid_password':               value => $qpid_password, secret => true;
      'DEFAULT/qpid_reconnect':              value => $qpid_reconnect;
      'DEFAULT/qpid_reconnect_timeout':      value => $qpid_reconnect_timeout;
      'DEFAULT/qpid_reconnect_limit':        value => $qpid_reconnect_limit;
      'DEFAULT/qpid_reconnect_interval_min': value =>
$qpid_reconnect_interval_min;
      'DEFAULT/qpid_reconnect_interval_max': value =>
$qpid_reconnect_interval_max;
      'DEFAULT/qpid_reconnect_interval':     value => $qpid_reconnect_interval;
      'DEFAULT/qpid_heartbeat':              value => $qpid_heartbeat;
      'DEFAULT/qpid_protocol':               value => $qpid_protocol;
      'DEFAULT/qpid_tcp_nodelay':            value => $qpid_tcp_nodelay;
    }
  }

  cinder_config {
    'DEFAULT/sql_connection':      value => $sql_connection, secret => true;
    'DEFAULT/sql_idle_timeout':    value => $sql_idle_timeout;
    'DEFAULT/verbose':             value => $verbose;
    'DEFAULT/debug':               value => $debug;
    'DEFAULT/api_paste_config':    value => $api_paste_config;
    'DEFAULT/rpc_backend':         value => $rpc_backend;
  }

#  if $use_syslog {
#    cinder_config {
#      'DEFAULT/use_syslog':           value => true;
#      'DEFAULT/syslog_log_facility':  value => $log_facility;
#    }
#  } else {
#    cinder_config {
#      'DEFAULT/use_syslog':           value => false;
#    }
#  }

}
