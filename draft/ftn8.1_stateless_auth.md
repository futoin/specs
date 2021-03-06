<pre>
FTN8.1: FutoIn Security Concept - Stateless Authentication
Version: 0.4DV
Date: 2018-05-17
Copyright: 2014-2018 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v0.3 - 2018-05-17 - Andrey Galkin
    - CHANGED: revised with implementation
* v0.2 - 2017-12-29 - Andrey Galkin
    - CHANGED: heavily revised & split into sub-specs
    - CHANGED: replaced HMAC with more generic MAC method
    - NEW: futoin.auth.stateless & futoin.auth.stateless specs
* v0.1 - 2014-06-03 - Andrey Galkin
    - Initial draft

# 1. Intro

This sub-specification of [FTN8](./ftn8_security_concept.md) covers
the simplest Stateless Authentication for Clients and Services.

The ultimate goal is to authenticate user based on local user ID
and pre-shared secret (password) without automatic Secret renewal.

The following methods are defined:

1. Clear Text
2. Simple MAC based on Secret

# 2. Concept

This scheme does no support foreign users. 

The following "sec" field definition refer to [FTN3][] request
message "Security-defined extension" element.

The Secret used in requests must be separate from all other secrets to
prevent exposure of those. It's assumed that there is a unique User
Secret per Service as Service should be able to retrieve the Secret
from AuthService for caching purposes.


## 2.1. Clear text method

Clear text directly corresponds to [HTTP Basic Authentication][http-basic-auth].

Main parameters are:

* `{user}` - local user ID
* `{secret}` - arbitrary string used for Clear Text

However, this sub-spec allows using "login:password" pairs outside of
HTTP requests headers.

**Use of this method is discouraged and should be limited to
not important functionality accessed through SecureChannel.**

### 2.1.1. Clear text request "sec" field structured format

`Schema(futoin-sec-credentials){`

    {
        "title" : "FutoIn 'sec' field - Credentials",
        "type" : "object",
        "additionalProperties" : false,
        "required" : [ "user" ],
        "properties" : {
            "user" : {
                "type" : "string",
                "description" : "Unique user identification"
            },
            "secret" : {
                "type" : "string",
                "description" : "Any type of secret, typically password"
            }
        }
    }

`}Schema`

### 2.1.2. Clear text request "sec" field format as string

String representation format is `"{user}:{secret}"` without brackets. Such
format is size efficient for transmission.

### 2.1.3. Clear text response "sec" field

The field must not be present as there is no point for that.

### 2.1.4. Clear text security level

`SafeOps` security level must be assigned.


## 2.2. Simple MAC method

Please refer to main [FTN8][] spec for details of generation and validation.

Main parameters are:

* `{user}` - local user ID,
* `{algo}` - MAC algorithm to use,
* `{sig}` - actual MAC value encoded as [base64][] string with or without trailing padding.

The method has serious advantages over clear text method:

* Shared Secret does not need to be transmitted in messages.
* Both request and response can be signed to protect from external modifications.

There are still some problems:

* Insecure manual key exchange
* Once Secret is bruteforced, it's easy to fake any messages.
* The same message can be easily replayed, but protocols should be designed the way
    which minimizes replay issues (e.g. using transaction IDs).
* No key updates and no derived keys are used.

However, it's still relatively simple to implement with meaningful advantages.

### 2.2.1. Simple MAC request "sec" field structured format

`Schema(futoin-sec-simple-mac){`

    {
        "title" : "FutoIn 'sec' field - Simple MAC",
        "type" : "object",
        "additionalProperties" : false,
        "required" : [ "user", "algo", "sig" ],
        "properties" : {
            "user" : {
                "type" : "string",
                "description" : "Unique user identification"
            },
            "algo" : {
                "type" : "string",
                "description" : "MAC algo name as defined in FTN8"
            },
            "sig" : {
                "type" : "string",
                "description" : "Base64 encoded MAC"
            }
        }
    }

`}Schema`

### 2.2.2. Simple MAC request "sec" field string format

Preferred for message size reduction.

```
    "-smac:{user}:{algo}:{sig}"
```

### 2.2.3. Simple MAC response "sec" field

Response must be authenticated by the same Secret and the same hash algorithm
as used for request signing. Only signature has to be sent.

### 2.2.4. Simple MAC security level

`PrivilegedOps` security level must be assigned.

## 2.3. Events

### 2.3.1. New secret set events

