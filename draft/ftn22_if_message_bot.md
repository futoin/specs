<pre>
FTN22: FutoIn Interface - Message Bot
Version: 0.2DV
Date: 2019-11-03
Copyright: 2019 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v0.2 - 2019-11-03 - Andrey Galkin
    - NEW: server iface
    - NEW: extended with event concept
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

    .________.   .________.   ._______.   ._______.   ._______.
    |        |   |        |   |       |   |       |   |       |
    | Server |-->| Bridge |-->| FTN22 |-->| FTN22 |-->| FTN22 |
    |________|   |________|   |_______|   |_______|   |_______|
                                  \      _______ 
                                   \    |       |
                                    `-->| FTN22 |
                                        |_______|

## 2.9. Command message router

Traditional message bots support various commands of fixed format. Very often, such commands
are split by functionality into modular parts.

To support such command handling paradigm, a message router is required to listen for
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
* `#msgbot.server.{UUIDB64}` - server interfaces

## 2.11. Server interface

Server interface is expected to be based on push handler interface with additional features
to retrieve additional information needed for operation of custom business logic.

# 3. Interfaces

## 3.1. Common types

These are common types to be used in scope of other interfaces.

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
                "ExtID": {
                    "type": "string",
                    "minlen": 1,
                    "maxlen": 32
                },
                "ExtActorID": "ExtID",
                "BaseMessage": {
                    "type": "map",
                    "fields": {
                        "server": "ServerID",
                        "channel": {
                            "type": "ChannelID",
                            "optional": true
                        },
                        "payload": "MessagePayload"
                    }
                },
                "InputMessage": {
                    "type": "BaseMessage",
                    "fields": {
                        "private": "boolean",
                        "sender": "ExtActorID",
                        "ts": "MicroTimestamp",
                        "ext_id": {
                            "type": "ExtID",
                            "optional": true,
                            "desc": "Unique external message ID, if supported"
                        }
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
                },
                "EventName": {
                    "type": "string",
                    "minlen": 1,
                    "maxlen": 64
                },
                "EventData": [ "string", "map" ],
                "Event": {
                    "type": "map",
                    "fields": {
                        "server": "ServerID",
                        "channel": {
                            "type": "ChannelID",
                            "optional": true
                        },
                        "name": "EventName",
                        "data": "EventData",
                        "ts": "MicroTimestamp"
                    }
                }
            }
        }

`}Iface`

## 3.2. Reactive message handler interface

This is the base which is expected to be implemented by leaf handlers and routers.

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
                        "msg": "InputMessage"
                    },
                    "result": {
                        "rsp": "ResponsePayload"
                    }
                },
                "onEvent": {
                    "params": {
                        "evt": "Event"
                    }
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

## 3.3. Push message interface

This is message pushing interfaces to be implemented by servers and push routers.

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
                        "msg": "PushMessage"
                    },
                    "result": "boolean",
                    "throws": [
                        "UnknownServer",
                        "DeliveryFailed"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

## 3.4. Command router interface

This is extension of reactive interface to handle router registration logic.

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
                    "maxlen": 100
                },
                "EventNames": {
                    "type": "array",
                    "elemtype": "EventName",
                    "maxlen": 100
                }
            },
            "funcs" : {
                "registerHandler": {
                    "params": {
                        "ccm_name": "HandlerName",
                        "commands": "CommandPrefixes",
                        "events": "EventNames",
                        "catch_all": "boolean"
                    },
                    "result": "boolean",
                    "throws": [
                        "AlreadyRegistered",
                        "UnknownInterface"
                    ]
                },
                "unRegisterHandler": {
                    "params": {
                        "ccm_name": "HandlerName"
                    },
                    "result": "boolean",
                    "throws": [
                        "NotRegistered"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

## 3.5. Server interface

The server interface is expected to grow over time via mixins. Mixin strategy is used
to logically separate scopes of common flat interfaces.

### 3.5.1. Composite server interface

This interface should be used for registration and interaction.

`Iface{`

        {
            "iface" : "futoin.msgbot.server",
            "version" : "{ver}",
            "ftn3rev" : "1.9",
            "inherit" : "futoin.msgbot.push:{ver}",
            "types" : {
                "Flavour" : {
                    "type" : "GenericIdentifier",
                    "maxlen" : 32,
                    "desc" : "Actual actual database driver type"
                }
            },
            "funcs" : {
                "getFlavour": {
                    "result": "Flavour"
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

### 3.5.2. Native extensions

It expected that the interface provides various helpers for message and event processing.

* `helpers()` - access native helpers
* `systemIface()` - access message system interface implementation

### 3.5.3. Native helpers

Text processing API are expected to return input AS-IS, if some feature is not supported.

* `string bold(string)` - returns input wrapped in bold text markup.
* `string italic(string)` - returns input wrapped into italic text markup.
* `string color(string, hexcolor)` - returns input wrapped into RGB color markup.
* `string imgUrl(url)` - insert image by url.
* `string emoji(name)` - add named emoji markup.
* `string line()` - line break
* `string menion(ext_actor_id)` - returns mention of particular user

### 3.5.4. Member server API

`Iface{`

        {
            "iface" : "futoin.msgbot.server.members",
            "version" : "{ver}",
            "ftn3rev" : "1.9",
            "imports" : [
                "futoin.msgbot.types:{ver}"
            ],
            "types" : {
                "ExtActorList": {
                    "type": "array",
                    "elemtype": "ExtActorID",
                    "maxlen": 100
                }
            },
            "funcs" : {
                "listMembers": {
                    "params": {
                        "channel": {
                            "type": "ChannelID",
                            "default" : null
                        },
                        "start": {
                            "type": "NotNegativeInteger",
                            "default" : 0
                        }
                    },
                    "result": "ExtActorList"
                },
                "isMember": {
                    "params": {
                        "actor": "ExtActorID",
                        "channel": {
                            "type": "ChannelID",
                            "default" : null
                        }
                    },
                    "result": "boolean"
                },
                "kick": {
                    "params": {
                        "actor": "ExtActorID",
                        "reason": "MessagePayload",
                        "channel": {
                            "type": "ChannelID",
                            "default" : null
                        }
                    },
                    "result": "boolean",
                    "throws": [
                        "Failed"
                    ]
                },
                "listBanned": {
                    "params": {
                        "channel": {
                            "type": "ChannelID",
                            "default" : null
                        },
                        "start": {
                            "type": "NotNegativeInteger",
                            "default" : 0
                        }
                    },
                    "result": "ExtActorList"
                },
                "isBanned": {
                    "params": {
                        "actor": "ExtActorID",
                        "channel": {
                            "type": "ChannelID",
                            "default" : null
                        }
                    },
                    "result": "boolean"
                },
                "ban": {
                    "params": {
                        "actor": "ExtActorID",
                        "reason": "MessagePayload",
                        "channel": {
                            "type": "ChannelID",
                            "default" : null
                        }
                    },
                    "result": "boolean",
                    "throws": [
                        "Failed"
                    ]
                },
                "unBan": {
                    "params": {
                        "actor": "ExtActorID",
                        "channel": {
                            "type": "ChannelID",
                            "default" : null
                        }
                    },
                    "result": "boolean",
                    "throws": [
                        "Failed"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

=END OF SPEC=
