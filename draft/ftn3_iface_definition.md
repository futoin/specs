<pre>
FTN3: FutoIn Interface Definition
Version: 0.1
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# 1. Basic concept

## 1.1. Peer-to-peer communication

There is invoker and executor side. Both can be implemented in scope of single
process, different processes or different machines across network.

Multi-peer communication is assumed to be a higher level concept on top of 
current one.

Object-oriented remote calls is also assumed to be a higher level concept.

It assumed that there language- and/or software platform-specific
standardized low-level API for connection establishing and calls coupled
with optional standardized high-level binding/mapping of FutoIn interfaces
to native features.

All specifications and implementations assume to support loose coupling of
each components, suitable for easy separation, replacement and unit testing.

Each call has request and response messages with key-value pairs described below.
If a call does not expect to return any result then no response message must be
sent and/or expected to be received. It should be possible to override with *forcersp*
flag.
<br>
*Note: it means that call must return at least something to detect on invoker if the
call is properly executed*

Low-level protocol for message exchange is out of scope of this specification.


Possible examples of Peer-to-peer communication types:

* raw datagram like UNIX Socket, UDP or SCTP
* WebSockets
* HTTP with request in POST and response in body
* HTTP with request in GET path and parameters and response in
* HTTP with request in POST or GET and non-response payload in body (e.g. BLOB)
* HTTP CRUDL mapped to/from FutoIn interface




## 1.2. Function Call

There are three major parts: **function identifier**, **parameters**, **result** and
**exception**.

* **function identifier** - unique associative name of string type
* **parameters** - key-value pairs
    * key - unique associative name of string type
    * value - value of arbitrary type
* **result** - key-value pairs, similar to parameters
* **exception** - associative name of first error occurred during function execution


## 1.3. Client-server/service multiplexing mode

Invoker is responsible to enable request message (and response therefore)
multiplexing by adding special *request ID* field. Executor is responsible
for adding the same field to related response message.

Please note that Invoker and Client, Executor and Server side are NOT the same terms.
Client is the peer which initiated peer-to-peer communication. Server is the peer 
which accepts peer-to-peer communications.

Client side request ID must be prefixed with "C".
Server side request ID must be prefixed with "S".

The rest of request ID should be integer value starting with 1 and incrementing with
every subsequent request sent. However, it should be allowed to add other prefixes
to this value.


## 1.4. Uni-directional call pattern

Invoker/Executor side is semantically defined and does not rely on Client/Server
status of peer. There is no protocol-level support for that. Each side controls if
it can act as Executor.

It is suggested that Client side is always Invoker in uni-directional pattern.

Both serial and multiplexing modes are allowed.


## 1.5. Bi-directional call pattern

Each side is both Invoker and Executor. Bi-directional pattern must always work
in message multiplexing mode.


## 1.6. Request schema

Using [JSON-SCHEMA][]:

`Schema(futoin-request){`

        {
            "title" : "FutoIn request schema",
            "type" : "object",
            "required" : [ "f", "p" ],
            "additionalProperties" : false,
            "properties" : {
                "f" : {
                    "type" : "string",
                    "pattern" : "^([a-z][a-z0-9]*)(\\.[a-z][a-z0-9]*)*:[0-9]+\\.[0-9]+:[a-z][a-zA-Z0-9]*$",
                    "description" : "Unique interface identifier and version"
                },
                "p" : {
                    "type" : "object",
                    "additionalProperties" : false,
                    "patternProperties" : {
                        "^[a-z][a-z0-9_]*$" : {}
                    },
                    "description" : "Parameters key-value pairs"
                },
                "rid" : {
                    "type" : "string",
                    "pattern" : "^(C|S)[0-9]+$",
                    "description" : "Optional request ID for multiplexing"
                },
                "forcersp" : {
                    "type" : "boolean",
                    "description" : "If present and true, force response to be sent, even if no result is expected"
                },
                "sec" : {
                    "type" : "object",
                    "description" : "Security-defined extension"
                }
            }
        }

`}Schema`


*Example:*

        {
            "f" : "futoin.event:1.0:reliableEvent",
            "p" : {
                "event" : "SomeEvent"
            }
        }


## 1.7. Response schema

Using [JSON-SCHEMA][]:

