<pre>
FTN3: FutoIn Interface Definition
Version: 1.DV
</pre>

# Basic concept

## Peer-to-peer communication

There is invoker and executor side. Both can be implemented in scope of single
process, different processes or different machines across network.

Multi-peer communication is assumed to be a higher level concept on top of 
current one.

Object-oriented remote calls is also assumed to be a higher level concept.

It assumed that there language- and/or software platform-specific
standardized low-level API for connection establishing and calls coupled
with optional standardized high-level binding/mapping of FutoIn interfaces
to native features.

All specifications and implementations assume to support loose coupling of
each components, suitable for easy separation, replacement and unit testing.

Each call has request and response messages with key-value pairs described below.
If a call does not expect to return any result then no response message must be
sent and/or expected to be received.
<br>
*Note: it means that call must return at least something to detect on invoker if the
call is properly executed*

Low-level protocol for message exchange is out of scope of this specification.


## Function Call

There are three major parts: *function identifier*, *parameters*, *result* and
*exception*.

* function identifier - unique associative name of string type
* parameters - key-value pairs
** key - unique associative name of string type
** value - value of arbitrary type
* result - key-value pairs, similar to parameters
* exception - associative name of first error occurred during function execution


## Client-server/service multiplexing mode

Invoker is responsible to enable request message (and response therefore)
multiplexing by adding special *request ID* field. Executor is responsible
for adding the same field to related response message.

Please note that Invoker and Client, Executor and Server side are NOT the same terms.
Client is the peer which initiated peer-to-peer communication. Server is the peer 
which accepts peer-to-peer communications.

Client side request ID must be prefixed with "C".
Server side request ID must be prefixed with "S".


## Uni-directional call pattern

Invoker/Executor side is semantically defined and does not rely on Client/Server
status of peer. There is no protocol-level support for that. Each side controls if
it can act in Executor.

It is suggested that Client side is always Invoker in uni-directional pattern.

Both serial and multiplexing modes are allowed.


## Bi-directional call pattern

Each side is both Invoker and Executor. Bi-directional pattern must always work
in message multiplexing mode.









