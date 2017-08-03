<pre>
FTN3: FutoIn Interface - Ping-Pong
Version: 1.0
Date: 2017-07-22
Copyright: 2015-2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.0 - 2017-07-22 - Andrey Galkin
    - Split into AllowAnonymous & secure
    - Changed to use integer instead of string for echo
* Intial draft - 2015-01-24 - Andrey Galkin

# 1. Intro

Nothing to say, just a generic ping interface, which can be used
to check other peer availability.

This interface should be implemented on all peers, which can act
as Executor.

# 2. Interface schema

## 2.1. Generic interface

This version requires authentication by default.

`Iface{`

        {
            "iface" : "futoin.ping",
            "version" : "1.0",
            "ftn3rev" : "1.1",
            "funcs" : {
                "ping" : {
                    "params" : {
                        "echo" : {
                            "type" : "integer",
                            "desc" : "Arbitrary integer"
                        }
                    },
                    "result" : {
                        "echo" : {
                            "type" : "integer",
                            "desc" : "See params"
                        }
                    },
                    "desc" : "Check if peer is accessible"
                }
            },
            "desc" : "Ping-pong interface"
        }

`}Iface`

## 2.1. Anoynmous variation of ping interface

`Iface{`

        {
            "iface" : "futoin.anonping",
            "version" : "1.0",
            "ftn3rev" : "1.1",
            "inherit" : "futoin.ping:1.0",
            "requires" : [
                "AllowAnonymous"
            ],
            "desc" : "Ping-pong interface"
        }

`}Iface`


=END OF SPEC=
