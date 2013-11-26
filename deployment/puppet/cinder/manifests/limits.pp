# == Class: cinder::limits
#
# Setup and configure the cinder API limits
#
# === Parameters
#
# [*ratelimits*]
#   (optional) The state of the service
#   Defaults to undef. If undefined the default ratelimiting values are used.
#
# [*ratelimits_factory*]
#   (optional) Factory to use for ratelimiting
#   Defaults to 'cinder.api.v1.limits:RateLimitingMiddleware.factory'
#
class cinder::limits (
  $limits = {
    'POST' => '10',
    'POST_SERVERS' => '50',
    'PUT' => '10',
    'GET' => '3',
    'DELETE' => '100',
  },
  $factory = 'cinder.api.v1.limits:RateLimitingMiddleware.factory')

{
  $post_limit=$limits[POST]
  $put_limit=$limits[PUT]
  $get_limit=$limits[GET]
  $delete_limit=$limits[DELETE]
  $post_servers_limit=$limits[POST_SERVERS]


  cinder_api_paste_ini {
    'filter:ratelimit/limits': value => "(POST, \"*\", .*, $post_limit, MINUTE);(POST, \"*/servers\", ^/servers, $post_servers_limit, DAY);(PUT, \"*\", .*, $put_limit, MINUTE);(GET, \"*changes-since*\", .*changes-since.*, $get_limit, MINUTE);(DELETE, \"*\", .*, $delete_limit, MINUTE)";
    'filter:ratelimit/paste.filter_factory': value => $factory;
  }

}

