<pre>
FTN9: FutoIn burst call extension
Version: 0.1
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# 1. Intro
In some cases, its more effective to combine several calls into
a large one.

Possible use cases:

* In lack of WebSocket support, single HTTP request - multiple FutoIn calls
* A set of events or log messages can be uploaded after original request
    has compelted execution
* A state modifying request can be combined with information retrieval
    minimizing processing delay, by removed intermediate response-request part

It should be possible to enable burst explicitly through API or
implicitly by Invoker implementation (e.g. for web pages).

Both Invoker and Executor must disable "AllowAnonymous", if any of invoking
interfaces lacks one. "SecureChannel" must be enabled, if any of invoking
interfaces has one set.

Note: message multiplexing must be enabled to match request and response messages

# 2. Interface schema

`Iface{`

        {
            "iface" : "futoin.burst",
            "version" : "{ver}",
            "ftn3rev" : "1.4",
            "funcs" : {
                "noResultBurst" : {
                    "params" : {
                        "requests" : {
                            "type" : "array",
                            "desc" : "List of regular FutoIn request messages"
                        }
                    },
                    "desc" : "Perform multi-call with no result for all calls"
                },
                "resultBurst" : {
                    "params" : {
                        "requests" : {
                            "type" : "array",
                            "desc" : "List of regular FutoIn request messages"
                        }
                    },
                    "result" : {
                        "responses" : {
                            "type" : "array",
                            "desc" : "List of regular FutoIn response messages"
                        }
                    },
                    "desc" : "Perform multi-call with result at least for some calls"
                }
            },
            "requires" : [
                "AllowAnonymous"
            ],
            "desc" : "Burst call interface"
        }

`}Iface`

# 3. Burst call API extension

All messages between start() and finish() should be delayed. If there is more than one
request to the same end-point, then they should be wrapped into futoin.burst.resultBurst
or futoin.burst.noResultBurst, depending on interface definition.

Simple CCM can implement dummy start() and finish() without affecting regular flow.
**Therefore, invoking code must not rely on side effects of batch processing.**

Burst can be used globally on CCM or on individual interfaces.

* start()
* finish()

=END OF SPEC=
