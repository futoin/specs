<pre>
FTN3: FutoIn Interface Definition
Version: 1.0
Date: 2014-09-08
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# 1. Basic concept

## 1.1. Peer-to-peer communication

There is Invoker and Executor side. Both can be implemented in scope of single
process, different processes or different machines across network.

Multi-peer communication is assumed to be a higher level concept on top of 
current one.

Object-oriented remote calls is also assumed to be a higher level concept.

It assumed that there is language- and/or software platform-specific
standardized low-level API/ABI for connection establishing and calls coupled
with optional standardized high-level binding/mapping of FutoIn interfaces
to native features.

All specifications and implementations assume to support loose coupling of
each components, suitable for easy separation, replacement and unit testing.

Each call has a request and may have a response messages with key-value pairs described below.
If a call does not expect to return any result then no response message must be
sent and/or expected to be received. It must be possible to override with *forcersp*
flag in request message.
<br>
*Note: it means that call must return at least something to detect on invoker if the
call is properly executed*

For large data transfer efficiency purposes, if message transport allows such extension,
request message can be coupled with raw request data and/or response can be *replaced*
with raw response data. Typical scenario is file upload and/or download through HTTP(S).

Lower-level protocol of message exchange is out of scope of this specification.


Possible examples of Peer-to-peer communication types:

* raw datagram like UNIX Socket, UDP or SCTP
* WebSockets
* HTTP with request in POST and response in body
* HTTP with request in GET path with parameters and response in body
* HTTP with request in POST or GET and non-message payload in body (e.g. BLOB)
* HTTP CRUDL mapped to/from FutoIn interface




## 1.2. Function Call

The major parts: **function identifier**, **parameters**, **result** and
**exception**.

* **function identifier** - unique associative name of string type with interface name,
    version and interface function coded in it
* **parameters** - key-value pairs
    * key - unique associative name of string type
    * value - value of arbitrary JSON type defined in interface
* **result** - key-value pairs, similar to parameters
* **exception** - associative name of the first error occurred during function execution


## 1.3. Client-server/service multiplexing mode

Invoker is responsible to enable request message (and response therefore)
multiplexing by adding special *request ID* field. Executor is responsible
for adding the same field to related response message.

Please note that *Invoker* and *Client*, *Executor* and *Server* are NOT the same terms.
Client is the peer which initiated peer-to-peer communication. Server is the peer 
which accepts peer-to-peer communications. On the other hand, Invoker sends request and
Executor replies to the request.

Client side request ID must be prefixed with "C".
Server side request ID must be prefixed with "S".

The rest of request ID should be integer value starting with 1 and incrementing with
every subsequent request sent. However, it should be allowed to add other prefixes
to this value.

*Note: Request ID must never be used outside of multiplexing context as it by definition
duplicates across different communication channels*


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
                    "description" : "Unique interface identifier, version and function identifier"
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
            "maxProperties" : 3,
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
                    "description" : "Exception/error name. Either r or e must be present"
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

* boolean - true or false
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

Any functional call can result in expected or unexpected errors. This concept
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
    *Must be generated only on Invoker side*.
* **CommError** - communication error at any stage after request is sent
    and before response is received.
    *Must be generated only on Invoker side*.
* **UnknownInterface** - unknown interface requested.
    *Must be generated only on Executor side*.
* **NotImplemented** - in case interface function is not implemented on Executor side
    *Must be generated only on Executor side*.
* **NotSupportedVersion** - not supported interface version
    *Must be generated only on Executor side*.
* **Unauthorized** - security policy on Executor side does not allow to
    access interface or specific function.
    *Must be generated only on Executor side*.
* **InternalError** - unexpected internal error on Executor side, including internal CommErrors.
    *Must be generated only on Executor side*.
* **InvokerError** - unexpected internal error on Invoker side, not related to CommErrors.
    *Must be generated only on Invoker side*.
* **InvalidRequest** - invalid data is passed as FutoIn request.
    *Must be generated only on Executor side*.
* **DefenseRejected** - defense system has triggered rejection
    *Must be generated on Executor side, but also possible to be triggered on Invoker*.
* **PleaseReauth** - Executor requests re-authorization
    *Must be generated only on Executor side*.
* **SecurityError** - 'sec' request section has invalid data or not SecureChannel
    *Must be generated only on Executor side*.
* **Timeout** - Timeout occurred in any stage
    *Must be used only internally*.




# 2. Interface concept

Executor side functions identifiers are grouped into interfaces, which must have
a specifications in FutoIn format. Further, those will be named "*spec*" for singular
or "*specs*" for plural.

All used specs should be available to Invoker and Executor for dynamic retrieval
from special repositories through network. Repository access and format will
be described later in this document.