`Schema(futoin-response){`

        {
            "title" : "FutoIn response schema",
            "type" : "object",
            "additionalProperties" : false,
            "minProperties" : 1,
            "maxProperties" : 2,
            "properties" : {
                "r" : {
                    "type" : "object",
                    "additionalProperties" : false,
                    "patternProperties" : {
                        "^[a-z][a-z0-9_]*$" : {}
                    },
                    "description" : "Result key-value pairs"
                },
                "e" : {
                    "type" : "string",
                    "description" : "Exception/error name"
                },
                "rid" : {
                    "type" : "string",
                    "pattern" : "^(C|S)[0-9]+$",
                    "description" : "Optional request ID for multiplexing"
                },
                "sec" : {
                    "type" : "object",
                    "description" : "Security-defined extension"
                }
            }
        }

`}Schema`

*Example:*

        {
            "r" : {
                "delivered" : true
            }
        }
          or 
        {
            "e" : "NotImplemented"
        }




## 1.8. Parameter and result types

* boolean - true of false
* integer - signed integer with 32-bit precision
* number - float value with 32-bit precision
* string - string of unlimited length
* map - key-value pairs (JSON object by fact). No ordering is guaranteed.
    * key - string
    * value - any type defined in this section
* array - ordered list of values
    * value - any type defined in this section

*Note: **null** can be used only as placeholder in "default" values.*


## 1.9. Errors and exceptions

Any functional call can result in expected and unexpected errors. This concept
is similar to checked/unchecked exceptions in Java language.

All expected exceptions/errors, which appear in standard flow must be enumerated
in "throws" clause of function declaration in interface definitions (see below).

Unexpected exceptions/errors are generated by execution environment/condition as
reaction to error condition not related to logic implemented in given function. 
Example: internal communication errors, hit of resource limits, crashes, etc.

If possible, language/platform-specific bindings should enforce Invoker to check
for all excepted errors.

### 1.9.1. Predefined unexpected errors

* **ConnectError** - connection error before request is sent.
    *Must be generated on Invoker side*.
* **CommError** - communication error at any stage after request is sent
    and before response is received. *Must be generated on Invoker side*.
* **NotImplemented** - in case interface function is not implemented on Executor side
    *Must be generated on Executor side*.
* **Unauthorized** - security policy on Executor side does not allow to
    access interface or specific function.
    *Must be generated on Executor side*.
* **InternalError** - unexpected internal error on Executor side, including internal CommErrors.
    *Must be generated on Executor side*.
* **InvokerError** - unexpected internal error on Invoker side, not realted to CommErrors.
    *Must be generated on Invoker side*.
* **UnknownInterface** - unknown interface requested.
    *Must be generated on Executor side*.
* **NotSupportedVersion** - not supported interface version
    *Must be generated on Executor side*.
* **InvalidRequest** - invalid data is passed as FutoIn request.
    *Must be generated on Executor side*.
* **DefenseRejected** - defense system has triggered rejection
    *Must be generated on Executor side*.
* **PleaseReauth** - Executor requests re-authorization
    *Must be generated on Executor side*.
* **SecurityError** - 'sec' request section has invalid data or not SecureChannel
    *Must be generated on Executor side*.



# 2. Interface concept

Executor side functions identifiers are grouped into interfaces, which must be
standardized as one of FutoIn specifications.

Interfaces must be defined in machine-readable form using
[JSON][].
There is existing neutral JSON Schema, but it is universal and therefore too
loose for interface definition.


## 2.1. Interface definition schema

Using [JSON-SCHEMA][]:

