<pre>
FTN23: FutoIn Enclave Device
Version: 1.0DV
Date: 2026-07-09
Copyright: 2026 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>


# CHANGES

* v1.0 - 2026-07-09 initial draft

# 1. Concept

This specification is an answer for a general pattern seen in applications and
devices which perform certain security feature, but execute in hostile and/or
untrusted environment. Hence, the "enclave" name is defined for such pattern.

Unlike different type of communication patterns the devices are not pre-enrolled
into the system with proper key management scheme. Therefore, each instance
starts with roughly the same shared obscure secrets embedded in the binary code.

The goal is to establish a bidirectional communication channel where each
instance of an Enclave Device uniquely identifies itself in the system and
provides a foundation to employ various techniques of device attestation and
dynamic security to prevent potential attackers of spoofing authentic operation
of such part of a complex system.

## 1.1. Definitions

- **Backend** - the part of the systems which operates in controlled
  environment.
- **Enclave** - a mobile or web application, and an embedded device operating in
  foreign, potentially hostile, environment under third-party control.

## 1.1. Communication Channel

It is required that the Enclave establishes a cryptographically secure
bidirectional communication channel. A strong suggested is the universal
[WebSocket][] protocol.

As an extra security measure the Enclave should use custom pinning of backend's 
public key, preshared secrets as necessary, and [White-box cryptography][] to
embed and rotate client-side cryptographic secrets obscure and difficult to
reverse engineer way.

## 1.2. Unique Identification of Enclave Instance

At very minimum each Enclave should generate a 128-bit Device ID or larger
unique number and store that as persistently as possible upon the first startup.

Additionally, execution environment specific strong cryptography facilities
should be used to create asymmetric cryptographic key pair for each outgoing
message signing with clear binding to host environment.

Upon every Enclave startup another unique ID must be generated to identify the
current instance either it is a binary application or a web browser tab.

## 1.3. Time Synchronization

Dynamic protection and attestation requires relatively precise time
synchronization with a reasonable time drift limit to prevent replay attacks
and other type of spoofing.

The Backend should reject Enclave communication channel registration, if the
time drift is above its custom configurable threshold, which can be as low as a
few milliseconds. A couple of minutes is a more realistic scenario in case of
manual time synchronization.

## 1.4. Attestation Requests

Modern device attestation employs various techniques, including runtime checks
embedded in the downloadable software, behavior analysis and Backend-driven
attestation-related requests. Such requests are out of scope of this
specification.

However, some of passed parameters like SessionID and DateTime facilitate
certain detection techniques.

## 1.5. Deterministic Message Multiplexing

The sequence of actions (messages), their timing, timing of responses and
sequential order aid behavioral analysis. Independent REST or similar requests
affect quality of such analysis techniques and lower their precision.

Strict ordering of messages with general FutoIn-based ordered message IDs also
add additional roadblocks for unsolicited request injection on behalf of
an authentic Enclave Device.

## 1.6. Protocol Pattern

Upon startup, Enclave Devices immediately establish a bidirectional channel. Any
errors related to transport security or time synchronization should be handled
implementation-defined way, which prevents further operations as general rule.
Some offline functionality may still be provided, if the problem is network
communication.

Once the channel is established, all other message exchange should happen only
through such channel regardless if messages are under FutoIn-based specification
or using any foreign format.

## 1.7. Message Signing

It is highly encouraged for implementation to use custom message signing for
messages inside such communication channel.

One of possible recommendations is use of the standard FutoIn message `sec`
field with either custom format or FTN8 Security Concept HMAC signing.

## 1.8. Backend Commands

Despite the attestation-related queries, there a few predefined common commands
which Backend may issue and the Enclave must obey.

Backend should be able to request the Enclave to reestablish the channel
graceful way to minimize network error-related timeouts and other unexpected
delays.

Backend should be able to request the Enclave to wipe out all stored data,
except for the device ID. This can be done both as security mitigation and
as casual support activities.

## 1.9. Ping-Pong Interface

Both ends of the communication channel should support standalone
*FTN4: FutoIn Interface - Ping-Pong*.

# 2. Interface schema

This specs defines Backend and Device base interfaces. Those can be used either
directly or inherited for custom extensions.

## 2.1. Enclave Backend interface

This is a base Backend iface from which custom interfaces should inherit.

`Iface{`

        {
            "iface" : "futoin.enclave.backend",
            "version" : "{ver}",
            "ftn3rev" : "1.8",
            "imports" : [
                "futoin.types:1.0"
            ],
            "types": {
                "DeviceID": {
                    "type": "UUIDB64",
                    "desc": "Enclave-generated Base64-encoded UUID of the device"
                },
                "InstanceID": {
                    "type": "UUIDB64",
                    "desc": "Enclave-generated Base64-encoded UUID of the current startup"
                },
                "PublicKey": {
                    "type": "Base64",
                    "minlen": 22,
                    "maxlen": 128,
                    "desc": "Base64-encoded implementation-defined public key"
                },
                "SessionID": {
                    "type": "GenericIdentifier",
                    "maxlen": 64
                },
                "HelloResponse": {
                    "type": "map",
                    "fields": {
                        "sess_id": "SessionID",
                        "pub_key": {
                            "type": "PublicKey",
                            "desc": "Backend-generated PublicKey"
                        }
                    }
                }
            },
            "funcs" : {
                "hello": {
                    "params": {
                        "device_id": "DeviceID",
                        "instance_id": "InstanceID",
                        "pub_key": {
                            "type": "PublicKey",
                            "desc": "Enclave-generated execution environment-bound PublicKey"
                        },
                        "prev_sess_id": {
                            "type": "SessionID",
                            "desc": "Previous SessionID, if known",
                            "default": null
                        },
                        "ts": "MicroTimestamp"
                    },
                    "result": "HelloResponse",
                    "throws": [
                        "TimeDrift"
                    ],
                    "desc": "Initialize the communication channel"
                }
            },
            "requires" : [
                "AllowAnonymous",
                "SecureChannel"
            ],
            "desc" : "Enclave Backend interface"
        }

`}Iface`

## 2.2. Enclave Device interface

This is a base Device iface from which custom interfaces should inherit.

`Iface{`

        {
            "iface" : "futoin.enclave.device",
            "version" : "{ver}",
            "ftn3rev" : "1.8",
            "funcs" : {
                "shutdown": {
                    "desc": "Informs Enclave of graceful shutdown of the channel"
                },
                "wipeOut": {
                    "result": "boolean",
                    "desc": "Request Enclave to wipe out all its stored data"
                }
            },
            "requires" : [
                "AllowAnonymous",
                "SecureChannel",
                "MessageSignature"
            ],
            "desc" : "Enclave Device interface"
        }

`}Iface`


[WebSocket]: https://datatracker.ietf.org/doc/html/rfc6455
[White-box cryptography]: https://en.wikipedia.org/wiki/White-box_cryptography

=END OF SPEC=
