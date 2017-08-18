<pre>
FTN6: FutoIn Executor Concept
Version: 1.6DV
Date: 2015-03-08
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.6 - 2017-08-18
    * NEW: RequestInfo.result(replace)
    * NEW: "-internal" in "sec" for internal channel calls
* v1.5 - 2015-03-08
    * Added "System" security level for internal communications
    * Fixed SL_SAFEOPS -> SL_SAFE_OPS, SL_PRIVLEGED_OPS -> SL_PRIVILEGED_OPS
* v1.4 - 2015-02-22
    * Added HMAC support
* v1.3 - 2015-01-25
    * added RequestInfo.cancelAfter()
    * added security notes
    * added ChannelContext.register() & ChannelContext.iface()
    * added onEndpointRequest() & onInternalRequest()
    * added Executor close()
* v1.2 - 2014-12-26
    * More precise executor function result return
    * Updated rawInput() / rawOutput() to throw error, instead of returning null on error
* v1.1 - 2014-10-11
    * Dropped INFO_COOKIES and INFO_USER_AGENT (were not used)
    * Added concept of ChannelContext/INFO_CHANNEL_CONTEXT
        * HTTPChannelContext is defined in scope of FTN5: HTTP Integration
    * Added INFO_HAVE_RAW_RESULT
    * Dropped ignoreInvokerAbort() and replaced with ChannelContext.onInvokerAbort()
        (would be broken backward compatibility, if used somewhere)
    * Changed context() to executor() to avoid ambiguity
        (would be broken backward compatibility, if used somewhere)
* v1.0 - 2014-10-03

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

## 1.2. Executor security

Besides standard authentication and authorization mechanisms, peer with executor capabilities
must create separate Executor objects to minimize risk of security flaws in such mechanisms.
Example:

* A single process implements:
    * public services with Master/Slave key exchange authentication
    * private services with Basic login/password authentication
    * internal services like Logger DB access
* The correct way would be:
    1. Create a single CCM object
    1. Create bare Executor for internal service implementation
    1. Create HTTP/WS Executor for public services
    1. Create Executor for private services
        * Either local-transport Executor in scope of single operating system
        * Or HTTP/WS Executor, but accessible from private network only

## 1.3. HMAC generation

See [HMAC][] for details

### 1.3.1 Rules of HMAC generation for payload

* Payload has a tree structure and coded in JSON or any alternative format
* All keys and fields are feed to HMAC generator in text representation
* Top level "sec" field is skipped, if present (in case of request validation)
* For each nested level, starting from the very root of tree-like payload structure:
    * Key-value pairs are processing in ascending order based on Unicode comparison rules
    * Key is feed into HMAC generator
    * ':' separator is feed into HMAC generator
    * If value is subtree then recurse this algorithm
    * else if value is string then feed into HMAC generator
    * Otherwise, feed textual JSON representation to HMAC generator
    * ';' separator is feed into HMAC generator

### 1.3.2. Request "sec" field coding with HMAC data

The "sec" field is normally used for Basic Auth in "{user}:{password}" format.
However, a special "-hmac" user name is reserved for HMAC message signature.

The HMAC signature has the following format:
```
"-hmac:{user}:{algo}:{signature}"
```

Where:

* {user} - user name
* {algo} - on of pre-defined algorithms identifiers or custom extension
* {signature} - Base64 encoded hash

### 1.3.3. Predefined HMAC algorithms

* "MD5" - MD5 128-bit (acceptably secure, even though MD5 itself is weak)
* "SHA224" - SHA v2 224-bit (acceptably secure)
* "SHA256" - SHA v2 256-bit (acceptably secure)
* "SHA384" - SHA v2 384-bit (acceptably secure)
* "SHA512" - SHA v2 512-bit (acceptably secure)
* "SHA3-*" - SHA v3 224/256/384/512-bit (high secure at the moment)

*Note: MD5 and SHA2 are mandatory to be implemented on server, SHA3 - if supported by runtime.
However, server may reject unsupported algorithms through configuration*

### 1.3.4. Response "sec" field with HMAC

If request comes signed with HMAC then response must also be signed
with HMAC using exactly the same secret key and hashing algorithm.

Only Base64-encoded signature in sent back in the "sec" field.

### 1.4. Internal system calls security

If internal communication channel is used, a special "-internal" user
name can be passed in "sec" field.

