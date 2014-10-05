<pre>
FTN6: FutoIn Executor Concept
Version: 1.DV1
Date: 2014-09-30
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.1
    * Dropped INFO_COOKIES and INFO_USER_AGENT (were not used)
    * Added concept of ChannelContext/INFO_CHANNEL_CONTEXT
        * HTTPChannelContext is defined in scope of FTN5: HTTP Integration
    * Added INFO_HAVE_RAW_RESULT

# Warning

This specification IS NOT mandatory. It is just a reference model.
Any implementation IS ALLOWED to provide own architecture with
drawback of breaking easy migration from one to another.

# 1. Concept

There must be a generic object type, which can represent both
request and response message data and/or communication channels.

There must be a wrapper, which holds current request-response info
and potentially a set of standard utilities.

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

Executor should also integrate with AuthService as consumer, if real human users expected to use the service.

*Note: Executor is allowed to pass control to implementation only if requested major version of
interfaces exactly matches implemented version and minor version is greater than or equal
to requested minor version.*


All actions are implemented through AsyncSteps interface ([FTN12: Async API](./ftn12\_async\_api.md)).
For backward compatibility with pre-FutoIn code and/or complex logic, it is possible to make blocking
implementation. Such implementations run in dedicated worker threads/processes and receive only RequestInfo
object reference.

All true asynchronous implementations must implement special FutoIn AsyncImplementation interface to
clearly distinguish more advanced one.

Method signatures:

    void AsyncMethod( AsyncSteps as, RequestInfo reqinfo );
    Result BlockingMethod( RequestInfo reqinfo );
    
*Note: if BlockingMethod or AsyncMethod returns result then its fields are added to already existing
result fields in reqinfo object.*


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
3. Implementation method can assume that all request parameters defined
    in spec can be accessed from request data
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
    * INFO_SECURE_CHANNEL - boolean - is request coming through secure channel?
    * INFO_REQUEST_TIME_FLOAT - platform-specific timestamp of request processing start
    * INFO_SECURITY_LEVEL - one of pre-defined security levels of current processing
    * INFO_USER_INFO - user information object
    * INFO_RAW_REQUEST - raw request object
    * INFO_RAW_RESPONSE - raw response object
    * INFO_DERIVED_KEY - derived key object
    * INFO_HAVE_RAW_UPLOAD - boolean - have raw upload (e.g. can open rawInput())
    * INFO_HAVE_RAW_RESULT - boolean - have raw result (e.g. should open rawOutput())
    * INFO_CHANNEL_CONTEXT - persistent channel context (e.g. WebSockets
1. map params() - return reference to request parameter map
1. map result() - return reference to response parameter map
1. map info() - return reference to info parameter map, keys (defined as const with INFO_ prefix):
    * Note: info() is not merged to AsyncSteps only for minor security reasons
1. stream rawInput() - return raw input stream or null, if FutoIn request comes in that stream
1. stream rawOutput() - return raw output stream (no result variables are expected)
1. Excutor context() - get reference to Executor
1. void ignoreInvokerAbort( [bool=true] ) - [un]mark request as ready to be canceled on
    Invoker abort (disconnect)
1. Language-specic get accessor for info properties


## 2.3. User info

1. string localID() - get user ID as seen by trusted AuthService
1. string globalID() - get globally unique user ID
1. void details( AsyncSteps as, array user_field_identifiers )
    * Request more detailed user information gets available
    * Note: executor implementation should cache it at least in scope of current request processing


## 2.4. Source Address

1. string host() - numeric, no name lookup
1. string port() - IP port or local path/identifier
1. string type() - IPv4, IPv6, LOCAL
1. string asString() "Type:Host:Port"


## 2.5. Derived Key

1. string baseID()
1. string sequenceID()
1. void encrypt( AsyncSteps as, data ) - return Base64 data
1. void decrypt( AsyncSteps as, data ) - decrypt Base64 data


## 2.6. General Async Step interface

See [FTN12 Async API](./ftn12\_async\_api.md)


## 2.7. Async completion interface

There is little use of extended AsyncSteps to provide additional API.
Instead, by convention, "reqinfo" AsyncSteps state field must point to
associated RequestInfo instance.

## 2.8. Executor

1. AdvancedCCM ccm() - get reference to Invoker CCM, if any
1. void register( AsyncSteps as, ifacever, impl ) - add interface implementation
    * ifacever must be represented as FutoIn interface identifier and version, separated by colon ":"
    * impl is object derived from native interface or associative name for lazy loading
1. void process( AsyncSteps as ) - do full cycle of request processing, including all security checks
    * as->reqinfo must point to instance of RequestInfo
1. void checkAccess( AsyncSteps as, acd ) - shortcut to check access through #acl interface
    * as->reqinfo must point to instance of RequestInfo
1. void initFromCache( AsyncSteps as )
    * load initialization from cache
1. void cacheInit( AsyncSteps as )
    * store initialization to cache


## 2.9. Interface Implementation

No public members

## 2.10. Channel Context

*ChannelContext* interface

* string type() - get type of channel
    * HTTP (including HTTPS)
    * LOCAL
    * TCP
    * UDP
    * any other
* boolean isStateful()
* map state() - get channel state variables
    * state is persistent only for stateful protocols
* Language/Platform-specific get/set/remove/check accessors to state variables

Various specification can extend this interface with additional functionality.



# 3. Language/Platform-specific notes

## 3.1. native JVM (Java, Groovy, etc.)

## 3.2. Python

## 3.3. PHP

## 3.4. C++


[RAII]: http://en.wikipedia.org/wiki/Resource_Acquisition_Is_Initialization "Resource Acquisition Is Initialization"

=END OF SPEC=