* `STLS_NEW` - new stateless secret
    * `user_id` - local user ID
    * `service_id` - local service ID
    * `key_id` - secure vault key identifier
    * `for_mac` - if MAC secret
* `STLS_DEL` - stateless secret is removed
    * `user_id` - local user ID
    * `service_id` - local service ID
    * `key_id` - secure vault key identifier
    * `for_mac` - if MAC secret

## 2.4. Backward compatibility to historical "#basicauth" interface

For many years, a temporary solution similar to this spec was used. The
major difference was to use classical usernames instead of local user IDs.

To allow smooth transition, there should be optional implementation-defined
way to map legacy usernames to local user IDs.

# 3. Interface

## 3.1. Message authentication

The interface is used only to process stateless authentication requests.
It is designed the way when MAC secret is always kept inside AuthService to
minimize risk of exposure.

`Iface{`

    {
        "iface" : "futoin.auth.stateless",
        "version" : "{ver}",
        "ftn3rev" : "1.9",
        "imports" : [
            "futoin.ping:1.0",
            "futoin.auth.types:{ver}"
        ],
        "types" : {
            "ClearSecField" : {
                "type" : "map",
                "fields" : {
                    "user" : "LocalUserID",
                    "secret" : "Password"
                }
            },
            "MACSecField" : {
                "type" : "map",
                "fields" : {
                    "user" : "LocalUserID",
                    "algo" : "MACAlgo",
                    "sig" : "MACValue"
                }
            }
        },
        "funcs" : {
            "checkClear" : {
                "params" : {
                    "sec" : "ClearSecField",
                    "source" : "ClientFingerprints"
                },
                "result" : "AuthInfo",
                "throws" : [
                    "SecurityError"
                ],
                "seclvl" : "SafeOps"
            },
            "checkMAC" : {
                "params" : {
                    "base" : "MACBase",
                    "sec" : "MACSecField",
                    "source" : "ClientFingerprints"
                },
                "result" : "AuthInfo",
                "throws" : [
                    "SecurityError"
                ],
                "seclvl" : "PrivilegedOps"
            },
            "genMAC" : {
                "params" : {
                    "base" : "MACBase",
                    "reqsec" : "MACSecField"
                },
                "result" : "MACValue",
                "throws" : [
                    "SecurityError"
                ],
                "seclvl" : "PrivilegedOps"
            },
            "getMACSecret" : {
                "params" : {
                    "user" : "LocalUserID"
                },
                "result" : "MACKey",
                "throws" : [
                    "UnknownUser",
                    "NotSet"
                ],
                "desc" : "For internal caching purposes",
                "seclvl" : "PrivilegedOps"
            }
        },
        "requires" : [
            "SecureChannel",
            "MessageSignature",
            "BinaryData"
        ]
    }

`}Iface`

## 3.2. Management

This one is complementary to "futoin.auth.manage" iface.

`Iface{`

    {
        "iface" : "futoin.auth.stateless.manage",
        "version" : "{ver}",
        "ftn3rev" : "1.9",
        "imports" : [
            "futoin.ping:1.0",
            "futoin.auth.types:{ver}"
        ],
        "funcs" : {
            "genNewSecret" : {
                "params" : {
                    "user" : "LocalUserID",
                    "service" : "LocalUserID",
                    "for_mac" : "boolean"
                },
                "result" : "StatelessSecret",
                "throws" : [
                    "UnknownUser"
                ],
                "seclvl" : "System"
            },
            "getSecret" : {
                "params" : {
                    "user" : "LocalUserID",
                    "service" : "LocalUserID",
                    "for_mac" : "boolean"
                },
                "result" : "StatelessSecret",
                "throws" : [
                    "UnknownUser",
                    "NotSet"
                ],
                "seclvl" : "System"
            },
            "removeSecret" : {
                "params" : {
                    "user" : "LocalUserID",
                    "service" : "LocalUserID",
                    "for_mac" : "boolean"
                },
                "result" : "boolean",
                "throws" : [
                    "UnknownUser"
                ],
                "seclvl" : "System"
            }
        },
        "requires" : [
            "SecureChannel",
            "MessageSignature"
        ]
    }

`}Iface`


[http-basic-auth]: https://tools.ietf.org/html/rfc1945#section-11
[FTN3]: ./ftn3_iface_definition.md
[FTN8]: ./ftn8_security_concept.md
[base64]: http://www.ietf.org/rfc/rfc2045.txt "RFC2045 section 6.8"

=END OF SPEC=
