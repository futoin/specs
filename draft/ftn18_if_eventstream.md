<pre>
FTN18: FutoIn Interface - Event Stream
Version: 1.0DV
Date: 2017-08-27
Copyright: 2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* DV - 2017-08-27 - Andrey Galkin
    - Initial draft

# 1. Intro

Event stream or event log is a know pattern to distribute state asynchronously.
Most database system and filesystems have some sort of data modification logs,
modern version control systems are stream of changes and even
cryptocurrency blockchains are also ordered streams of events.

This spec does not cover all possible cases and is focused on distributing
abstract information system state in large heterogeneous ad-hoc systems.

There are cases like financial transactions which must be distributed reliable way
and there are cases where loss of data is desired in favor of up to date like
live events.

# 2. Concept

Concept is split into to separate parts: event generation and event consumption.

## 2.1. Event generation

One kind of events is tighly bound to associated internal action like financial
transaction operation. Such events must be processed reliable transactional way
in scope of data modification operation. Actual implementation is very specific
to target database type. However, recommended implementation guidelines are provided.

Another kind of events is related to external action (event). Such events can be
injected through standard interface, if mutliple delivery of same event is not
a requirement. Behind such interface a typical message broker can be used with
different properties of durability.

It's assumed that event generator never makes outgoing connections to push events.
All event pushes must be done through BiDirectional communication channels. This 
significantly simplifies overall setup and access control when diffirent parts
of the system operate in dedicated security domains.

### 2.1.1. Event ID

There must be an increasing positive 64-bit integer event ID per stream. It's
possible to have event ID gaps. All extra identification like UUID can be part
of event data, but it must not be used in scope of this spec.

### 2.1.2. Event attributes:

1. Event ID - as defined above
2. Event Type
    - always represented as string, but can be stored as enumerated integer
    - string limit 1 to 16 characters
3. Event Data - arbitrary JSON-encodable data

## 2.2. Event consumption

Each consumer with reliable delivery of events must be registered on generating peer.
Unreliable live event consumer must not register.

Two well known approaches for event delivery are assumed: polling and pushing.

Generator does not care about which approach consumer uses to retrieve events.
Consumer may even use both approaches interchangeably - for example, to skip
some event data in recovery through polling with not really processed event ID.

### 2.2.1. polling

Polling is the most simple one. On poll request, consumer provides the last known
event ID. Generator sends an ordered list of new events since specified event ID.

There is a limit of events in single response. It may lead to throughput bottlenecks.
Then pushing approach must be used in particular case.

It is consumer's responsibility to add reasonable adaptive delays between calls
to prevent empty or not "filled enough" request-response loops.

In reliable delivery cases, generator uses provided ID for old event discarding
from active data area.

### 2.2.2. pushing

This is more efficient, but more difficult to implement pattern from typical client-server
perspective as BiDirectional channel is required as stated above. Each consumer
must still connect to generator and make initial call to start receiving events
through the opened BiDirectional channel. 

It's assumed that events are grouped with reasonable maximum delay and send to consumer.
Consumer responses with success only after events are reliably scheduled for internal processing.

For efficent throughput, generator may send many event groups in parallel. It is consumer's
responsibility to process events in proper order. Each request must have sequence ID
hint for that purpose.

### 2.2.3. filtering

In large systems, event consumers may need to process only a limited subset of
all event types. It's not efficent to send all events to all consumers. Therefore,
it should be possible to select required types of events at consumer poll or
push request time.

For security reasons, actual implementation may apply additional filter logic based on
actual event data.

Generator is responsible for event filterig. That also means, that possible skipped events
must be accounted in scope of operation. Generator is allowed to assume that skipped events
can be marked as delivered.

### 2.2.4. consumer identification

Primary identification of peer is out of scope and should be covered in
[FTN8: Security Concept](./ftn8\_security\_concept.md).

However, a single peer from security concept may have different components which 
process different parts of event stream. Therefore, extra identification of such
component is supported.

So, consumer is represented with tuple of local user ID as defined in FTN8 and
component name.

A special "LIVE" component is reserved for live streams. It's not allowed to register
consumers with such component.

### 2.2.5. Race conditions of consumer requests

Consumer is responsible to ensure there is only one request.


## 2.3. Extra large and long running systems

### 2.3.1. Event archiving or discarding

For efficiency and reliability of operation active data needs to be kept small enough.
Definition of "small" is very case-specific, but almost always there is a fast storage
like RAM or high speed database and slower larger one like persistent memory or
data warehouse.

Event generator should keep event stream in active data area until the last registred
consumer reliably reads it.

If event stream history is important and must be persistent then event stream is continuously
moved to persistent storage area. Persistent storage area is seen as one of consumers
requiring reliable delivery.

If the above requirements are met then events can be discarded from active data area
to minimize its size.

