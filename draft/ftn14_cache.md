<pre>
FTN13: FutoIn Cache
Version: 1.0DV
Date: 2015-01-14
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

* v1.0 - 2015-01-14

# 1. Concept

This spec is trying to be as simple as possible to
meet very basic needs of caching.

# 2. Interface schema

`Iface{`

        {
            "iface" : "futoin.cache",
            "version" : "1.0",
            "ftn3rev" : "1.1",
            "funcs" : {
                "get" : {
                    "params" : {
                        "key" : {
                            "type" : "string",
                            "desc" : "Unique cache key"
                        }
                    },
                    "desc" : "Trivial cached value retrieval"
                },
                "set" : {
                    "params" : {
                        "key" : {
                            "type" : "string",
                            "desc" : "Unique cache key"
                        },
                        "value" : {
                            "type" : "any",
                            "desc" : "arbitrary value to cache"
                        },
                        "ttl" : {
                            "type" : "integer",
                            "desc" : "Time to live in milliseconds"
                        }
                    },
                    "desc" : "Trivial cached value storing"
                },
                "custom" : {
                    "params" : {
                        "cmd" : {
                            "type" : "string",
                            "desc" : "Implementation-defined custom command"
                        },
                        "prm" : {
                            "type" : "any",
                            "desc" : "Implementation-defined custom command parameters"
                        }
                    }
                }
            },
            "requires" : [
                "SecureChannel"
            ],
            "desc" : "Audit Log interface"
        }

`}Iface`

# 3. Native interface

* Extend "futoin.cache"
* Functions:
    * void getOrSet( as, key_prefix, params, callable, ttl )
        * *key_prefix* - unique key prefix
        * *params* - parameters to be passed to *callable*
        * *callable( params.. )* - a callable which is called to generated value on cache miss
        * *tt* - time to live to use, if value is set on cache miss
        * NOTE: the actual cache key is formed with concatenation of *key_prefix* and join
            of *params* values
        * NOTE: implementation should mitigate cache hammering to achieve single execution
            of callable per cache miss

=END OF SPEC=
