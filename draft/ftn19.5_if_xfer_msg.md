<pre>
FTN19.5: FutoIn Interface - Transaction Engine - Messages
Version: 1.0DV
Date: 2017-12-24
Copyright: 2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* DV - 2017-12-24 - Andrey Galkin
    - Split into sub-specs
* DV - 2017-08-27 - Andrey Galkin
    - Initial draft

# 1. Intro

This is sub-specification of main [FTN19: Transaction Engine](./ftn19\_if\_xfer\_engine.md).

# 2. Concept (Messages)

Due to security and traceability considerations use of third-party communication channels
may be undesired. A basic plain text in-system messaging feature is required for
operator <-> user communication in scope of transaction processing.

All other types of communications must be handled externally.

# 3. Interface (Messages)

The interface is assumed to be a reliable channel for plain email-like communication
between user and system represented by operators. It is not a peer-to-peer messaging system.

`Iface{`

        {
            "iface" : "futoin.xfer.message",
            "version" : "{ver}",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:{ver}"
            ],
            "types" : {
                "ExtMessageID" : "XferExtID",
                "MessageID" : "XferID",
                "MessageSubject" : {
                    "type" : "string",
                    "minlen" : 1,
                    "maxlen" : 64
                },
                "MessageBody" : {
                    "type" : "string",
                    "minlen" : 1,
                    "maxlen" : 3000
                },
                "MessageData" : {
                    "type" : "map",
                    "fields" : {
                        "subject" : "MessageSubject",
                        "body" : "MessageBody",
                        "other" : {
                            "type" : "map",
                            "optional" : true
                        }
                    }
                }
            },
            "funcs" : {
                "userSend" : {
                    "params" : {
                        "sender" : "AccountHolderID",
                        "ext_id" : "ExtMessageID",
                        "orig_ts" : "XferTimestamp",
                        "data" : "MessageData",
                        "rel_id" : {
                            "type" : "MessageID",
                            "default" : null
                        }
                    },
                    "result" : "MessageID",
                    "throws" : [
                        "LimitReject",
                        "OriginalTooOld",
                        "OriginalMismatch",
                        "UnknownRelID"
                    ]
                },
                "systemSend" : {
                    "params" : {
                        "sender" : "AccountHolderID",
                        "recipient" : "AccountHolderID",
                        "ext_id" : "ExtMessageID",
                        "orig_ts" : "XferTimestamp",
                        "data" : "MessageData",
                        "rel_id" : {
                            "type" : "MessageID",
                            "default" : null
                        }
                    },
                    "result" : "MessageID",
                    "throws" : [
                        "LimitReject",
                        "OriginalTooOld",
                        "OriginalMismatch",
                        "UnknownRelID"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

### 3.7.1. Events

* MSG - on new message
* MSG_ERR - on message error

=END OF SPEC=
