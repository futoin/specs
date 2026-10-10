<pre>
FTN3: FutoIn Interface Definition
Version: 1.10DV
Date: 2026-10-04
Copyright: 2014-2026 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.10 - 2026-10-04 - Andrey Galkin
    * CHANGED: use Java package naming convention as guideline.
    * CHANGED: AI-aided proofreading changes.
    * NEW: extended "obf" field use cases and predefined field names.
    * NEW: type variations support in detailed "fields", "elemtype", "params",
      and "results" definitions.
* v1.9.2 - 2019-05-27 - Andrey Galkin
    * FIXED: minor typo/spelling fixes
* v1.9.1 - 2018-04-17 - Andrey Galkin
    * FIXED: minor typo/spelling fixes
    * NEW: cosmetic improvements
* v1.9 - 2018-01-14 - Andrey Galkin
    * NEW: fundamental "data" type
    * NEW: multiple transport format support
    * NEW: "BinaryData" interface constraint
* v1.8 - 2017-12-05 - Andrey Galkin
    * NEW: "maxreqsize" & "maxrspsize" function definition attribute
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

There are Invoker and Executor sides. Both can be implemented within the scope
of a single process, across different processes, or across different machines
over a network.

Multi-peer communication is assumed to be a higher-level concept built on top of
the current one.

Object-oriented remote calls are also assumed to be a higher-level concept.

It is assumed that there is a language- and/or platform-specific standardized
low-level API/ABI for establishing connections and making calls, coupled with an
optional standardized high-level binding/mapping of FutoIn interfaces to native
language features.

All specifications and implementations are assumed to support loose coupling of 
each component, making them suitable for easy separation, replacement, and unit 
testing.

Each call has a request message and may have a response message containing the
key-value pairs described below. If a call does not expect to return any result,
no response message must be sent or expected. It must be possible to override
this behavior using the *forcersp* flag in the request message.
<br>
*Note: This means a call must return at least something to allow the Invoker to
detect whether the call was executed properly.*

For large data transfer efficiency, if the message transport allows such
extensions, a request message can be coupled with raw request data and/or a
response can be *replaced* with raw response data. A typical scenario is a file
upload and/or download via HTTP(S).

The lower-level message exchange protocol is out of the scope of this
specification.

Possible examples of Peer-to-peer communication types:

* Raw datagrams (e.g., UNIX Domain Sockets, UDP, or SCTP)
* WebSockets
* HTTP with the request in POST and response in the body
* HTTP with the request in the GET path with parameters and response in the body
* HTTP with the request in POST or GET and a non-message payload in the body
  (e.g. BLOB)
* HTTP CRUDL mapped to/from a FutoIn interface


## 1.2. Function Call

The major components are: **function identifier**, **parameters**, **result**,
and **exception**.

* **function identifier** - A unique associative string containing the interface
name, version, and interface function encoded within it.
* **parameters** - Key-value pairs:
    * key - Unique associative string name.
    * value - Value of an arbitrary JSON type defined in the interface.
* **result** - Key-value pairs, structured similarly to parameters.
* **exception** - Associative name of the first error that occurred during
  function execution.


## 1.3. Client-server/service multiplexing mode

The Invoker is responsible for enabling request message (and consequently
response message) multiplexing by adding a special *request ID* field. The
Executor is responsible for echoing the exact same field back in the related
response message.

Please note that *Invoker* and *Client*, as well as *Executor* and *Server*, are
NOT synonymous terms. The Client is the peer that initiated the peer-to-peer
communication channel. The Server is the peer that accepts peer-to-peer
communications. On the other hand, an Invoker sends a request and an Executor
replies to it.

Client-side request IDs must be prefixed with "C".
Server-side request IDs must be prefixed with "S".

The rest of the request ID should be an integer value starting at 1 and
incrementing with every subsequent request sent. However, implementations should
allow adding other custom prefixes to this value.

*Note: A Request ID must never be used outside of a multiplexing context, as it
is, by definition, duplicated across different communication channels.*


## 1.4. Uni-directional call pattern

The Invoker/Executor side is semantically defined and does not rely on the
Client/Server status of the peer. There is no protocol-level support for
enforcing this relationship; each side controls whether it can act as an
Executor.

It is recommended that the Client side always acts as the Invoker in a
uni-directional pattern.

Both serial and multiplexing modes are permitted.


## 1.5. Bi-directional call pattern

