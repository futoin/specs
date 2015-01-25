<pre>
FTN14: FutoIn Cache
Version: 1.0
Date: 2015-01-22
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.0 - 2015-01-22


# 1. Concept

This spec is trying to be as simple as possible to
meet very basic needs of caching.

It it expected that Service implementation handles cache hammering
mitigation (e.g. by "expiring" ttl for some get requests 10% earlier).

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
                    "result" : {
                        "value" : {
                            "type" : "any",
                            "desc" : "Any previously cached value"
                        }
                    },
                    "throws" : [
                        "CacheMiss"
                    ],
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
    * void getOrSet( as, key_prefix, callable, params, ttl )
        * *key_prefix* - unique key prefix
        * *callable( as, params.. )* - a callable which is called to generated value on cache miss
        * *params* - parameters to be passed to *callable*
        * *tt* - time to live to use, if value is set on cache miss
        * NOTE: the actual cache key is formed with concatenation of *key_prefix* and join
            of *params* values
        * NOTE: cache hammering mitigation logic should be implemented on Service side
            to achieve single execution of callable per cache miss

=END OF SPEC=