### 2.3.2. Use of message brokers

Of course, internal design may have different approaches and include well known message
broker implementations, but integration points must not depend on implementation-specific
interface. Therefore, there must be a thin interface layer based on this FutoIn spec.

### 2.3.3. Horizontal scaling

Scalability planning of different components of heterogeneous systems must avoid
bottlenecks like single event stream for whole system. Each component should allow
partitioning to allow horizontal scaling. Related peer component may paritition
themselves even further or aggregate depending on load characteristics of each.

In general, it should be possible to aggregate partitioned event streams into a new
stream with new event IDs, if there is any practical justification. However,
each peer must clearly understand that different sets of event IDs are used.

### 2.3.4. Event storage format

Even though interface expects arbitrary event storage, actual implementation may have
tailored storage format for each type of event, but it must be absolutely hidden
for interface.


# 3. Interface

## 3.1. Common types

`Iface{`

        {
            "iface" : "futoin.evt.types",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "types" : {
                "EventID" : {
                    "type" : "string",
                    "regex" : "^[1-9][0-9]{0,17}$",
                    "desc" : "1-999999999999999999 for now"
                },
                "EventType" : {
                    "type" : "string",
                    "regex" : "^[A-Z_]{1,16}$"
                },
                "EventData" : "any",
                "EventTimestamp" : {
                    "type" : "string",
                    "regex": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"
                },
                "Event" : {
                    "type" : "map",
                    "fields" : {
                        "id" : "EventID",
                        "type" : "EventType",
                        "data" : "EventData",
                        "ts" : "EventTimestamp"
                    }
                },
                "EventList" : {
                    "type" : "array",
                    "elemtype" : "Event",
                    "maxlen" : 1000
                },
                "EventTypes" : {
                    "type" : "array",
                    "elemtype" : "EventType"
                },
                "ConsumerComponent" : {
                    "type" : "string",
                    "regex" : "^[A-Za-z0-9_]{1,16}$",
                    "desc" : "Identify component of consumer's side"
                }
            }
        }

`}Iface`

## 3.2. Generator interface

`Iface{`

        {
            "iface" : "futoin.evt.gen",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.evt.types:1.0",
                "futoin.ping:1.0"
            ],
            "funcs" : {
                "addEvent" : {
                    "params" : {
                        "type" : "EventType",
                        "data" : "EventData"
                    },
                    "result" : "EventID"
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

### 3.2.1. Native extension

* void addXferEvent(XferBuilder, type, data, table=IMPL_DEFINED)

## 3.3. Consumer interface

### 3.3.1. Base

Base interface to use for registration and polling purposes.

Registration can be repeated to modify list of events in interest. It's strongly
suggested to make registration call on consumerr startup, if it's
software version changes as a general convention for plug & play approach.

`Iface{`

        {
            "iface" : "futoin.evt.poll",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.evt.types:1.0",
                "futoin.ping:1.0"
            ],
            "funcs" : {
                "registerConsumer" : {
                    "params" : {
                        "component" : "ConsumerComponent"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "LiveNotAllowed"
                    ]
                },
                "pollEvents" : {
                    "params" : {
                        "component" : "ConsumerComponent",
                        "last_id" : {
                            "type": "EventID",
                            "default": null
                        },
                        "want" : {
                            "type": "EventTypes",
                            "default": null
                        }
                    },
                    "result" : "EventList",
                    "throws" : [
                        "NotRegistered"
                    ]
                }
            }
        }

`}Iface`

### 3.3.2. Bi-Directional

This interface extends the base one to provide Bi-Directional channel features.
As stated in the concept, event generator does not make outgoing connections
for event delivery.

`Iface{`

        {
            "iface" : "futoin.evt.push",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "inherit" : "futoin.evt.poll:1.0",
            "funcs" : {
                "readyToReceive" : {
                    "params" : {
                        "component" : "ConsumerComponent",
                        "want" : {
                            "type": "EventTypes",
                            "default": null
                        }
                    },
                    "result" : "boolean",
                    "desc" : "Inform generator to start pushing events",
                    "throws" : [
                        "NotRegistered"
                    ]
                }
            },
            "requires" : [ "BiDirectChannel" ]
        }

`}Iface`

### 3.3.3. Consumer callback

This interface must be available on initiating peer of bi-directional communication.

`Iface{`

        {
            "iface" : "futoin.evt.receiver",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.evt.types:1.0"
            ],
            "types" : {
                "SequenceID" : {
                    "type" : "integer",
                    "min" : 0
                }
            },
            "funcs" : {
                "onEvents" : {
                    "params" : {
                        "seq" : "SequenceID",
                        "events" : "EventList"
                    },
                    "result" : "boolean"
                }
            },
            "requires" : [ "AllowAnonymous" ]
        }

`}Iface`

=END OF SPEC=
