<pre>
FTN6: FutoIn Invoker Concept
Version: 0.DV
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

* #resolver - end-point for runtime resolution
* #auth - AuthService end-point
* #defense - defense system end-point

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

# 1.2. Invoker calls to Executor in scope of the same process

FutoIn implementations are allowed to optimize calls within single process in
implementation-defined way, keeping the same behavior between remote and local calls.

Local calls must never 


# 2. Invoker interfaces

## 2.1. Connection and Credentials Manager

1. register( name, iface, endpoint ) - register standard MasterService end-point
2. registerPlain( name, iface, endpoint, credentials ) - register end-point with 'plain" credentials
3. getIface( name ) / getIface<Spec.>( name ) - get end-point's native interface by name
4. unregister( name ) - unregister any type of interface (should not be used, unless really needed)
5. defense() - shortcut to getIface( "#defense" )

*Note: iface may represented as plain FutoIn interface identifier or "{ID}:{Version}" pair.
Example: "futoin.master.service", "futoin.master.service:1.0"*

## 2.2. Native FutoIn interface interface

1. results call( name, params ) throws FutoInException - generic FutoIn function call interface
2. callAsync( name, params, callback( result ), callback( error ) ) - generic FutoIn asynchronous function call interface
3. futoinType() - get FutoIn interface type, may be not implemented
4. futoinVersion() - get FutoIn interface version, may be not implemented
5. futoinInherits() - get list of inherited interfaces
6. futoinFuncs() - get list of available functions
7. futoinConstraints() - get list of interface constraints




# 3. Language/Platform-specific notes

## 3.1. native JVM (Java, Groovy, etc.)

## 3.2. Python

## 3.3. PHP

## 3.4. C++
