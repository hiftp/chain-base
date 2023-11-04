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

ODOO_SESSION_REDIS = True
ODOO_SESSION_REDIS_HOST      = localhost      # Redis IP. default: locahost
ODOO_SESSION_REDIS_PORT      = 6379           # Redis Port, default: 6379
ODOO_SESSION_REDIS_DBINDEX   = 1              # Redis database index, default: 1
#ODOO_SESSION_REDIS_PASSWORD     =                # Redis password, default: None
server_wide_modules = base,web,beanus_redis_session
ODOO_SESSION_REDIS_PREFIX = t000
#ODOO_SESSION_REDIS_URL =
#ODOO_SESSION_REDIS_EXPIRATION =
#ODOO_SESSION_REDIS_EXPIRATION_ANONYMOUS =
#ODOO_SESSION_REDIS_SENTINEL_HOST = 
#ODOO_SESSION_REDIS_SENTINEL_MASTER_NAME =
````

