<pre>
FTN7: FutoIn Invoker Concept
Version: 1.DV0
Date: 2015-01-19
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.0 - 2015-01-19

# 1. Concept

There is nothing new in this specification, but a formalization for
referencing of a well known API pattern in JavaScript world.

Any object may have on(), off(), once() and emit() methods to
register event handler, unregister event handler, register event
handler to catch only once and emit events.

Event handler must get executed with no emit() call in function stack.

# 2. API

* void on( event, handler )
    * register event handler
    * *event* - event name (string)
    * *handler* - callable, receiving optional emit() arguments
* void once( event, handler )
    * the same as on(), but handler is fired only on first event
* void off( event, handler )
    * unregister handler from the event
    * *event* - event name (string)
    * *handler* - the handler originally passed to on() or once()
* void emit( event [, arg1, arg2, ...] )
    * Fire an event
    * *event* - event name (string)
    * *args* - optional arguments to be passed to event handler

=END OF SPEC=
