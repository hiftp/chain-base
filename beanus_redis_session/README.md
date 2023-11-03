The Bean Family: Redis Session for Odoo
----

Odoo is a suite of web based open source business apps.

This module allows you to use a Redis database to manage sessions, instead of classic filesystem storage.

Redis is an open source, in-memory data structure store, used as a database, cache and message broker.

It is useful for load balancing because session's directory may not be shared.



Requirements
-------------------------

You need to install and to start a Redis server to use this module. Documentation is available on Redis website.

You need to install package redis:
````
pip3 install redis
````
    

Usage
-------------------------
To use Redis, install this module and please add "enable_redis = True" option and add bean_redis_session as a wide module "server_wide_modules = base,web,bean_redis_session" in configuration file.

Example setting in configuration file

````
[options]

enable_redis    = True
redis_host      = localhost      # Redis IP. default: locahost
redis_port      = 6379           # Redis Port, default: 6379
redis_dbindex   = 1              # Redis database index, default: 1
#redis_pass     =                # Redis password, default: None

server_wide_modules = base,web,beanus_redis_session
````