Such internal calls must bypass Auth Service processing and trust
on-behalf-of data in request message. Otherwise, user info must
"-internal" for both local and global user ID, SL_SYSTEM must be set
as security level.

Normally, internal channel can exist only with the same process.

# 2. Native Executor interface requirements

Language/platform should support runtime introspection and
exceptions. For other cases, platform/language-specific workarounds
are assumed.


## 2.1. FutoIn interface

1. Each FutoIn interfaces is represented as simple native
    interface type with only abstract methods for each
    FutoIn interface function
2. Each abstract method should return no value and take exactly one
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
    * SL_SAFE_OPS = "SafeOps"
    * SL_PRIVILEGED_OPS = "PrivilegedOps"
    * SL_EXCEPTIONAL_OPS = "ExceptionalOps"
    * SL_SYSTEM = "System"
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
1. map result([replace]) - return reference to response parameter map
    - NOTE: replaced result may be of any type expected by interface definition
1. map info() - return reference to info parameter map, keys (defined as const with INFO_ prefix):
    * Note: info() is not merged to AsyncSteps only for minor security reasons
1. stream rawInput() - return raw input stream or throws error
1. stream rawOutput() - return raw output stream (no result variables are expected) or throws error
1. Executor executor() - get reference to Executor
1. ChannelContext channel() - get reference to ChannelContext
1. void cancelAfter( timeout_ms ) - set to abort request after specified timeout_ms from the
    moment of call. It must override any previous cancelAfter() call.
    *Note: it is different from as.setTimeout() as inner step timeout does not override outer step
    timeout.*
    * *timeout_ms* - timeout in miliseconds to cancel after. 0 - disable timeout
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
1. string asString() "Type:Host:Port" or "Type:Port"


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
1. void onEndpointRequest( info, ftnreq, send_executor_rsp )
    * Entry point for Server-originated requests
    * *info* - internal CCM interface info
    * *ftnreq* - incoming FutoIn request object
    * *send_executor_rsp( rsp )* - callback to send response
1. void onInternalRequest( as, info, ftnreq )
    * Entry point for in-program originated requests. Process with maximum efficiency
    * *info* - internal CCM interface info
    * *ftnreq* - incoming FutoIn request object
    * returns ftnrsp through as.success() or fails through as.error()
1. void checkAccess( AsyncSteps as, acd ) - shortcut to check access through #acl interface
    * as->reqinfo must point to instance of RequestInfo
1. void initFromCache( AsyncSteps as )
    * load initialization from cache
1. void cacheInit( AsyncSteps as )
    * store initialization to cache
1. void close()
    * Shutdown Executor processing


## 2.9. Interface Implementation

No public members, except for members of the implemented spec.

Each call can set result variables the following way:

1. through reqinfo.result() map
2. by returning a map from the function
3. by returning a map through as.success() call
4. by replacing result through reqinfo.result(replace)

*Note: Executor implementation must merge all possible ways to set result variables
in the strict order as listed above.*

## 2.10. Channel Context

*ChannelContext* interface

* string type() - get type of channel
    * HTTP (including HTTPS)
    * WS
    * BROWSER
    * TCP
    * UDP
    * UNIX
    * any other - as non-standard extension
* boolean isStateful()
    * check if current communication channel between Invoker and Executor is stateful
* map state() - get channel state variables
    * state is persistent only for stateful protocols
* void onInvokerAbort( callable( AsyncSteps as, user_data ), user_data=null )
* void register( as, ifacever, options )
    * Register interface as implemented by client peer
    * *ifacever* - iface identifier and its version separated by colon
    * *options* - options to pass to AdvancedCCM.register()
* NativeIface iface( ifacever )
    * Get native interface wrapper for invocation of iface methods on client peer
    * *ifacever* - iface identifier and its version separated by colon
* Language/Platform-specific get/set/remove/check accessors to state variables

Various specification can extend this interface with additional functionality.

[hmac]: http://www.ietf.org/rfc/rfc2104.txt "RFC2104 HMAC"
[base64]: http://www.ietf.org/rfc/rfc2045.txt "RFC2045 section 6.8"
[RAII]: http://en.wikipedia.org/wiki/Resource_Acquisition_Is_Initialization "Resource Acquisition Is Initialization"

=END OF SPEC=
