<pre>
FTN6: FutoIn Executor Concept
Version: 1.DV0
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
It is required almost for each request to validate and generate HMAC.

Executor should also integrate with AuthService consumer.

*Note: Executor is allowed to pass control to implementation only if requested major version of
interfaces exactly matches implemented version and minor version is greater than or equal
to requested minor version.*


All actions are implemented through AsyncSteps interface ([FTN12: Async API](./ftn12\_async\_api.md)).
For backward compatibility and/or complex logic, it is possible to make blocking
implementation. Such implementations run in dedicated worker threads and receive only RequestInfo
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

Language/platform must support runtime introspection and
exceptions.


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

1. request() - return reference to request parameter map
1. response() - return reference to response parameter map
1. info() - return reference to info parameter map, keys (defined as const with INFO_ prefix):
    * X509_CN - validated x509 certificate CN field
    * PUBKEY - public key, if present
    * CLIENT_ADDR - IPv4, IPv6 or any other type of address
    * USER_AGENT - User Agent, coming from HTTP headers or other source
    * COOKIES - array of strings
    * SECURE_CHANNEL - boolean
    * UPLOAD_FILES - map of upload_name -> file stream
    * REQUEST_TIME_FLOAT - platform-specific reference of request creation time
    * SECURITY_LEVEL - one of pre-defined security levels of current processing
    * SOURCE_ADDRESS - source address of request external to current system
        (e.g. without *trusted* reverse proxies, gateways, etc.)
    * USER_INFO - user information object
1. error(name) - set request error and raise exception to complete execution
1. getDerivedKey() - return associated derived key to be used in HMAC
    and perhaps other places. Implementation may forbid its use.
1. log() - returns extended API interfaces defined in [FTN9 IF AuditLogService][]
1. files() - return map to uploaded temporary file streams
1. rawoutput() - return raw output stream
1. context() - get reference to Executor
1. rawRequest() - get raw request data map
1. rawResponse() - get raw response data map
1. constants:
    * SL_ANONYMOUS = "Anonymous"
    * SL_INFO = "Info"
    * SL_SAFEOPS = "SafeOps"
    * SL_PRIVLEGED_OPS = "PrivilegedOps"
    * SL_EXCEPTIONAL_OPS = "ExceptionalOps"
1. ignoreInvokerAbort( [bool=true] ) - [un]mark request as ready to be canceled on
    Invoker abort (disconnect)


## 2.3. User info

1. getLocalID() - get user ID as seen by trusted AuthService (integer)
1. getGlobalID() - get globally unique user ID (string)
1. getXYZ() - where XYZ is standard field identifier, like FirstName, DateOfBirth, AvatarURL, etc.


## 2.4. Source Address

1. getHost() - numeric, no name lookup
1. getPort()
1. getType() - IPv4, IPv6
1. asString() "Type:Host:Port"


## 2.5. Derived Key

1. getBaseID()
1. getSequenceID()
1. encrypt( data ) - return Base64 data, implementation should limit max length
1. decrypt( data ) - decrypt Base64 data, implementation should limit max length
1. encryptAsync( AsyncSteps as, data ) - return Base64 data
1. decryptAsync( AsyncSteps as, data ) - decrypt Base64 data


## 2.6. General Async Step interface

See [FTN12 Async API](./ftn12\_async\_api.md)


## 2.7. Async completion interface

AsyncCompletion inherits from AsyncSteps interface. When all steps are executed and request info is
still not complete, InternalError is automatically raised

1. reqinfo() - return reference to original request info

## 2.8. Executor

1. ccm() - get reference to Invoker CCM, if any
1. register( ifacever, impl ) - add interface implementation
    * ifacever must be represented as FutoIn interface identifier and version, separated by colon ":"
    * impl is object derived from native interface or associative name for lazy loading
1. process( AsyncCompletion as, RequestInfo reqinfo ) - do full cycle of request processing, including all security checks
1. checkAccess( AsyncCompletion as, acd ) - shortcut to check access through #acl interface



# 3. Language/Platform-specific notes

## 3.1. native JVM (Java, Groovy, etc.)

## 3.2. Python

## 3.3. PHP

## 3.4. C++


[RAII]: http://en.wikipedia.org/wiki/Resource_Acquisition_Is_Initialization "Resource Acquisition Is Initialization"

=END OF SPEC=
