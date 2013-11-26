#
# parameters that may need to be added
# $state_path = /opt/stack/data/cinder
# $osapi_volume_extension = cinder.api.openstack.volume.contrib.standard_extensions
# $root_helper = sudo /usr/local/bin/cinder-rootwrap /etc/cinder/rootwrap.conf
# $use_syslog = Rather or not service should log to syslog. Optional.
# $syslog_log_facility = Facility for syslog, if used. Optional.
# $syslog_log_level = logging level for non verbose and non debug mode. Optional.

class cinder::base (
  $rabbit_password,
  $qpid_password,
  $sql_connection,
  $rpc_backend            = 'cinder.openstack.common.rpc.impl_kombu',
  $qpid_rpc_backend       = 'cinder.openstack.common.rpc.impl_qpid',
  $queue_provider         = 'rabbitmq',
  $rabbit_host            = false,
  $rabbit_hosts           = ['127.0.0.1'],
  $rabbit_port            = 5672,
  $rabbit_virtual_host    = '/',
  $rabbit_userid          = 'nova',
  $qpid_host              = false,
  $qpid_hosts             = ['127.0.0.1'],
  $qpid_port              = 5672,
  $qpid_userid            = 'nova',
  $package_ensure         = 'present',
  $api_paste_config       = '/etc/cinder/api-paste.ini',
  $verbose                = 'False',
  $debug                  = 'False',
  $use_syslog             = false,
  $syslog_log_facility    = "LOCAL3",
  $syslog_log_level       = 'WARNING',
  $log_dir                = '/var/log/cinder',
) {

  include cinder::params
  warning('The cinder::base class is deprecated. Use cinder instead.')

  class { 'cinder':
    rabbit_password         => $rabbit_password,
    qpid_password           => $rabbit_password,
    sql_connection          => $sql_connection,
    rpc_backend             => $rpc_backend,
    qpid_rpc_backend        => $qpid_rpc_backend,
    queue_provider          => $queue_provider,
    rabbit_host             => $rabbit_host,
    rabbit_port             => $rabbit_port,
    rabbit_hosts            => $rabbit_hosts,
    rabbit_virtual_host     => $rabbit_virtual_host,
    rabbit_userid           => $rabbit_userid,
    qpid_host               => $qpid_host,
    qpid_hosts              => $qpid_hosts,
    qpid_port               => $qpid_port,
    qpid_userid             => $qpid_userid,
    package_ensure          => $package_ensure,
    api_paste_config        => $api_paste_config,
    verbose                 => $verbose,
    debug                   => $debug,
    use_syslog              => $use_syslog,
    syslog_log_facility     => $syslog_log_facility,
    syslog_log_level        => $syslog_log_level,
    log_dir                 => $log_dir,
  }

}
