<pre>
FTN8.5: FutoIn Security Concept - Defense System
Version: 0.2DV
Date: 2017-12-27
Copyright: 2014-2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v0.2 - 2017-12-27 - Andrey Galkin
    - CHANGED: heavily revised & split into sub-specs
* v0.1 - 2014-06-03 - Andrey Galkin
    - Initial draft

# WARNING

**INCOMPLETE: just peaces from old FTN8 v0.1**

To be revised

# 1. Intro

This sub-specification of [FTN8](./ftn8_security_concept.md) covers
Defense System specification.

# 2. Concept

To be revised.




# 3. Defense system integration

Security is common responsibility. Every node of the system must be a defense barrier for
both attacks and simple misconfiguration.

Typically, more farther node from actual attacker should have a dynamic failure rate
limit to avoid a closer node being banned, leading to Denial of Service of specific 
functionality.

Each service must detect attacking Clients/Services and deny access before security limit
is triggered on another host.

*Note: all hit or approaching limits must be reported to administration for actions to be 
taken*

**Any error, which never happens by race condition, mistake, etc. must immediately trigger
defense system action** Example: session token validation by other Service.

## 3.1. Possible limit types

* Limit per period from the same client and/or host and/or network
    * Request count
    * Security failures
* Dynamic limits
    * Limit can be risen and lowered dynamically (e.g. AuthService rices limits per Services
    based on number of active users)


    
# 6. Defense Systems

Any open system requires effective reaction to errors generated
by misconfiguration and intentional attacks. It is also required
to impose limits on utilization of resources for normal operation.

There are no requirements on how defense system must behave to
identify possible attacks and misconfiguration, and how to react
to them. It is like a fraud detection system - a full time job type
of thing.

However, this specification defines a universal interface for
system audit and reaction.

## 6.1. Example

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

To be revised.

`Iface{`

        {
            "iface" : "futoin.defense.provider",
            "version" : "{ver}",
            "ftn3rev" : "1.4",
            "funcs" : {
                "onCall" : {
                    "params" : {
                        "client_id" : {
                            "type" : "string",
                            "desc" : "Unique Client ID"
                        },
                        "client_addr" : {
                            "type" : "string",
                            "desc" : "IPv4:addr, IPv6:addr or other-type:addr, optionally followed by :port or :path"
                        },
                        "request" : {
                            "type" : "map",
                            "desc" : "Original request data"
                        }
                    },
                    "result" : {
                        "act" : {
                            "type" : "string",
                            "desc" : "one of: pass, drop, reject, reauth, delay"
                        },
                        "delay" : {
                            "type" : "number",
                            "desc" : "delay response (processing for 'delay') for specific absolute time in microseconds since request was made for _any_ action"
                        },
                        "refid" : {
                            "type" : "string",
                            "desc" : "Reference ID for onResult()"
                        }
                    },
                    "desc" : "Call before processing each client's call"
                },
                "onResult" : {
                    "params" : {
                        "refid" : {
                            "type" : "string",
                            "desc" : "Reference ID for onCall()"
                        },
                        "response" : {
                            "type" : "map",
                            "desc" : "Original response data"
                        }
                    },
                    "desc" : "Call after processing each client's call"
                },
                "onFail" : {
                    "params" : {
                        "refid" : {
                            "type" : "string",
                            "desc" : "Reference ID for onCall()"
                        },
                        "error" : {
                            "type" : "string",
                            "desc" : "Generated error"
                        }
                    },
                    "result" : {
                        "delay" : {
                            "type" : "number",
                            "desc" : "delay response for specific absolute time in microseconds since request was made"
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
