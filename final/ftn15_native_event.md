<pre>
FTN15: Native Event API
Version: 1.1
Date: 2017-12-26
Copyright: 2015-2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.1 - 2017-12-26 - Andrey Galkin
    - NEW: fail on unknown event names
    - NEW: control of max listeners per event
* v1.0 - 2015-01-19

# 1. Concept

There is nothing new in this specification, but a formalization for
referencing of a well known API pattern in JavaScript world.

Any object may have on(), off(), once() and emit() methods to
register event handler, unregister event handler, register event
handler to catch only once and emit events.

Event handler must get executed with no emit() call in function stack.

Allowed event name list must be provided during initialization. Public
API must fail on unknown event, if applicable.

There should be soft control of max listeners per event and
implementation-defined warning when limit is reached.

All manipulations of EventEmitter settings should be done through
API which is not exposed through target object.

# 2. Native API

* class EventEmitter:
    * c-tor( event_list, max_listeners=8 )
        * `event_list` - whitelist of allowed event names
        * `max_listeners` - default threshol for the warning
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
    * static void setMaxListeners( instance, max_listeners )
        * `instance` - target object with event emitter
        * `max_listeners` - threshol for the warning

=END OF SPEC=
