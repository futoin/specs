<pre>
FTN6: FutoIn Invoker Concept
Version: 1.DV0
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

### 1.1.2. Pre-defined interfaces names:

* "#resolver" - end-point for runtime resolution
* "#auth" - AuthService end-point
* "#defense" - defense system end-point
* "#acl" - access control system end-point
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
map of result values is returned. If there are no
result values then native member returns nothing and should complete as soon
as request message is scheduled to be sent without waiting for reply.

Note: Simple CCM is not expected to parse interfaces. Therefore, all request
messages must have "forcersp" flag and Simple CCM must expect response for every call.

# 1.2. Invoker calls to Executor in scope of the same process

FutoIn implementations are allowed to optimize calls within single process in
implementation-defined way, keeping the same behavior between remote and local calls.

Local calls must never execute if there are Invoker frames on execution stack. It means, Invoker
function must return before Executor runs or Executor must run in a different thread. Yes, it may have performance
issues.


# 2. Invoker interfaces

Reference Invoker concept is built around [FTN12 Async API](./ftn12\_async\_api.md)


## 2.1. Connection and Credentials Manager

1. void register( AsyncSteps as, name, ifacever, endpoint [, $credentials] )
    * register standard MasterService end-point (adds steps to *as*)
    * *as* - AsyncSteps instance as registration may be blocking on external resources
    * *name* - unique identifier in scope of CCM instance
    * *ifacever* - iface identifier and its version separated by colon, see note below
    * *endpoint* - URI or any other resource identifier of iface implementing peer, accepted by CCM implementation
    * *$credentials* - optional, authentication credentials
1. NativeIface iface( name )
    * Get native interface wrapper for invocation of iface methods
    * *name* - see register()
    * Note: it can have template/generic counterpart like iface<NativeImpl>() for strict type languages
1. void unRegister( name )
    * unregister previously registered interface (should not be used, unless really needed)
    * *name* - see register()
1. NativeDefenseIface defense() - shortcut to iface( "#defense" )
1. NativeLogIface log() - returns extended API interfaces defined in [FTN9 IF AuditLogService][]
1. NativeBurstIface burst() - returns extended API interfaces defined in [FTN10 Burst Calls][]
1. void assertIface( name, ifacever )
    * Assert that interface registered by name matches major version and minor is not less than required.
    * This function must generate fatal error and forbid any further execution
    * *name* - see register()
    * *ifacever* - required interface and its version
1. void alias( name, alias )
    * Alias interface name with another name
    * *name* - as provided in register()
    * *alias* - register alias for *name*

### 2.1.1. Unique interface name in CCM instance (*name*)

The idea behind is that each component/library/etc. assumes that end product registers interfaces,
their endpoints and possibly provides other information during initialization phase or
prior to using the specific component.

Example:

    // Init
    AsyncSteps as;
    
    ccm.register( as, "some_id', "some.iface:1.3", "https://..." )
    ccm.alias( "some_id', "componentA.ifaceA" )
    ccm.alias( "some_id', "componentB.ifaceB" )
    
    as.add( ComponentA.init )
    as.add( ComponentB.init )
    
    as.add( startService )
    
    // start actual execution
    as.execute();
    
    // in Component A (note minor version less than registered)
    ComponentA.init()
    {
        ccm.assertIface( "componentA.iface", "some.iface:1.0" )
        iface = ccm.iface( "componentA.iface" )
        iface.someFunc()
    }

    // in Component B (note different minor version)
    ComponentB.init()
    {
        ccm.assertIface( "componentB.iface", "some.iface:1.1" )
        iface = ccm.iface( "componentB.iface" )
        iface.someFunc()
    }



### 2.1.2. Interface and version

*ifacever* must be represented as FutoIn interface identifier and version, separated by colon ":"
Example: "futoin.master.service:1.0", "futoin.master.service:2.1".

Invoker implementation must ensure that major versions match and registered minor version is not less
than requested minor version.


## 2.2. Native FutoIn interface interface

1. void call( AsyncSteps as, name, params )
    - generic FutoIn function call interface
    - result is passed through AsyncSteps.success() as a map
1. void callData( AsyncSteps as, name, params, upload_data )
    * generic FutoIn asynchronous function call interface with data transfer
    * upload_data - map of input streams or buffers
    * Note: all data transfer requests must be done through separate communication channel
1. InterfaceInfo iface() - return interface to introspect interface information:
1. NativeBurstIface burst() - returns extended API interfaces defined in [FTN10 Burst Calls][]
1. void bindDerivedKey( AsyncSteps as )
    * results with DerivedKeyAccessor through as.success()


## 2.3. Derived Key accessing wrapper

The same interface can be used in parallel. This feature generated and
binds specific DerivedKey for the following call.

1. derivedKey()
1. *() - any function, calls underlying iface function, ensuring the right derived key in use

## 2.4. Derived Key

See [FTN6 Interface Executor Concept](./ftn6\_iface\_executor\_concept.md)

## 2.5. AsyncSteps interface

See [FTN12 Async API](./ftn12\_async\_api.md)

## 2.5. InterfaceInfo

1. name() - get FutoIn interface type
1. version() - get FutoIn interface version
1. inherits() - get list of inherited interfaces starting from the most derived, may be null
1. funcs() - get list of available functions, may be null
1. constraints() - get list of interface constraints, may be null


# 3. Language/Platform-specific notes

## 3.1. native JVM (Java, Groovy, etc.)

## 3.2. Python

## 3.3. PHP

## 3.4. C++


[FTN9 IF AuditLogService]: ./ftn9\_if\_auditlog.md "FTN9 Interface - AuditLog"
[FTN10 Burst Calls]: ./ftn10\_burst\_calls.md "FTN10 Burst Calls"


=END OF SPEC=
