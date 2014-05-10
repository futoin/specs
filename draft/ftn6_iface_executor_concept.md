<pre>
FTN6: FutoIn Interface bindings in strict type languages
Version: 0.DV
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# Warning

This specification IS NOT mandatory. It just a reference model.
Any implementation IS ALLOWED to provide own architecture with
drawback of breaking easy migration from one to another.

# 1. Concept

There must be a generic object type, which can represent both
request and response message data.

There must be a wrapper, which holds current request-response info
and potentially as set of standard utilities.

There must be a generic request Executor, which knows all registered
interfaces and their implementations.

Executor implementation is not limited in internal behavior, but should
have standardized interface even for helper tools, like FutoIn interface
compilers and/or converters.


Executor is responsible for:

1. converting request from transport-level representation to internal message format
2. gathering basic request-response info
3. checking interface constraints
4. checking message security (HMAC) or authenticating user by credentials
5. passing control to implementation
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

Executor should also 
           
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
2. Each abstract must return no value and take exactly one
    Request Info object as argument
3. Method can assume that all request parameters can be
    accessed from request data
4. Access to unexpected request and/or response parameters
    should raise InternalError
5. Throw of unexpected error should raise InternalError
6. Each method should have public accessed
7. There must be no other public method
8. All native interfaces should inherit from single
    native interface with no abstract methods

## 2.2. Request Info

1. request() - return reference to request parameter map
2. response() - return reference to response parameter map
3. info() - return reference to info parameter map
4. throw(name) - set request error and raise exception to complete execution
5. getSecurityLevel() - get current authentication security level
6. getUser() - get user object
7. getSourceAddress() - reference to source IPv4/IPv6/etc. address
8. getDerivedKey() - generate, cache and return derived key to be used in HMAC
    and perhaps other places. Implementation may forbid its use.
9. async() - mark request as asynchronous and return async completion interface

## 2.3. User info

1. getLocalID() - get user ID as seen by trusted AuthService (integer)
2. getGlobalID() - get globally unique user ID (string)
3. getXYZ() - where XYZ is standard field identifier, like FirstName, DateOfBirth, AvatarURL, etc.

## 2.4. Source Address

1. getHost() - numeric, no name lookup
2. getPort()
3. getType() - IPv4, IPv6

## 2.5. Derived Key

1. getRaw()
2. getBaseID()
3. getSequenceID()
4. encrypt( data ) - return Base64 data
5. decrypt( data ) - decrypt Base64 data

## 2.6. Async completion interface

1. parent() - return reference to original request info
2. throw( name ) - complete request with error, but do not throw anything
3. complete() - complete request
4. checkAlive() - check, if request can be completed (client is still connected)



