<pre>
FTN6: FutoIn Executor Concept
Version: 1.DV0
Date: 2014-09-26
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# Warning

This specification IS NOT mandatory. It is just a reference model.
Any implementation IS ALLOWED to provide own architecture with
drawback of breaking easy migration from one to another.

# 1. Concept

There must be a generic object type, which can represent both
request and response message data and/or communication channels.

There must be a wrapper, which holds current request-response info
and potentially as set of standard utilities.

There must be a generic request Executor, which knows all registered
interfaces and their implementations.

Executor implementation is not limited in internal behavior, but should
have standardized interface even for helper tools, like FutoIn interface
compilers and/or converters.


Executor is responsible for (actions are done in AsyncSteps):

1. converting request from transport-level representation to internal message format
2. gathering basic request-response info
3. checking interface constraints
4. checking message security (HMAC) or authenticating user by credentials
5. passing control to implementation of specific interfaces with required major version
6. catching exceptions or normal result
7. converting response to transport-level representation
8. maintaining persistent communication channel, if needed

                    Firewall
        Client          ||  Executor           Implementation
           .            || [Register]                 .
           .            ||      |                     .
           |----- Request ----->|                     .
           |            ||  [Unpack]                  .
           |            ||   [Info]                   .
           |            || [Constraints]              .
           |            ||  [Security]                .
           |            ||      |---- Invoke -------->|
           |            ||      |<-- Except/Result ---|
           |            ||   [Pack]                   .
           |<---- Response -----|                     .
           .            ||      |                     .
           .            ||      |                     .


Executor should be tighly integrated with MasterService implementation, if supported.
General FutoIn message verification should be based on HMAC checking.

Executor should also integrate with AuthService as consumer.

*Note: Executor is allowed to pass control to implementation only if requested major version of
interfaces exactly matches implemented version and minor version is greater than or equal
to requested minor version.*


All actions are implemented through AsyncSteps interface ([FTN12: Async API](./ftn12\_async\_api.md)).
For backward compatibility and/or complex logic, it is possible to make blocking
implementation. Such implementations run in dedicated worker threads/processes and receive only RequestInfo
object reference.

All true asynchronous implementation must implement special FutoIn AsyncImplementation interface to
clearly distinguish more advanced one.

Method signatures:

    void AsyncMethod( AsyncSteps as, RequestInfo reqinfo );
    void BlockingMethod( RequestInfo reqinfo );


## 1.1. FutoIn interfaces

Interfaces must get converted according to language/platform-specific
convention into native interfaces, which can depend only on
standard runtime and native language/platform-specific interfaces
of Executor and related objects.


# 2. Native Executor interface requirements

Language/platform should support runtime introspection and
exceptions. For other cases, platform/language-specific workarounds
are assumed.


## 2.1. FutoIn interface

1. Each FutoIn interfaces is represented as simple native
    interface type with only abstract methods for each
    FutoIn interface function
2. Each abstract method must return no value and take exactly one
    Request Info object as argument for blocking implementation. Or
    AsyncSteps and RequestInfo objects as arguments for asynchronous
    implementation.
3. Method can assume that all request parameters can be
    accessed from request data
4. Access to unexpected request and/or response parameters
    should raise InternalError
5. Throw of unexpected error should raise InternalError
6. Each implementation method should have public access
7. There must be no public method which is not part of the
    specific FutoIn interface definition
8. All native interfaces should inherit from single
    native interface with no public abstract methods

## 2.2. Request Info

1. constants:
    * SL_ANONYMOUS = "Anonymous"
    * SL_INFO = "Info"
    * SL_SAFEOPS = "SafeOps"
    * SL_PRIVLEGED_OPS = "PrivilegedOps"
    * SL_EXCEPTIONAL_OPS = "ExceptionalOps"
    * INFO_X509_CN - validated x509 certificate CN field
    * INFO_PUBKEY - public key, if present
    * INFO_CLIENT_ADDR - SourceAddress object of request external to current system
        (e.g. without *trusted* reverse proxies, gateways, etc.)
    * INFO_USER_AGENT - User Agent, coming from HTTP headers or other source
    * INFO_COOKIES - array of strings
    * INFO_SECURE_CHANNEL - boolean - is request coming through secure channel?
    * INFO_REQUEST_TIME_FLOAT - platform-specific timestamp of request processing start
    * INFO_SECURITY_LEVEL - one of pre-defined security levels of current processing
    * INFO_USER_INFO - user information object
1. request() - return reference to request parameter map
1. response() - return reference to response parameter map
1. info() - return reference to info parameter map, keys (defined as const with INFO_ prefix):
1. error(name) - set request error and raise exception to complete execution
1. derivedKey() - return associated derived key to be used in HMAC
    and perhaps other places. Implementation may forbid its use. Note: can be null
1. log() - returns extended API interfaces defined in [FTN9 IF AuditLogService][]
1. rawInput() - return raw input stream or null, if FutoIn request comes in that stream
1. rawOutput() - return raw output stream (no result variables are expected)
1. context() - get reference to Executor
1. rawRequest() - get request object, representing FutoIn message
1. rawResponse() - get response object, representing FutoIn message
1. ignoreInvokerAbort( [bool=true] ) - [un]mark request as ready to be canceled on
    Invoker abort (disconnect)
1. http_header( name, value [,override=true] ) - set HTTP response headers
    * should not be used in regular processing
    * *name* - HTTP header name
    * *value* - HTTP header value
    * *override* - boolean - Should any previously set header with the same $name be overridden?


## 2.3. User info

1. localID() - get user ID as seen by trusted AuthService (string)
1. globalID() - get globally unique user ID (string)
1. details( AsyncCompletion async_compl, array user_field_identifiers )
    * Request more detailed user information gets available
    * Note: executor implementation should cache it at least in scope of current request processing


## 2.4. Source Address

1. host() - numeric, no name lookup
1. port()
1. type() - IPv4, IPv6
1. asString() "Type:Host:Port"


## 2.5. Derived Key

1. baseID()
1. sequenceID()
1. encrypt( AsyncSteps as, data ) - return Base64 data
1. decrypt( AsyncSteps as, data ) - decrypt Base64 data


## 2.6. General Async Step interface

See [FTN12 Async API](./ftn12\_async\_api.md)


## 2.7. Async completion interface

AsyncCompletion inherits from *AsyncSteps* interface. When all steps are executed and request info is
still not complete, InternalError is automatically raised

1. reqinfo() - return reference to original request info

## 2.8. Executor

1. ccm() - get reference to Invoker CCM, if any
1. register( ifacever, impl ) - add interface implementation
    * ifacever must be represented as FutoIn interface identifier and version, separated by colon ":"
    * impl is object derived from native interface or associative name for lazy loading
1. process( AsyncCompletion async_completion ) - do full cycle of request processing, including all security checks
1. checkAccess( AsyncCompletion async_completion, acd ) - shortcut to check access through #acl interface


## 2.9. Interface Implementation

No public members


# 3. Language/Platform-specific notes

## 3.1. native JVM (Java, Groovy, etc.)

## 3.2. Python

## 3.3. PHP

## 3.4. C++


[RAII]: http://en.wikipedia.org/wiki/Resource_Acquisition_Is_Initialization "Resource Acquisition Is Initialization"

=END OF SPEC=
