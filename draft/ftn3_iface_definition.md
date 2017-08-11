<pre>
FTN3: FutoIn Interface Definition
Version: 1.7
Date: 2017-08-11
Copyright: 2014-2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.7 - 2017-08-11 - Andrey Galkin
    * NEW: added support for result as type instead of result object
* v1.6 - 2017-08-04 - Andrey Galkin
    * FIXED: minor enforcements for interface schema
    * NEW: "enum" and "set" basic type support
    * NEW: type variations
    * NEW: "elemtype" for "map"
* v1.5 - 2017-08-03 - Andrey Galkin
    * NEW: minlen/maxlen instead of only regex for string support
* v1.4.1 - 2017-07-20 - Andrey Galkin
    * FIXED: JSON schema issue with "types" type shortcut
* v1.4 - 2017-07-19 - Andrey Galkin
    * FIXED: interface JSON schema "fields" constraints
    * NEW: clarified imports logic in diamond shaped cases
    * NEW: clarified default "null" behavior
    * NEW: type, field, parameter or result shortcut for type definition
* v1.3 - 2015-03-08 - Andrey Galkin
    * Added "obf" - on behalf field support
    * Added "seclvl" - user authentication security level minimum
* v1.2 - 2015-02-22 - Andrey Galkin
    * Extended 'rid' field regex to support custom prefix part
    * Added "MessageSignature" interface constraint
* v1.1 - 2015-01-08 - Andrey Galkin
    * Added response.edesc optional field
    * Added iface.ftn3rev field
    * Added custom types concept
    * Added import/mixin concept
    * Added "any" type
    * Added clarification of inheritance feature purpose compared to import
    * Added "BiDirectChannel" constraint
    * Added "heavy" function property
    * Officially documented payload size safety limits
