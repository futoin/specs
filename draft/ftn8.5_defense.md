<pre>
FTN8.5: FutoIn Security Concept - Defense System
Version: 0.3DV
Date: 2017-12-27
Copyright: 2014-2018 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v0.2 - 2017-12-27 - Andrey Galkin
    - CHANGED: heavily revised & split into sub-specs
* v0.1 - 2014-06-03 - Andrey Galkin
    - Initial draft

# 1. Intro

This sub-specification of [FTN8](./ftn8_security_concept.md) covers
Defense System specification.

# 2. Concept

## 2.1. Defense Systems

Any open system requires effective reaction to errors generated
by misconfiguration and intentional attacks. It is also required
to impose limits on utilization of resources for normal operation.

There are no requirements on how defense system must behave to
identify possible attacks and misconfiguration, and how to react
to them. It is like a fraud detection system - a full time job type
of thing.

However, this specification defines a universal interface for
system audit and reaction.

## 2.2. Holistic pictures of defense integration

* Successful call (common):

        Client                     Service                      DefenseService
           |                          |                              |
           |-------- request -------> |                              |
           |                          |----------- onCall() -------> |
           |                          | <----- defense action -------|
           |                  [defense action]                       |
           |                      [process]                          |
           |                          |----------- onResult() -----> |
           | <------ response --------|                              |
           |                          |                              |

* Failed call (common):

        Client                     Service                      DefenseService
           |                          |                              |
           |-------- request -------> |                              |
           |                          |----------- onCall() -------> |
           |                          | <----- defense action -------|
           |                  [defense action]                       |
           |                      [process]                          |
           |                          |----------- onFail() -------> |
           |                          | <----- defense action -------|
           |                  [defense action]                       |
           | <------ response --------|                              |
           |                          |                              |

* Defense with drop:

        Client                     Service                      DefenseService
           |                          |                              |
           |-------- request -------> |                              |
           |                          |----------- onCall() -------> |
           |                          | <----- defense action -------|
           |                       [drop]                            |
           |                          |                              |

* Defense with reject / reauth:

        Client                     Service                      DefenseService
           |                          |                              |
           |-------- request -------> |                              |
           |                          |----------- onCall() -------> |
           |                          | <----- defense action -------|
           |                  [defense action]                       |
           | <-- response failure ----|                              |
           |                          |                              |

* Defense with request delay:

        Client                     Service                      DefenseService
           |                          |                              |
           |-------- request -------> |                              |
           |                          |----------- onCall() -------> |
           |                          | <----- defense action -------|
           |                       [delay]                           |
           |                      [process]                          |
           |                          |----------- onResult() -----> |
           | <------ response --------|                              |
           |                          |                              |

* Defense with response delay:

        Client                     Service                      DefenseService
           |                          |                              |
           |-------- request -------> |                              |
           |                          |----------- onCall() -------> |
           |                          | <----- defense action -------|
           |                  [defense action]                       |
           |                      [process]                          |
           |                          |----------- onFail() -------> |
           |                          | <----- defense action -------|
           |                       [delay]                           |
           | <------ response --------|                              |
           |                          |                              |



# 3. Interface

`Iface{`

    {
        "iface" : "futoin.defense",
        "version" : "{ver}",
        "ftn3rev" : "1.8",
        "imports" : [
            "futoin.ping:1.0",
            "futoin.auth.types:{ver}"
        ],
        "funcs" : {
            "onCall" : {
                "params" : {
                    "user" : "AuthInfo",
                    "client" : "ClientFingerprints",
                    "request" : "FTNRequest"
                },
                "result" : {
                    "refid" : "UUIDB64"
                },
                "desc" : "Call before processing each client's call"
            },
            "onResult" : {
                "params" : {
                    "refid" : "UUIDB64",
                    "response" : "FTNResponse"
                },
                "desc" : "Call after processing each client's call"
            },
            "onFail" : {
                "params" : {
                    "refid" : "UUIDB64",
                    "error" : {
                        "type" : "string",
                        "desc" : "Generated error"
                    },
                    "error_info" : {
                        "type" : "string",
                        "desc" : "Generated error info"
                    }
                },
                "desc" : "Call before processing each client's call"
            }
        },
        "requires" : [
            "SecureChannel"
        ],
        "desc" : "AuthService Backend Provider interface"
    }

`}Iface`

=END OF SPEC=
