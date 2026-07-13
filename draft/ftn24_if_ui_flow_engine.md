<pre>
FTN24: FutoIn UI Flow Engine
Version: 1.0DV
Date: 2026-07-12
Copyright: 2026 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.0 - 2026-07-12 initial draft

# 1. Concept

This specification is tightly connected to [FTN23 Enclave Device concept][FTN23]
, which assumes presence of a secure bidirectional communication channel and
client-server model between the Enclave Device and the secure Backend.

This specification covers complex User Interface Process driving in distributed
systems. Although it is common for mobile applications and single page web
applications to drive the UI process, that creates a number of challenges
related to synchronization of the coded logic among mobile applications for
different platforms and their web counterparts. Every business logic change
requires application update, which is a challenge by itself. Quality Assurance
requires more effort, and some fine discrepancies often get unnoticed. This
specification moves the business process control duty, including screen flow, to
the backend at slight cost of added latency between UI screen switching in
Enclave Devices.

Another important part is definition of the flow. The classic approach is an
ordered graph or map for user navigation through screens. This is difficult to
maintain without errors after requirement changes. Out-of-band screens like
error messages, notifications, conditional features can easily break user
navigation without QA noticing the problem. As a solution, this specification
defines not only the interfaces, but also UI flow design approach, which is
based on requirements gathering and requirements fulfilling in predefined order.
This means that the current screen is determined not by a navigational map or
graph, but by a set of required inputs from the user in the predefined priority.

This concept is not suited for cases of chaotic navigation like dynamic games,
integrated environments, online maps, etc. However, it still remains applicable
for certain processes with business flow inside them, like making in-app
purchases or reporting a problem. Instead, the concept strictly guides users
through the screens, where they have to provide input, consent or perform
other required activity.

## 1.1. Backend-driven UI Flow concept

An Application of the Enclave Device requests certain UI process and informs
the Backend about that. The default home screen inside the application can be
considered as a process too.

Backend maintains certain Process and User Context to determine the current UI
screen to show. Backend responds with the required screen, optional properties
and a copy of the Context as seen by the Backend - the only source of truth.

Application renders required screen with specified properties and context as 
INPUT. The screen can be either embedded or dynamically loaded from the Backend.

The OUTPUT of the screen is certain navigational action to proceed with the
flow; go to previous screen, if applicable; to cancel the process. Every
action can have additional properties like input element data or reason code for
cancellation of the process.

Every navigational action should follow with a transition screen as an immediate
feedback to the user while waiting for the Backend's decision on further steps.

The Enclave Device must not employ any flow business logic, except unique
features defined inside the screens. The Device must just obey the Backend's
instructions.

There is one exception - application-specific settings and similar features
that should temporary override the Backend flow when the features are activated.

## 1.2. Process Context concept

The context consists of a subset of process and user data. The Application must
not receive the full context with possible sensitive information like risk
factors and other signals.

User data subset consists of important for UI/UX properties like greeting name,
current language, accessibility settings, and others.

Process data subset consists of the current screen to show, its dynamic
properties, other important factors for processing on the Enclave Device side.

The overall data must be compact enough to be transferred over wire in one shot
many times during the session in scope of ordinary message exchange between the
Device and the Backend, avoiding any fragile and complex incremental update
logic.

The context is typically received as a part of the response for requesting a
process or as the response for a navigational action on the current screen. It
is expected that the Backend may send out-of-band Process Context updates too.

## 1.3. Requirement Fulfillment UI Flow concept

It is assumed that the business process flow is defined as a deterministic pure
function, which operates over the Process Context data and executes
non-blocking way, and is convenient for simple Unit Testing.

Any previous screen OUTPUTs must be processed with processing outcomes reflected
in the Process Context before invoking the business process flow function for
returning the response.

Such flow function should consist from three main steps:

1. Determine static required input fulfillment for the given process.
2. Dynamically refine the inputs list based on the fulfilled data like choices.
3. Select the next screen in the priority of input requirement fulfillment. Some
   backend post-actions like process completion may also be scheduled when
   all requirements are fulfilled or certain barrier is reached.

It is not recommended to use caching for the decision making data.

## 1.4. Screen Implementation concept

Every screen is assumed to be a standalone UI component, covering whole
application interface, except some common parts like headers, footers, floating
elements, etc.

Such screen also represent a logical business process step. Therefore, screens
can have some sub-screens, popups, other dialogs, which are just UI/UX elements,
but not a reflection of the business process step.

Such screen gets rendered with a set of optional properties, which can affect
the representation or enable certain features. The Process Context should be
also available for screen rendering and controlling as an implicit input
property or in equivalent way.

## 1.5. Generic WebView and Inline Frames Screens concept

There are many cases when business wants to show some temporary introduced 
screens and processes like marketing campaigns, third-party service providers,
out-of-band questionnaires and other use cases. It is highly not desired to
force users updating installed applications or device firmware for such
purposes.

Therefore, a special type of screen is a WebView, which renders HTML-based
and JavaScript-based screens. The screen may be loaded from Backend outside of
the bidirectional communication channel, or as a direct HTML page.