* v1.0 - 2014-09-08 - Andrey Galkin

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
                    "pattern" : "^(C|S)[a-zA-Z0-9_\\-]*[0-9]+$",
                    "description" : "Optional request ID for multiplexing"
                },
                "forcersp" : {
                    "type" : "boolean",
                    "description" : "If present and true, force response to be sent, even if no result is expected"
                },
                "sec" : {
                    "type" : "object",
                    "description" : "Security-defined extension"
                },
                "obf" : {
                    "type" : "object",
                    "description" : "On-Behalf-oF user info",
                    "additionalProperties" : false,
                    "properties" : {
                        "lid" : {
                            "type" : "string",
                            "description" : "Local User ID"
                        },
                        "gid" : {
                            "type" : "string",
                            "description" : "Global User ID"
                        },
                        "slvl" : {
                            "type" : "string",
                            "description" : "User authentication security level"
                        }
                    }
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
                    "description" : "Result key-value pairs (pre-1.7) or any type"
                },
                "e" : {
                    "type" : "string",
                    "description" : "Exception/error name. Either r or e must be present"
                },
                "edesc" : {
                    "type" : "string",
                    "description" : "Optional. Error description, if e is present"
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

The standard FutoIn interface types:

* boolean - true or false
* integer - signed integer with 32-bit precision
* number - float value with 32-bit precision
* string - string of unlimited length
* map - key-value pairs (JSON object by fact). No ordering is guaranteed.
    * key - string
    * value - any type defined in this section
* array - ordered list of values
    * value - any type defined in this section
* enum - value from predefined set
    * value - integer or string
* set - list of unique values
    * value - integer or string
* any - field type is not checked
* *CustomType* - any pre-defined custom type defined, inherited or imported
    in the same iface

*Note: **null** can be used only as placeholder in "default" values.*

### 1.8.1. Custom types

Each iface can define own types in the optional "types" fields.

The types are inherited and imported. It is an error to redefine type in such case.

Each custom type must be based on one of the standard types, but can define
various *optional* constraints:

* integer and number:
    * min - minimal allowed value (inclusive).
    * max - maximal allowed value (inclusive).
* string:
    * regex - ECMAScript regular expression.
    * minlen - minimal string length (inclusive).
    * maxlen - maximal string length (inclusive).
* array:
    * minlen - minimal array length (inclusive).
    * maxlen - maximal array length (inclusive).
    * elemtype - required element type.
* map:
    * fields - a map of field_name to:
        * type - required field type
        * optional - optional. boolean. True, if the field can be omitted.
        * desc - optional. string, Description of the field.
    * elemtype - required element type, if no "fields" are provided.
* enum:
    * items - list of allowed integer or string values
* set:
    * items - complete set of allowed integer or string values

*NOTE: omitted optional field of custom map type must be set to null on incoming message (request
for Executor and response for Invoker case). Optional fields should be allowed to be sent as null.*

### 1.8.2. "null" parameter value

As a special case, it's possible to mark any parameter with default value of "null". Besides
providing the default value, it also triggers a special parameter verification logic which skips
any constraint check, if actual value is null.

### 1.8.3. Shortcut for type definition

Parameter, result variable, field in "map" and type can be defined with string.
The string must be a name of a known type.

So,
`
    "param" : "integer"
`
is equivalent to
`
    "param" : {
        "type" : "integer"
    }
`

### 1.8.4. Type variations

Sometimes the same parameter or result may be allowed to have different types.
For example: database query can return both integer and string field data.

For that purpose, specification allows listing several types in array. Such
approach is supported only in shortcut type definition form, e.g.:
`
    "param" : ["integer", "string"]
`

*Since: v1.6*

### 1.8.5. Result type

Very often function calls return only single value. It not efficient and
not clean write something `result.result`. Therefore, it's allowed
to define result as string refering to standard or custom type.

Type variations are not allowed in result.

*Since: v1.7*

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

## 1.10. Payload size safety limits

It is assumed that both request and response messages are relatively small. All heavy data should be
transfered as raw HTTP or other lower level protocol payload. Therefore, a **safety limit
of 64 KBytes is imposed for any type of payload**. Both Invoker and Executor should control
this limit, unless there is efficient mechanism with O(1) complexity to transfer message
from peer to peer (e.g. shared memory).

## 1.11. On Behalf Of calls

It is expected that Executor passes authenticated user information in sub-calls, so
all security checks are done against user, but not Executor itself. It is a 
simple security measure to avoid error-prone access control implementation in sub-calls.
If call is expected to be done on behalf of system then it should be controlled by
System's Invoker iface option.

## 1.12. Minimum user authentication security level

Each function can have *seclvl* defined to control minimum security level of user
authentication. It is not related to access control, but user validation, e.g.
important functionality may require dual factor or public key based authentication.
**PleaseReauth** is to be triggered on security level mismatch with the first word
in description containing required security level.

All unknown security levels are to be treated as maximum level of security.


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
            "required" : [ "iface", "version", "ftn3rev" ],
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
                "ftn3rev" : {
                    "type" : "string",
                    "pattern" : "^[0-9]+\\.[0-9]+$",
                    "description" : "Version of the FTN3 spec, according to which the iface is defined"
                },
                "types" : {
                    "type" : "object",
                    "description" : "iface types. Must start with Capital",
                    "patternProperties" : {
                        "^[A-Z][a-zA-Z0-9]*$" : {
                            "type" : ["object", "string", "array"],
                            "uniqueItems": true,
                            "minItems": 1,
                            "additionalProperties" : false,
                            "properties" : {
                                "type" :  {
                                    "type" : "string",
                                    "pattern" : "^any|boolean|integer|number|string|map|array|enum|set|[A-Z][a-zA-Z0-9]+$"
                                },
                                "min" : {
                                    "type": "number"
                                },
                                "max" : {
                                    "type": "number"
                                },
                                "minlen" : {
                                    "type": "number"
                                },
                                "maxlen" : {
                                    "type": "number"
                                },
                                "regex" : {
                                    "type": "string"
                                },
                                "elemtype" : {
                                    "type": "string"
                                },
                                "fields" : {
                                    "type": "object",
                                    "additionalProperties" : false,
                                    "patternProperties" : {
                                        "^[a-z][a-z0-9_]*$" : {
                                            "type" : ["object", "string", "array"],
                                            "uniqueItems": true,
                                            "additionalProperties" : false,
                                            "properties" : {
                                                "type" :  {
                                                    "type" : "string",
                                                    "pattern" : "^any|boolean|integer|number|string|map|array|[A-Z][a-zA-Z0-9]+$"
                                                },
                                                "optional" : {
                                                    "type" : "boolean",
                                                    "description" : "If true the field is optional. Defaults to null"
                                                },
                                                "desc" : {
                                                    "type" : "string",
                                                    "description" : "Result variable description"
                                                }
                                            }
                                        }
                                    }
                                },
                                "items" : {
                                    "type" : "array",
                                    "uniqueItems": true,
                                    "additionalItems": false,
                                    "items" : {
                                        "type" : ["string", "integer"]
                                    },
                                    "minItems": 1,
                                    "maxItems": 1000
                                },
                                "desc" : {
                                    "type" : "string",
                                    "description" : "Custom type description"
                                }
                            }
                        }
                    },
                    "additionalProperties" : false
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
                                    "type" : "object",
                                    "additionalProperties" : false,
                                    "patternProperties" : {
                                        "^[a-z][a-z0-9_]*$" : {
                                            "type" : ["object", "string", "array"],
                                            "uniqueItems": true,
                                            "additionalProperties" : false,
                                            "properties" : {
                                                "type" :  {
                                                    "type" : "string",
                                                    "pattern" : "^any|boolean|integer|number|string|map|array|[A-Z][a-zA-Z0-9]+$"
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
                                    "type" : ["object", "string"],
                                    "additionalProperties" : false,
                                    "patternProperties" : {
                                        "^[a-z][a-z0-9_]*$" : {
                                            "type" : ["object", "string", "array"],
                                            "uniqueItems": true,
                                            "additionalProperties" : false,
                                            "properties" : {
                                                "type" :  {
                                                    "type" : "string",
                                                    "pattern" : "^any|boolean|integer|number|string|map|array|[A-Z][a-zA-Z0-9]+$"
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
                                "heavy" : {
                                    "type" : "boolean",
                                    "desc" : "Mark request as \"heavy\" in terms processing"
                                },
                                "seclvl" : {
                                    "type" : "string",
                                    "desc" : "Minimum user authentication security level"
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
                "imports" : {
                    "type" : "array",
                    "uniqueItems": true,
                    "description" : "Name:version of interface to be imported as a mixin"
                },
                "requires" : {
                    "type" : "array",
                    "description" : "List of conditions for interface operation",
                    "items" : {
                        "type" : "string",
                        "pattern" : "^AllowAnonymous|SecureChannel|BiDirectChannel|MessageSignature|[a-zA-Z0-9]+$"
                    },
                    "uniqueItems": true,
                    "additionalItems": false
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
                        },
                        "ref" : "string"
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

Unfortunately, due to Executor's interface selection logic. The same base iface must not
be used for inheritance of more than one derived interface within the same Executor instance.
*The primary use of inheritance feature is to create reusable **base implementation logic**
with customized extensions possible through derived interface.*

If only the interface itself, but not the implementation logic needs to be re-used then
mixin/import feature is appropriate solution.


## 2.4. Interface operation requirements

Some interfaces must be restricted to certain conditions. This can be defined on interface level
through "requires" attribute.

Standard requirement type:

* AllowAnonymous - interface can be called without Client Authentication information
* SecureChannel - message exchange must be done through secure channel as it contains
    not encrypted sensitive information. Channel security control is both Client and Service
    implementation responsibility
* BiDirectChannel - communication channel must allow bi-directional message exchange (both
    peers should be able to act as invoker and executor)
* MessageSignature - requires full message signing (e.g. HMAC)


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

## 2.6. Iface definition spec version

Each interface must define "ftn3rev" field in standard MAJOR.MINOR version format.
When the field is missing, FTN3 revision 1.0 is assumed.

Invoker part must allow loading interface definition only if major version is supported,
regardless of minor version.

Executor part must allow loading interface only if specified FTN3 spec revision is fully
supported.

## 2.7. Interface mixin

Interface mixin is appropriate solution when only **interface definition** needs to be re-used,
but the logic behind is absolutely different. Example: CRUDL-like interface.

Mixin interfaces are defined using "imports" field - an array of imported "iface:version"
identifiers.

Import procedure must act exactly as inheritance in scope of processing "types", "funcs"
and "requires" fields. However, imported interface must never be listed as inherited.

If imported interfaces includes own "imports" field it must be treated as if imported
interfaces are listed in the top-most main interface. Interface imports of compatible
interface versions must get merged together. This is a workaround for diamond-shaped cases.

## 2.8. "Heavy" requests

Some request functions can be marked as "heavy". Executor implementation may use this meta-
information to limit number of concurrent "heavy" requests for stability and performance
reasons. Heavy requests may also get a different default timeout value.


[json]: http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf "JSON"
[json-schema]: http://tools.ietf.org/html/draft-fge-json-schema-validation-00 "JSON-SCHEMA"


=END OF SPEC=
