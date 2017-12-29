<pre>
FTN8.1: FutoIn Security Concept - Stateless Authentication
Version: 0.2DV
Date: 2017-12-27
Copyright: 2014-2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v0.2 - 2017-12-27 - Andrey Galkin
    - CHANGED: heavily revised & split into sub-specs
    - CHANGED: replaced HMAC with more generic MAC method
* v0.1 - 2014-06-03 - Andrey Galkin
    - Initial draft

# 1. Intro

The ultimate goal is to authenticate user based on local user ID
and pre-shared secret (password) without automatic Secret renewal.

The following methods are defined:

1. Clear Text
2. Simple MAC based on Secret

# 2. Concept

This scheme does no support foreign users. 

The following "sec" field definition refer to [FTN3][] request
message "Security-defined extension" element.


## 2.1. Clear text method

Clear text directly corresponds to [HTTP Basic Authentication][http-basic-auth].

Main parameters are:

* `{user}` - local user ID
* `{secret}` - arbitrary string used for Clear Text

However, this sub-spec allows using "login:password" pairs outside of
HTTP requests headers.

**Use of this method is discouraged and should be limited to
not important functionality accessed through SecureChannel.**

The Secret used in clear text requests must be separate from all other
secrets to provent exposure of those.

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

`Info` authentication level must be assigned.


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

* Once Secret is bruteforced, it easy to fake any messages.
* The same message can be easily replayed, but protocols should be designed the way
    which minimizes replay issues (e.g. using transaction IDs).

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

Prefered for message size reduction.

```
    "-mac:{user}:{algo}:{sig}"
```

### 2.2.3. Simple MAC response "sec" field

Response must be authenticated by the same Secret and the same hash algorithm
as used for request signing.

### 2.2.4. Simple MAC security level

`SafeOps` authentication level must be assigned.


# 3. Interface

## 3.1. Request authentication

The interface is used only to process stateless authentication requests.
It is designed the way when MAC secret is always kept inside AuthService to
minimize risk of exposure.

`Iface{`

        {
            "iface" : "futoin.auth.stateless",
            "version" : "{ver}",
            "ftn3rev" : "1.8",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.auth.types:{ver}"
            ],
            "types" : {
                "ClearSecField" : {
                    "type" : "map",
                    "fields" : {
                        "user" : "LocalUserID",
                        "secret" : "ClearSecret"
                    }
                },
                "MACSecField" : {
                    "type" : "map",
                    "fields" : {
                        "user" : "LocalUserID",
                        "algo" : "MACAlgo",
                        "sig" : "MACValue"
                    }
                },
                "MessageAuth" : {
                    "type" : "map",
                    "fields" : {
                        "local_id" : "LocalUserID",
                        "global_id" : "GlobalUserID"
                    }
                }
            },
            "funcs" : {
                "clearAuth" : {
                    "params" : {
                        "sec" : "ClearSecField"
                    },
                    "result" : "MessageAuth",
                    "throws" : [
                        "SecurityError"
                    ]
                },
                "checkMAC" : {
                    "params" : {
                        "base" : "MACBase",
                        "sec" : "MACSecField"
                    },
                    "result" : "MessageAuth",
                    "throws" : [
                        "SecurityError"
                    ]
                },
                "genMAC" : {
                    "params" : {
                        "base" : "MACBase",
                        "user" : "LocalUserID",
                        "algo" : "MACAlgo"
                    },
                    "result" : "MACSecField",
                    "throws" : [
                        "SecurityError"
                    ]
                }
            },
            "requires" : [
                "SecureChannel"
            ]
        }

`}Iface`

## 3.2. User management

`Iface{`

        {
            "iface" : "futoin.auth.stateless.manage",
            "version" : "{ver}",
            "ftn3rev" : "1.8",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.auth.types:{ver}"
            ],
            "funcs" : {
                "setup" : {
                    "params" : {
                        "domain" : "Domain",
                        "clear_auth" : {
                            "type" : "boolean",
                            "default" : false
                        },
                        "mac_auth" : {
                            "type" : "boolean",
                            "default" : true
                        }
                    }
                },
                "ensureUser" : {
                    "params" : {
                        "user" : "LocalUser",
                        "global_id" : {
                            "type": "GlobalUserID",
                            "default" : null,
                            "desc" : "Defaults to auto-generated"
                        }
                    },
                    "result" : "LocalUserID",
                    "throws" : [
                        "GlobalUserIDMismatch"
                    ]
                },
                "setClearSecret" : {
                    "params" : {
                        "user" : "LocalUser",
                        "secret" : {
                            "type" : "ClearSecret",
                            "default" : null
                        }
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownUser"
                    ]
                },
                "getClearSecret" : {
                    "params" : {
                        "user" : "LocalUser"
                    },
                    "result" : "ClearSecret",
                    "throws" : [
                        "UnknownUser",
                        "NotSet"
                    ]
                },
                "setMACSecret" : {
                    "params" : {
                        "user" : "LocalUser",
                        "secret" : {
                            "type" : "MACSecret",
                            "default" : null
                        }
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownUser"
                    ]
                },
                "getMACSecret" : {
                    "params" : {
                        "user" : "LocalUser"
                    },
                    "result" : "MACSecret",
                    "throws" : [
                        "UnknownUser",
                        "NotSet"
                    ]
                }
            },
            "requires" : [
                "SecureChannel"
            ]
        }

`}Iface`



[http-basic-auth]: https://tools.ietf.org/html/rfc1945#section-11
[FTN3]: ./ftn3_iface_definition.md
[FTN8]: ./ftn8_security_concept.md
[base64]: http://www.ietf.org/rfc/rfc2045.txt "RFC2045 section 6.8"

=END OF SPEC=