For optimization and reliability reasons, specs can be bundled and/or
embedded into Invoker and/or Executor application.

Interfaces must be defined in machine-readable form using [JSON][].
There is existing neutral JSON Schema, but it is universal and therefore too
loose for interface definition. Therefore FutoIn defines own JSON
structure for interface definition below.


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
                    "pattern" : "^[0-9]+\\.[0-9]+$",
                    "description" : "Version of the given interface"
                },
                "funcs" : {
                    "type" : "object",
                    "description" : "Member function declaration",
                    "additionalProperties" : false,
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
                                                    "type" : "string",
                                                    "description" : "Parameter description"
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
                                                    "type" : "string",
                                                    "description" : "Result variable description"
                                                }
                                            }
                                        }
                                    },
                                    "description" : "List of allowed result key-value pairs"
                                },
                                "rawupload" : {
                                    "type" : "boolean",
                                    "desc" : "If not set then arbitrary data upload is not allowed."
                                },
                                "rawresult" : {
                                    "type" : "boolean",
                                    "desc" : "If set then no FutoIn response is assumed. Arbitrary raw data is sent instead."
                                },
                                "throws" : {
                                    "type" : "array",
                                    "uniqueItems": true,
                                    "description" : "List of associative error names, which can be triggered by function execution"
                                },
                                "desc" : {
                                    "type" : "string",
                                    "description" : "Interface Function description"
                                }
                            },
                            "description" : "Interface Function declaration"
                        }
                    }
                },
                "desc" : {
                    "type" : "string",
                    "description" : "Description of the interface"
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
            "iface" : "futoin.event.receiver",
            "version" : "0.1",
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

### 2.2.1. Interface identifier

It is assumed that interface identifier (name) is unique and consists of several string tokens
concatenated with dots ("."). Each token is small latin alpha-numeric sequence.

    Example: "futoin.event.receiver", "futoin.event.poll"

The first part of identifier must reference related project domain name or be unique enough
to avoid name clashing (e.g. trademark, reserved prefix, etc.).
    
    Example: "example.com.interface", "example.org.namespace.interface"

**Note: "futoin." interface prefix is reserved for official FutoIn project specs**

### 2.2.2. Function identifier

Function names follow camelCase. Example: "someFunc", anotherFunc"

**Note: "futoin" function prefix is reserved for internal purposes**


### 2.2.3. Parameter/Result identifier

Parameter and result variable names follow small_caps_with_underscore pattern.
Example: "some_param", "some_result_value"



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
* Adding additional result fields to existing result variables
    * Invoker must ignore additional result variables, if function
    is called through parent interface (it should ignore additional result variable in general)
    * Note: it is not allowed to change "rawresult" flag

*Note: multiple interface inheritance is not supported at the moment*

## 2.4. Interface operation requirements

Some interfaces must be restricted to certain conditions. This can be defined on interface level
through "requires" attribute.

Standard requirement type:

* AllowAnonymous - interface can be called without Client Authentication information
* SecureChannel - message exchange must be done through secure channel as it contains
    not encrypted sensitive information. Channel security control is both Client and Service
    implementation responsibility


For safety reasons, inheriting interface must re-define all "requires" items from
inherited interface.

## 2.5. Interface repositories

For all publicly released specs, there must be associated repository. Repository must have
two identical in structure folder trees "**draft**" and "**final**".

Each tree must have:

* **meta/** folder for generated machine-readable data
* **preview/** simple generated HTML versions of specifications
* **misc/{spec_name}/** optional folder for any additional file used for spec creation
* files with "*md*" extension - original specs in Markdown format with custom extensions

Both "**meta**" and "**preview**" folders must have files in the following format:

* **{interface_name}-{major}.{minor}-iface.json** - spec definition file (old versions should remain)
* **{interface_name}-{major}-iface.json** - the latest version for {major}, typically a symlink to above
* **{interface_name}-iface.json** - the latest version, typically a symlink to above
* **{schema_name}-{major}.{minor}-schema.json** - the same as above, but for JSON Schema files
* **{schema_name}-{major}-schema.json** - as above
* **{schema_name}-schema.json** - as above

*Note: {minor} should not include DV prefix*

*Note: as a convention, repository domain name should start from "specs." and be available through HTTP and/or HTTPS*

It is assumed that automatic meta file retrieval first looks in **final/meta/** and then tries **draft/meta/**. So,
application source will not need to be changed during development of new spec and after release of the spec. However,
all draft specs are subject to change without version update. So, all draft specs should be cached with small
Time-To-Live or not cached at all.




[json]: http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf "JSON"
[json-schema]: http://tools.ietf.org/html/draft-fge-json-schema-validation-00 "JSON-SCHEMA"


=END OF SPEC=
