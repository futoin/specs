<pre>
FTN22: FutoIn Interface - Message Bot
Version: 0.1DV
Date: 2019-11-01
Copyright: 2019 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v0.1 - 2019-11-01 - Andrey Galkin
    - Initial draft

# 1. Intro

There are many modern message exchange systems with quite unique features.
It is common to extend user service with intelligent agent (bot) functionality.

This specification is focused on generic message handling inside such service.

Text message processing is assumed. Speech recognition and synthesis is expected
to be communication channel (de-)modulation which ends in processing of textual
representation.

# 2. Concept

## 2.1. Entity types

A typical message exchange system has the following entity types:

* **Actors** - users and bots which can send and receive messages from other Actors.
* **Channels** - peer-to-peer or peer-to-many communication for Actors.
* **Server** - a collection of Channels which possibly has administrative meaning.

## 2.2. Entity identification

It is expected that Servers and Channels are identified by UUIDv4 which should be
mapped by adapter interfaces reliable safe way. That allows predictable internal
database schemes.

However, such approach is technically excessive for Actors. Therefore, message system
native unique identifier is expected to be used as arbitrary string of characters.

## 2.3. Reactive message handling

It is expected that bot reacts to other Actors messages. Therefore, a generic interface
for message handling is expected to receive input message as parameter and return response
message as result variable. For most cases, that should greatly simplify implementation.

## 2.4. Unsolicited message push

Sometimes, bot service needs to push additional messages as reaction to some internal event, or
as side reaction to message on a different communication channel.

Such message processing is expected to be one-way. The push interface must be available through
associated [FTN7 CCM](./ftn7\_iface\_invoker\_concept.md) instance.

## 2.5. Message system integration

It is expected that various bridge and adapter implementations exist to connect
custom message system protocol to the interface of this specification.

Such implementation is responsible for efficient entitity identifier mapping, and for proper
slicing of response messages to match any limits, including single message size and message throttling.

## 2.6. Message system helpers

Most likely, each message system has unique rich text formatting. It is assumed that universal
native API helpers are provided similar to [FTN17 Database concept](./ftn17\_if\_database.md).

## 2.7. Message representation

Every message is represented by related server ID, optional channel ID for group communication and payload.

Incoming messages has additional sender and timestamp fields.

Reactive message is just a payload to be sent into the source channel/private chat. Other fields
are deduced from the incoming message.

Push message may have optional recipient for private message.

## 2.8. Chaining of message handlers

It is expected that actual bot implementation uses middleware chain pattern for separation
of concerns during message processing. Each element is expected to have a single reactive
message interface.

By design, the next chain must be selected via associated CCM instead of direct native object
references or pointers to follow FutoIn microservice pattern.

```
     ________     ________     _______     _______     _______
    |        |   |        |   |       |   |       |   |       |
    | Server |-->| Bridge |-->| FTN22 |-->| FTN22 |-->| FTN22 |
    |________|   |________|   |_______|   |_______|   |_______|
                                  \      _______ 
                                   \    |       |
                                    `-->| FTN22 |
                                        |_______|

```

## 2.9. Command message router

Traditional message bots support various commands of fixed format. Very often, such commands
are split by functionality into modular parts.

To support such command handling paradigm, a special message router is required to listen for
specially prefixed messages and route them into related message handler parts.

Custom extensions of such routers should be able to enforce access control for the commands. It should
be possible to create several message routers in general middleware chain way.

For efficiency and flexibility reasons, routed message must be stripped from a command command prefix.

Messages routed by prefix are expected to be sent only to respected handlers.
There must be support for traditional catch all handlers.

## 2.10. CCM interface naming plan

* `#msgbot.` - general prefix for interfaces in scope of this specification
* `#msgbot.router` - main reactive message handler
* `#msgbot.push` - main push message handler
* `#msgbot.system.{UUIDB64}` - system interfaces

# 3. Interfaces

## 3.1. Common types

`Iface{`

        {
            "iface" : "futoin.msgbot.types",
            "version" : "{ver}",
            "ftn3rev" : "1.9",
            "imports" : [
                "futoin.types:1.0"
            ],
            "types" : {
                "ServerID": "UUIDB64",
                "ChannelID": "UUIDB64",
                "MessagePayload": {
                    "type": "string",
                    "maxlen": 8192
                },
                "ExtActorID": {
                    "type": "string",
                    "maxlen": 32
                },
                "BaseMessage": {
                    "type": "map",
                    "fields": {
                        "server": "ServerID",
                        "channel": {
                            "type": "ChannelID",
                            "optional": true,
                            "desc": "Private message, if empty"
                        },
                        "payload": "MessagePayload"
                    }
                },
                "InputMessage": {
                    "type": "BaseMessage",
                    "fields": {
                        "sender": "ExtActorID",
                        "ts": "MicroTimestamp"
                    }
                },
                "ResponsePayload": "MessagePayload",
                "PushMessage": {
                    "type": "BaseMessage",
                    "fields": {
                        "recipient": {
                            "type": "ExtActorID",
                            "optional": true,
                            "desc": "For private message, .channel must be obeyed as well"
                        }
                    }
                }
            }
        }

`}Iface`

## 3.2. Reactive message handler interfaces

`Iface{`

        {
            "iface" : "futoin.msgbot.react",
            "version" : "{ver}",
            "ftn3rev" : "1.9",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.msgbot.types:{ver}"
            ],
            "funcs" : {
                "onMessage": {
                    "params": {
                        "msg": "PushMessage"
                    },
                    "result": {
                        "rsp": "ResponsePayload"
                    }
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

## 3.3. Push message interface

`Iface{`

        {
            "iface" : "futoin.msgbot.push",
            "version" : "{ver}",
            "ftn3rev" : "1.9",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.msgbot.types:{ver}"
            ],
            "funcs" : {
                "pushMessage": {
                    "params": {
                        "msg": "InputMessage"
                    },
                    "result": "boolean",
                    "throws": [
                        "DeliveryFailed"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

## 3.4. Command router

`Iface{`

        {
            "iface" : "futoin.msgbot.router",
            "version" : "{ver}",
            "ftn3rev" : "1.9",
            "inherit" : "futoin.msgbot.react:{ver}",
            "types" : {
                "HandlerName": {
                    "type": "GenericIdentifier",
                    "maxlen": 32
                },
                "CommandPrefix": {
                    "type": "string",
                    "maxlen": 32
                },
                "CommandPrefixes": {
                    "type": "array",
                    "elemtype": "CommandPrefix",
                    "minlen": 1,
                    "maxlen": 100
                }
            },
            "funcs" : {
                "registerHandler": {
                    "params": {
                        "ccm_name": "HandlerName",
                        "commands": "CommandPrefixes"
                    },
                    "result": "boolean",
                    "throws": [
                        "AlreadyRegistered"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`


=END OF SPEC=
