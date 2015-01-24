<pre>
FTN3: FutoIn Interface - Ping-Pong
Version: 1.0DV
Date: 2015-01-24
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.0 - 2015-01-24

# 1. Intro

Nothing to say, just a generic ping interface, which can be used
to check other peer availability.

This interface should be implemented on all peers, which can act
as Executor.

# 2. Interface schema

`Iface{`

        {
            "iface" : "futoin.ping",
            "version" : "1.0",
            "ftn3rev" : "1.1",
            "funcs" : {
                "ping" : {
                    "params" : {
                        "echo" : {
                            "type" : "string",
                            "desc" : "Any string"
                        }
                    },
                    "result" : {
                        "echo" : {
                            "type" : "string",
                            "desc" : "See params"
                        }
                    },
                    "desc" : "Check if peer is accessible"
                }
            },
            "requires" : [
                "AllowAnonymous"
            ],
            "desc" : "Ping-pong interface"
        }

`}Iface`

=END OF SPEC=