Each side acts as both Invoker and Executor. The bi-directional pattern must
always operate in message multiplexing mode.


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
                    "additionalProperties" : true,
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
                        },
                        "token" : {
                            "type" : "string",
                            "description" : "Original user token"
                        },
                        "trace_id" : {
                            "type" : "string",
                            "description" : "Associated tracing ID"
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

Standard FutoIn interface types:

* `boolean` - `true` or `false`
* `integer` - Signed integer with 32-bit precision
* `number` - Floating-point value with 32-bit precision
* `string` - String of unlimited length
* `map` - Key-value pairs (effectively a JSON object). No ordering is guaranteed.
    * `key` - String
    * `value` - Any type defined in this section
* `array` - Ordered list of values
    * `value` - Any type defined in this section
* `enum` - Value from a predefined set
    * `value` - Integer or string
* `set` - List of unique values
    * `value` - Integer or string
* `data` - Binary data
    * `value` - Sequence of bytes
* `any` - Field type is not validated
* *CustomType* - Any custom type defined, inherited, or imported within the same
    interface

*Note: **null** can be used only as a placeholder in "default" values.*

### 1.8.1. Custom types

Each interface can define its own types in the optional "types" field.

Custom types are inherited and imported. Re-defining an existing type in such
cases constitutes an error.

Each custom type must be based on one of the standard types, but can define
various *optional* constraints:

* `integer` and `number`:
    * `min` - Minimum allowed value (inclusive).
    * `max` - Maximum allowed value (inclusive).
* `string`:
    * `regex` - ECMAScript regular expression.
    * `minlen` - Minimum string length (inclusive).
    * `maxlen` - Maximum string length (inclusive).
* `array`:
    * `minlen` - Minimum array length (inclusive).
    * `maxlen` - Maximum array length (inclusive).
    * `elemtype` - Required element type.
* `map`:
    * `fields` - A map of field names to:
        * `type` - Required field type
        * `optional` - Optional boolean. `true` if the field can be omitted.
        * `desc` - Optional string description of the field.
    * `elemtype` - Required element type, if no "fields" map is provided.
* `enum`:
    * `items` - List of allowed integer or string values.
* `set`:
    * `items` - Complete set of allowed integer or string values.
* `data`:
    * `minlen` - Minimum byte length (inclusive).
    * `maxlen` - Maximum byte length (inclusive).

*NOTE: An omitted optional field of a custom map type must be set to `null` on
incoming messages (requests for the Executor and responses for the Invoker).
Optional fields must also be permitted to be sent explicitly as `null`.*

### 1.8.2. "null" parameter value

As a special case, any parameter can be marked with a default value of `"null"`.
Beyond providing a default value, this triggers special parameter verification
logic that bypasses constraint validation if the actual provided value is
`null`.

### 1.8.3. Shortcut for type definition

Parameters, result variables, fields in a `map`, and types can be defined using
a simple string representing a known type name.

For example:
`
    "param" : "integer"
`
is equivalent to:
`
    "param" : {
        "type" : "integer"
    }
`

### 1.8.4. Type variations

Occasionally, a single parameter or result field may accept multiple distinct
types. For example, a database query might return either integer or string field
data.

To support this, the specification permits listing multiple types in an array.
This approach is supported exclusively in shortcut type definition form, e.g.:
`
    "param" : ["integer", "string"]
`

*Since: v1.6*

### 1.8.5. Result type

Functions frequently return a single scalar value. Wrapping single-value results
in an object leads to redundant access paths like `result.result`. Therefore,
results may be defined as a string referring directly to a standard or custom
type.

Type variations are not allowed in result type definitions.

*Since: v1.7*

### 1.8.6. Binary "data" type

Although the original intent was to exclude raw binary data in favor of explicit
encodings, supporting the "microservice as library" concept requires native
handling of binary data. FutoIn supports raw binary data for efficient
in-process calls and binary-friendly codecs.

If an interface uses binary data, it should include the "BinaryData"
requirement. An alternative interface or function can be provided to support
text-only protocols.

*Since: v1.9*

## 1.9. Errors and exceptions

Any function call can produce expected or unexpected errors. This concept is
analogous to checked and unchecked exceptions in Java.

All expected exceptions/errors that occur during standard execution flow must be
enumerated in the `throws` clause of the function declaration inside interface
definitions (see below).

Unexpected exceptions/errors are generated by the execution environment/runtime
in response to error conditions unrelated to the logic of the specific function
(e.g., internal communication failures, resource limit breaches, crashes, etc.).

Where possible, language/platform-specific bindings should enforce that the
Invoker explicitly checks for all declared expected errors.

### 1.9.1. Predefined unexpected errors

* **ConnectError** - Connection error occurring before the request is sent.
    *Must be generated only on the Invoker side*.
* **CommError** - Communication error occurring at any stage after the request
    is sent and before a response is received.
    *Must be generated only on the Invoker side*.
* **UnknownInterface** - The requested interface is unknown.
    *Must be generated only on the Executor side*.
* **NotImplemented** - The interface function is not implemented on the Executor
    side.
    *Must be generated only on the Executor side*.
* **NotSupportedVersion** - The requested interface version is not supported.
    *Must be generated only on the Executor side*.
* **Unauthorized** - The Executor's security policy prohibits access to the
    interface or specific function.
    *Must be generated only on the Executor side*.
* **InternalError** - Unexpected internal error on the Executor side, including
    internal CommErrors.
    *Must be generated only on the Executor side*.
* **InvokerError** - Unexpected internal error on the Invoker side unrelated to
    CommErrors.
    *Must be generated only on the Invoker side*.
* **InvalidRequest** - Invalid payload passed as a FutoIn request.
    *Must be generated only on the Executor side*.
* **DefenseRejected** - Security defense systems triggered a rejection.
    *Must be generated on the Executor side, but may also be raised on the
    Invoker side*.
* **PleaseReauth** - Executor demands user re-authentication.
    *Must be generated only on the Executor side*.
* **SecurityError** - The `sec` request section contains invalid data or
    requires a SecureChannel.
    *Must be generated only on the Executor side*.
* **Timeout** - Timeout occurred during any execution stage.
    *Must be used only internally*.

## 1.10. Payload size safety limits

Both request and response messages are assumed to be relatively small. Heavy
data should be transferred as raw payload via HTTP or other lower-level
protocols. Therefore, a default safety limit of **64 KBytes** is enforced for
any payload type. Both Invoker and Executor must enforce this limit unless an
efficient mechanism with $O(1)$ complexity is used to transfer messages between
peers (e.g., shared memory).

## 1.10.1. Max message size adjustment per function definition

In cases where transferring larger payloads directly in the primary message
exchange protocol is necessary, limits can be adjusted per function using the
`maxreqsize` and `maxrspsize` attributes.

However, this practice is discouraged, as it may compromise service stability.

Supported units:

* 'B' - Bytes
* 'K' - Kilobytes (1024 bytes)
* 'M' - Megabytes (1024 kilobytes)

*Since: v1.8*

## 1.11. On Behalf Of calls

Executors are expected to pass authenticated user information in downstream
sub-calls so that all authorization checks are evaluated against the end user
rather than the Executor service itself. This mechanism simplifies access
control implementations in nested service topologies. If a sub-call is intended
to execute with service-level credentials, this must be managed via the System
Invoker interface options.

*Since: v1.3*

A set of predefined optional field names is available, but the `obf` object is
extendable with custom metadata by design. Edge executors must ensure that the
field is rejected for security reasons, except for some custom designated
metadata, which cannot compromise system's security model. All field values
must be of string type.

Predefined optional fields:

- `lid`: for local service user IDs;
- `gid`: for global/federated user IDs;
- `slvl`: for original security level as identified by the edge Executor;
- `token`: for JWT and similar original tokens passthrough;
- `trace_id`: for correlation IDs defined by edge Executors.


*Since v1.10*

## 1.12. Minimum user authentication security level

Each function can define a `seclvl` attribute specifying the minimum required
user authentication security level. This governs user validation rather than
access control (e.g., sensitive operations may mandate two-factor or public-key
authentication). A security level mismatch must trigger a **PleaseReauth**
error, with the first word of the error description specifying the required
security level.

All unrecognized security level identifiers must be treated as requiring the
maximum level of security.

## 1.13. Message coding formats

Invokers and Executors may support different sets of message serialization
formats. Whenever a format mismatch occurs, the Executor must respond with a
JSON-encoded error. The Invoker must then automatically fall back to JSON
encoding for all subsequent requests.

Auto-detection of message serialization formats follows these rules (when the
message begins with ASCII):

1. `{` - Use JSON
2. `CBOR` - Use CBOR
3. `MPCK` - Use MessagePack
4. Otherwise - Fall back and attempt JSON parsing

### 1.13.1. JSON

JSON is defined in [ECMA-404](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf).

JSON encoding must be supported by all standard Invoker and Executor
implementations. Implementations for resource-constrained embedded devices may
omit JSON support provided there is a clear justification based on size
reduction.

Because every FutoIn message is a JSON object, messages must start with the
ASCII character `{` with no leading whitespace.

### 1.13.2. CBOR

CBOR is defined in [RFC 7049](https://tools.ietf.org/html/rfc7049).

All CBOR-encoded messages must be prefixed with the 4-byte ASCII string `CBOR`.

### 1.13.3. MessagePack

MessagePack is defined in the [GitHub spec](https://github.com/msgpack/msgpack/blob/master/spec.md).

All MessagePack-encoded messages must be prefixed with the 4-byte ASCII string
`MPCK`.

# 2. Interface concept

Executor-side function identifiers are grouped into interfaces defined using
FutoIn format specifications (referred to individually as a "*spec*" or
collectively as "*specs*").

All specs used in a system should be available to both Invoker and Executor for
dynamic retrieval from specialized repositories over the network. Repository
access structures are described later in this document.

For performance and reliability, specs may be pre-bundled or embedded directly
within Invoker and Executor applications.

Interfaces must be defined in a machine-readable JSON format. While generic
JSON Schema specifications exist, they are too flexible for strict interface
definitions. FutoIn therefore defines its own structured JSON schema for
interface specifications below.


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
                                    "pattern" : "^any|boolean|integer|number|string|map|array|enum|set|data|[A-Z][a-zA-Z0-9]+$"
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
                                    "type": ["string", "array"]
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
                                                    "type" : ["string", "array"],
                                                    "pattern" : "^any|boolean|integer|number|string|map|array|[A-Z][a-zA-Z0-9]+$"
                                                },
                                                "optional" : {
                                                    "type" : "boolean",
                                                    "description" : "If true the field is optional. Defaults to null"
                                                },
                                                "desc" : {
                                                    "type" : "string",
                                                    "description" : "Field description"
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
                                                    "type" : ["string", "array"],
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
                                                    "type" : ["string", "array"],
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
                                    "description" : "If not set then arbitrary data upload is not allowed."
                                },
                                "rawresult" : {
                                    "type" : "boolean",
                                    "description" : "If set then no FutoIn response is assumed. Arbitrary raw data is sent instead."
                                },
                                "throws" : {
                                    "type" : "array",
                                    "uniqueItems": true,
                                    "description" : "List of associative error names, which can be triggered by function execution"
                                },
                                "heavy" : {
                                    "type" : "boolean",
                                    "description" : "Mark request as \"heavy\" in terms processing"
                                },
                                "maxreqsize" :  {
                                    "type" : "string",
                                    "pattern" : "^[1-9][0-9]*(B|K|M)$",
                                    "description" : "Specify max request size"
                                },
                                "maxrspsize" :  {
                                    "type" : "string",
                                    "pattern" : "^[1-9][0-9]*(B|K|M)$",
                                    "description" : "Specify max response size"
                                },
                                "seclvl" : {
                                    "type" : "string",
                                    "description" : "Minimum user authentication security level"
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
                        "pattern" : "^AllowAnonymous|SecureChannel|BiDirectChannel|MessageSignature|BinaryData|[a-zA-Z0-9]+$"
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

An interface identifier (name) is assumed to be unique and consists of several
string tokens joined by dot (`.`) separators. Each token must be a lowercase
alphanumeric ASCII sequence.

    Example: "futoin.event.receiver", "futoin.event.poll"

The first token of the identifier must reference a related domain name or be
sufficiently unique to prevent name collisions (e.g., trademarks or registered
namespaces). [Java package naming convention][JAVA-NAME] is highly suggested as
the guideline.
    
    Example: "com.example.interface", "org.example.namespace.interface"

**Note: The "futoin." interface prefix is reserved exclusively for official
FutoIn project specifications.**

### 2.2.2. Function identifier

Function names follow camelCase formatting. Example: "someFunc", "anotherFunc"

**Note: The "futoin" function prefix is reserved for internal system functions.**


### 2.2.3. Parameter/Result identifier

Parameter and result variable names follow snake_case formatting
(`small_caps_with_underscore`).
Example: "some_param", "some_result_value"



## 2.3. Interface inheritance

Domain-specific interfaces often share a large set of common functionality and
require only a few extra functions or parameters.

An interface can inherit from another interface. It must be possible to call any
derived interface through its parent or grandparent interfaces.

Inheritance is strictly restricted to:

* Adding new functions
* Adding new parameters to existing functions:
    * The Executor must accept `null` or omitted values for these additional
      parameters.
    * All added parameters must define default values.
* Adding new result fields to existing return types:
    * The Invoker must ignore new result fields when calling the function
      through a parent interface (and should generally ignore unrecognized
      result fields).
    * Note: Changing the `rawresult` flag is strictly forbidden.

*Note: Multiple interface inheritance is not supported at this time.*

Due to how Executors handle interface lookup, a single base interface must not
be inherited by multiple derived interfaces within the same Executor instance.
*The primary purpose of inheritance is to establish reusable
**base implementation logic** that can be extended by a single derived
interface.*

If only an interface's definitions should be reused without sharing implementation
logic then the mixin/import feature should be used instead.


## 2.4. Interface operation requirements

Interfaces can enforce runtime requirements using the `requires` attribute.

Standard requirement options:

* `AllowAnonymous` - The interface accepts calls without Client Authentication
    details.
* `SecureChannel` - Message transport must occur over an encrypted channel to
    protect sensitive payloads. Channel encryption is the joint responsibility
    of the Client and Service implementations.
* `BiDirectChannel` - Transport channels must support bi-directional message
    exchange (allowing both peers to act as Invokers and Executors).
* `MessageSignature` - Mandates payload signatures for all messages (e.g., HMAC).
* `BinaryData` - Mandates binary-friendly transport protocols and codecs (e.g.,
    CBOR instead of JSON).

To maintain security, inheriting interfaces must explicitly re-declare all
`requires` directives defined by parent interfaces.

## 2.5. Interface repositories

All publicly released specifications must be hosted in an accessible repository
containing two identically structured directory trees: "**draft**" and
"**final**".

Each tree contains:

* **meta/** - Directory containing generated machine-readable data files.
* **preview/** - Directory containing generated HTML renderings of
    specifications.
* **misc/{spec_name}/** - Optional directory holding assets used to generate
    the specification.
* Markdown (`.md`) specification source files using FutoIn custom extensions.

The **meta/** and **preview/** folders must follow this naming convention:

* **{interface_name}-{major}.{minor}-iface.json** - Explicit version spec
    definition file (historical versions must be retained).
* **{interface_name}-{major}-iface.json** - Pointer/symlink to the latest
    `{minor}` version for the `{major}` release.
* **{interface_name}-iface.json** - Pointer/symlink to the latest overall
    interface version.
* **{schema_name}-{major}.{minor}-schema.json** - Versioned JSON Schema file
    (following the same symlink conventions).
* **{schema_name}-{major}-schema.json** - Latest major release schema pointer.
* **{schema_name}-schema.json** - Absolute latest schema pointer.

*Note: `{minor}` version numbers must not include the `DV` prefix.*

*Note: By convention, specification repository domain names should use the
`specs.` subdomain prefix and be available via HTTP and/or HTTPS.*

Automatic retrieval processes must check **final/meta/** first before searching
**draft/meta/**. This allows application code to remain unchanged during spec
development and after final publication. However, draft specifications remain
subject to change without version updates; applications should cache draft specs
using short Time-To-Live (TTL) durations or disable caching entirely.

## 2.6. Iface definition spec version

Every interface definition must specify an `ftn3rev` field formatted as
`MAJOR.MINOR`. If this field is omitted, FTN3 revision 1.0 is assumed.

Invoker implementations must permit interface loading as long as the major
version is supported, regardless of the minor version.

Executor implementations must permit interface loading only if the exact
specified FTN3 revision is fully supported.

## 2.7. Interface mixin

Interface mixins provide a lightweight solution when **interface definitions**
need to be reused across unrelated implementation structures (for example,
standard CRUDL patterns).

Mixin interfaces are imported using the `imports` array containing
`iface:version` string identifiers.

The import procedure handles `types`, `funcs`, and `requires` declarations
identically to standard inheritance. However, an imported mixin is not
recognized as a parent interface class.

If an imported interface contains its own `imports` definitions, these must be
treated as if declared directly at the top level of the primary interface.
Duplicate imports of compatible interface versions will be merged automatically
to resolve diamond-dependency patterns.

## 2.8. "Heavy" requests

Functions that require significant system resources can be designated as
"heavy". Executors may use this metadata to constrain concurrent heavy
invocations to protect system stability and performance. Heavy requests may also
be assigned longer default timeout thresholds.


[json]: http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf "JSON"
[json-schema]: http://tools.ietf.org/html/draft-fge-json-schema-validation-00 "JSON-SCHEMA"
[java-name]: https://docs.oracle.com/javase/tutorial/java/package/namingpkgs.html "JAVA-NAME"


=END OF SPEC=
