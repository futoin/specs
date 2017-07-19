<pre>
FTN11: FutoIn - Implementation Feature Requirements
Version: 0.1
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# 1. Intro

Invoker and Executor implementation may not implement all required interfaces,
but they are required to provide dummy placeholder, which still allow to
operate. Below is a summary of required features for Invoker and Executor to
be implemented.

Note: version of this specification also serves as implementation feature
list to be used in dependency management.

# 2. Executor requirements

## 2.1. Service-side Executor requirements
* [futoin.ping](./ftn4\_if\_ping.md)
* [futoin.master.provider](./ftn8\_security\_concept.md)
* Client for [futoin.auth.backend](./ftn8\_security\_concept.md)
* [futoin.auth.consumer](./ftn8\_security\_concept.md)
* Client for [futoin.acl.provider](./ftn8\_security\_concept.md)
* [futoin.acl.consumer](./ftn8\_security\_concept.md)
* Client for [futoin.defense.provider](./ftn8\_security\_concept.md)
* [Interface Executor Concept](./ftn6\_iface\_executor\_concept.md)
* Client for [futoin.log](./ftn9\_if\_auditlog.md)
* [futoin.burst](./ftn10\_burst\_calls.md)
* HTTP and WebSocket end-point [FTN5 HTTP integration](./ftn5\_iface\_http\_integration.md)

## 2.2. Client-side Executor requirements
* In-Channel [futoin.ping](./ftn4\_if\_ping.md)
* In-Channel [futoin.master.consumer](./ftn8\_security\_concept.md)
* Optional: [FTN6 Interface Executor Concept](./ftn6\_iface\_executor\_concept.md)
    * If not implemented, In-Channel Executor interfaces must be handled
        internally by Client-side implementation

# 3. Invoker requirements

## 3.1. Invoker requirements - Simple CCM
* Client-side Executor requirements (#3)
* [Credentials or HMAC-based message security](./ftn8\_security\_concept.md)
* If interactive, support for "Unauthorized" error:
    * [Client for futoin.auth.consumer](./ftn8\_security\_concept.md)
* Simple part of [FTN7 Interface Invoker Concept](./ftn7\_iface\_invoker\_concept.md)
* Dummy API for [futoin.burst](./ftn10\_burst\_calls.md)
* Client for HTTP end-point [FTN5 HTTP integration](./ftn5\_iface\_http\_integration.md)


## 3.2. Invoker requirements - Advanced CCM
* Invoker requirements - Simple CCM (#4)
* [Both Credentials AND HMAC-based message security](./ftn8\_security\_concept.md)
* Full support [FTN7 Interface Invoker Concept](./ftn7\_iface\_invoker\_concept.md)
* Full API for [futoin.burst](./ftn10\_burst\_calls.md)
* Client for WebSocket end-point [FTN5 HTTP integration](./ftn5\_iface\_http\_integration.md)

=END OF SPEC=