`Schema(futoin-interface){`

        {
            "title" : "FutoIn interface definition schema",
            "type" : "object",
            "required" : [ "iface", "version" ],
            "additionalProperties" : false,
            "properties" : {
                "iface" : {
                    "type" : "string",
                    "pattern" : "^([a-z][a-z0-9]*)(\\.[a-z][a-z0-9]*)+$",
                    "description" : "Unique interface identifier"
                },
                "version" : {
                    "type" : "string",
                    "pattern" : "^[0-9]+\\.(DV)?[0-9]+$",
                    "description" : "Version of given interface"
                },
                "funcs" : {
                    "type" : "object",
                    "description" : "Version of given interface",
                    "additionalProperties" : false,
                    "properties" : {
                        "desc" : {
                            "type" : "string"
                        }
                    },
                    "patternProperties" : {
                        "^[a-z][a-zA-Z0-9]*$" : {
                            "type" : "object",
                            "additionalProperties" : false,
                            "properties" : {
                                "params" : {
                                    "additionalProperties" : false,
                                    "patternProperties" : {
                                        "^[a-z][a-z0-9_]*$" : {
                                            "type" : "object",
                                            "properties" : {
                                                "type" :  {
                                                    "type" : "string",
                                                    "pattern" : "^boolean|integer|number|string|map|array$"
                                                },
                                                "default" : {
                                                    "type" : [ "boolean", "integer", "number", "string", "object", "array", "null" ]
                                                },
                                                "desc" : {
                                                    "type" : "string"
                                                }
                                            }
                                        }
                                    },
                                    "description" : "List of allowed parameter key-value pairs"
                                },
                                "result" : {
                                    "additionalProperties" : false,
                                    "patternProperties" : {
                                        "^[a-z][a-z0-9_]*$" : {
                                            "type" : "object",
                                            "properties" : {
                                                "type" :  {
                                                    "type" : "string",
                                                    "pattern" : "^boolean|integer|number|string|map|array$"
                                                },
                                                "desc" : {
                                                    "type" : "string"
                                                }
                                            }
                                        }
                                    },
                                    "description" : "List of allowed result key-value pairs"
                                },
                                "throws" : {
                                    "type" : "array",
                                    "uniqueItems": true,
                                    "description" : "List of associative error names, which can be triggered by function execution"
                                }
                            },
                            "description" : "Interface Function definition"
                        }
                    }
                },
                "desc" : {
                    "type" : "string"
                },
                "inherit" : {
                    "type" : "string",
                    "description" : "Name:version of interface to be inherited"
                },
                "requires" : {
                    "type" : "array",
                    "description" : "List of conditions for interface operation",
                    "items" : {
                        "type" : "string",
                        "pattern" : "^AllowAnonymous|SecureChannel|[a-zA-Z0-9]+$"
                    },
                    "uniqueItems": true
                }
            }
        }
        
`}Schema`


*Example:*

        {
            "iface" : "futoin.event.received",
            "version" : "0.DV",
            "funcs" : {
                "onEvent" : {
                    "params" : {
                        "event" : {
                            "type" : "string",
                            "desc" : "Event name"
                        },
                        "data" : {
                            "default" : null,
                            "desc" : "Arbitrary event data"
                        }
                    },
                    "desc" : "Asynchronously send event"
                },
                "reliableEvent" : {
                    "params" : {
                        "event" : {
                            "type" : "string",
                            "desc" : "Event name"
                        },
                        "data" : {
                            "default" : null,
                            "desc" : "Arbitrary event data"
                        }
                    },
                    "result" : {
                        "delivered" : {
                            "type" : "boolean",
                            "desc" : "Must be true, if completed normally"
                        }
                    },
                    "desc" : "Synchronously send event"
                }
            }
        }


## 2.2. Naming convention

It is assumed that interface identifier (name) is unique and consists of several string tokens
concatenated with dots ("."). Each token is small latin alpha-numeric sequence.
Example: "futoin.event.receiver", "futoin.event.poll"

Function names follow camelCase. Example: "someFunc", anotherFunc"

Parameter and result value names follow small_caps_with_underscore pattern.
Example: "some_param", "some_result_value"

*Note: "futoin" function prefix is reserved for internal purposes*

## 2.3. Interface inheritance

In many cases, domain-specific interfaces have a large universal subset and only a few
domain-specific additional functions and/or function parameters.

Interface can inherit another interface. It should be possible to call any interface
through its parent or any grandparent.

Inheritance is limited to:

* Adding additional functions
* Adding additional parameters to existing function parameters
    * Executor must accept null/absent values for additional parameters
    * All additional parameters must have default value
* Adding additional result fields to existing result values
    * Invoker must ignore additional result values, if function is called through parent interface

*Note: multiple interface inheritance is not supported at the moment*

## 2.4. Interface operation requirements

Some interfaces must be restricted to certain conditions. This can be defined on interface level
through "requires" attribute.

Standard requirement type:

* AllowAnonymous - interface can be called Client Authentication information
* SecureChannel - message exchange must be done through secure channel as it contains
    not encrypted sensitive information. Channel security control is Service
    implementation responsibility


For safety reasons, inheriting interface must re-define all "requires" items from
inherited interface.
    


[json]: http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf "JSON"
[json-schema]: http://tools.ietf.org/html/draft-fge-json-schema-validation-00 "JSON-SCHEMA"


