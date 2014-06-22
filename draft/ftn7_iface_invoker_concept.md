<pre>
FTN6: FutoIn Invoker Concept
Version: 0.1
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# Warning

This specification IS NOT mandatory. It is just a reference model.
Any implementation IS ALLOWED to provide own architecture with
drawback of breaking easy migration from one to another.


# 1. Concept

There must be a centralized connection and credentials manager (CCM) object.
It should be possible to create multiple independent instances of such type.

Each connection end-point should have a unique associative name in scope of
single CCM object. Connection end-points can be statically and/or dynamically
registered/configured. More advanced implementation may use centralized service to
resolve/retrieve connection end-points and related credentials on demand.

Invoker code retrieves FutoIn interface references from CCM object and invokes
FutoIn interface function through special "call" method, passing function name
and associative parameter map. Invocation result is returned as a map of result
values.

There should be a common FutoIn exception type from which Expected and Unexpected
FutoIn exception types must inherit as defined in FTN3.

By design, most Executor implementation also implement Invoker design as it is required
for separation of concerns on Service/RPC level, but not single project level.

# 1.1. Reserved interface names

Some of interface names can be reserved for internal semantics, like runtime
resolving service interface.

All names starting with hash "#" symbol are reserved for internal purpose in
Invoker implementation concept.

Pre-defined interfaces names:

* "#resolver" - end-point for runtime resolution
* "#auth" - AuthService end-point
* "#defense" - defense system end-point
* "#acl" - defense system end-point
* "#log" - audit logging end-point

# 1.2. Type and identifier safety

There should be a Simple CCM, which is lightweight and designed for small memory
footprint and/or high performance cases. Advanced CCM interface should inherit
from the Simple one.

Advanced CCM implementation must implement a special native dummy interface,
even if there is no difference with Simple one, so native link/resolve error is generated,
if Simple CCM implementation is provided to Client code, which expects Advanced CCM.

Advanced CCM implementation can retrieve FutoIn interface definitions and enforce
additional checks, including compile and/or run-time specialized native interface
building.

In such process, FutoIn interface functions must become native interface members with
every function parameter becoming native member's formal parameter. If multiple
values can be returned natively, result values are mapped to those. Otherwise,
map of result values is returned. If there is only one return value then it
becomes return value of native member instead of result value map. If there are no
result values then native member returns nothing and should complete as soon
as request message is scheduled to be sent without waiting for reply.

Note: Simple CCM is not expected to parse interfaces. Therefore, all request
messages must have "forcersp" flag and Simple CCM must expect response for every call.

# 1.2. Invoker calls to Executor in scope of the same process

FutoIn implementations are allowed to optimize calls within single process in
implementation-defined way, keeping the same behavior between remote and local calls.

Local calls must never execute if there are Invoker frames on stack. It means, Invoker
function must return or Executor must run in a different thread. Yes, it may have performance
issues.


# 2. Invoker interfaces

## 2.1. Connection and Credentials Manager

1. register( name, ifacever, endpoint ) - register standard MasterService end-point
2. registerPlain( name, ifacever, endpoint, credentials ) - register end-point with 'plain" credentials
3. iface( name [, ifacever [,$endpoint [, $credentials]]] ) / getIface<Spec\>( name [, ifacever [,$endpoint [, $credentials]]] ) - get end-point's native interface by name
4. unRegister( name ) - unregister any type of interface (should not be used, unless really needed)
5. defense() - shortcut to getIface( "#defense" )
6. log() - returns extended API interfaces defined in [FTN9 IF AuditLogService][]
7. burst() - returns extended API interfaces defined in [FTN10 Burst Calls][]

*Note: iface must be represented as FutoIn interface identifier and version, separated by colon ":"
Example: "futoin.master.service:1.0", "futoin.master.service:2.1"*

## 2.2. Native FutoIn interface interface

1. results call( name, params ) throws FutoInError - generic FutoIn function call interface
2. callAsync( async_iface, name, params ) - generic FutoIn asynchronous function call interface
3. iface() - return interface to introspect interface information:
    1. name() - get FutoIn interface type, may be not implemented
    2. version() - get FutoIn interface version, may be not implemented
    3. inherits() - get list of inherited interfaces
    4. funcs() - get list of available functions
    5. constraints() - get list of interface constraints
4. callDataAsync( async_iface, name, params, upload_data )
    * generic FutoIn asynchronous function call interface with data transfer
    * upload_data - map of input streams or buffers
    * Note: all data transfer requests must be done through separate communication channel
5. burst() - returns extended API interfaces defined in [FTN10 Burst Calls][]


Note: result is either 

## 2.3. Derived Key accessing wrapper

This interface is designed only if access to Derived Key is expected.

1. Constructor( iface ) - wrap iface and act as proxy
2. getDerivedKey()
3. *() - any function, calls underlying iface function, ensuring the right derived key in use

## 2.4. Derived Key

See FTN6: Interface Executor Concept

## 2.5. Async callback interface

See FTN12: Async API - AsyncSteps

# 3. Language/Platform-specific notes

## 3.1. native JVM (Java, Groovy, etc.)

## 3.2. Python

## 3.3. PHP

## 3.4. C++


[FTN9 IF AuditLogService]: ./ftn9\_if\_auditlog.md "FTN9 Interface - AuditLog"
[FTN10 Burst Calls]: ./ftn10\_burst\_calls.md "FTN10 Burst Calls"