For Web applications, that can be implemented as an inline frame.

It is expected that a communication channel to the hosting application is
provided through injected JavaScript-to-native proxy interfaces and/or window
events implementation-defined way.

Under such concept fall general dynamically loadable screen, which can be also
an XML form with Lua script for example.

## 1.6. Expiration time

Most of processes have certain expiration time. The spec uses absolute
timestamps, relying on assumed time synchronization of the Enclave Devices
instead of timeouts, which are relative and cannot be reliably calculated in
distribution systems.

The Device action on the current context expiration is to send "action" request
with the predefined `Expired` value as the action ID to receive new UI Flow
instructions.

## 1.7. Predefined Process, Screen and Action IDs

The following predefined Processes IDs exist:

- `Home` - the home screen process in the device;
- `Register` - the enrollment of the device process;
- `SignIn` - the authentication on the device process;

The following predefined Screen IDs exist:

- `Home` - used in combination with the `Home` process, like landing screen;
- `Transition` - a placeholder type of screens;
- `Error` - a normal error condition;
- `Failure` - an unexpected type of problem;

The following predefined Action IDs exist:

- `Expired` - when the current time reaches Process Context `expires` timestamp;
- `Next` - a general continuation action (button);
- `Back` - a general return action (button);
- `Cancel` - a general cancellation action (button);
- `UnknownPage` - a code to inform Backend of unsupported native screen;

## 1.8. WebView Fallback Logic concept

Whenever the Application receives instruction for a Process or a Screen, which
it does not support. It must immediately inform the Backend with an `action`
call using the `UnknownPage` code.

The Backend's behavior is to request rendering of the same screen via WebView
instead of embedded code. Therefore, all applications should support WebView
rendering of pages even if those are not present in the original requirements.


# 2. Interface schema

This specs defines Backend and Device base interfaces. Those can be used either
directly or inherited for custom extensions.

## 2.1. Common UI FLow types

This is a common definition of types used in scope UI Flow interfaces.


`Iface{`

        {
            "iface" : "futoin.uiflow.types",
            "version" : "{ver}",
            "ftn3rev" : "1.8",
            "imports" : [
                "futoin.types:1.0"
            ],
            "types": {
                "ScreenID": {
                    "type": "GenericIdentifier",
                    "minlen": 1,
                    "maxlen": 64
                },
                "ProcessID": {
                    "type": "GenericIdentifier",
                    "minlen": 1,
                    "maxlen": 64
                },
                "ActionID": {
                    "type": "GenericIdentifier",
                    "minlen": 1,
                    "maxlen": 64
                },
                "GenericProperties": {
                    "type": "map",
                    "elemtype": "any"
                },
                "ProcessContext": {
                    "type": "map",
                    "fields": {
                        "lang": "FTNLocale",
                        "expires": "Timestamp",
                        "user_props": {
                            "type": "GenericProperties",
                            "optional": true
                        },
                        "process": "ProcessID",
                        "process_props": {
                            "type": "GenericProperties",
                            "optional": true
                        },
                        "screen": "ScreenID",
                        "screen_props": {
                            "type": "GenericProperties",
                            "optional": true
                        }
                    }
                }
            },
            "desc" : "FutoIn UI Flow common types"
        }

`}Iface`

## 2.2. UI FLow Backend interface

This is a base Backend iface from which custom interfaces should inherit.

`Iface{`

        {
            "iface" : "futoin.uiflow.backend",
            "version" : "{ver}",
            "ftn3rev" : "1.8",
            "imports" : [
                "futoin.uiflow.types:{ver}"
            ],
            "funcs" : {
                "launch": {
                    "params": {
                        "process_id": "ProcessID",
                        "props": "GenericProperties"
                    },
                    "result": "ProcessContext",
                    "throws": [ "UnknownProcessID" ],
                    "desc": "Request launch of a new process"
                },
                "action": {
                    "params": {
                        "process_id": "ProcessID",
                        "screen_id": "ScreenID",
                        "action_id": "ActionID",
                        "props": "GenericProperties"
                    },
                    "result": "ProcessContext",
                    "throws": [ "UnknownActionID" ],
                    "desc": "Perform navigational action in the current screen"
                }
            },
            "requires" : [
                "SecureChannel",
                "MessageSignature"
            ],
            "desc" : "FutoIn UI Flow Backend interface"
        }

`}Iface`

## 2.3. UI FLow Device interface

This is a base Device iface from which custom interfaces should inherit.

`Iface{`

        {
            "iface" : "futoin.uiflow.device",
            "version" : "{ver}",
            "ftn3rev" : "1.8",
            "imports" : [
                "futoin.uiflow.types:{ver}"
            ],
            "funcs" : {
                "context": {
                    "params": {
                        "context": "ProcessContext"
                    },
                    "desc": "Out-of-band update of the Device with new state"
                }
            },
            "requires" : [
                "SecureChannel",
                "MessageSignature"
            ],
            "desc" : "UI Flow Device interface"
        }

`}Iface`


[FTN23]: ./ftn23_if_enclave_device.md

=END OF SPEC=
