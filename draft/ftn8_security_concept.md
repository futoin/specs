<pre>
FTN3: FutoIn Security Concept
Version: 0.DV
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# Warning

This document is not actually a specification, but more an overview as it requires
a LOT of polishing first.

*Unfortunately. At the moment of writing this specification, the author
knows quite little about Security to judge the strength of proposed algorithms.
Every single part of that requires deep analysis of experts.*


# 1. Intro

Security concept is required to build a unified authentication and
authorization model across security domains with separate control
in open environment like internet.

There is no global trusted party is allowed. Chain of trust must be
fully distributed.


# 2. Functional description

## 2.1. Security Contexts

There are three major security context types:

* Service - Both execution environment and executable code is 
    under full control of the owner. This security context exists on
    servers.
* Client - Execution environment is under control of owner, but
    executable code is loaded from Service.
* Authentication Service (AuthService) - A special authentication service
    trusted by Service or by Client or by both.
    
Each Service and each Client must trust only one AuthService. If they 
trust different AuthServices then it is responsibility of AuthService
to establish communication to another AuthService. In such case,
Client is called *foreign AuthService user* or simply *foreign user*.

## 2.2. Service to Service interaction (and Service to AuthService in particular)

This is generic mechanism to establish interaction between any two services, where
one Service acts as shared secret MasterService.

MasterService is always the Server peer in initial interaction.

AuthService always acts as MasterService.


### 2.2.1. Establishing interaction
* Service must be able to self-register against any MasterService it trusts (only one)
    providing Service callback URL and initial shared secret (true randomly generated)
* MasterService must verify registration request through provided callback
** MasterService must reject non-secure callback connection in open environment
** Verification is performed through shared secret rotation

### 2.2.2. Shared secret

* There must be a persistent shared secret between Service and MasterService
* Special considerations are required as some messages can be passed
    through insecure third party (e.g Client), requiring encryption or
    at least verification to prevent certain type of attacks
* MasterService is responsible for shared secret rotation
** Every shared secret must have a sequential ID
** The previous shared secret must be active for transition period
    specified by MasterService and then discarded
* Shared secret must not be used for any encryption directly
** A derived key must be generated
** Derived can be re-used at any peer discretion based on Severity vs. Performance considerations.
*** There must be a limit imposed for total count of derived key reuse on each side
* So, each message must contain shared secret ID, derived key parameter and actual encrypted data/hmac
** Shared secret ID is overflowing monotonically incrementing hexdigit value
** Derived key parameter has similar behavior
* Key management policy is out of scope of this specification so far

### 2.2.3. Unregistration from MasterService

Under some communication patterns, a persistent shared secret exchange is not required.
It must be possible to unregister from MasterService.

* Service sends unregistration request to MasterService with HMAC
* MasterService verifies HMAC
* MasterService "forgets" Service
* Service can register again later


## 2.3. Stateful user authentication

This is default method to be used for most cases.

* Service redirects Client to AuthService with special parameters, identifying
    1) requesting Service (deduced from HMAC key ID) and 2) required security level
    3) random token associated with Client (must not be sensitive information)
    4) hmac signature made with Shared Secret.
** The data sent as regular FutoIn request message, encoded in JSON+Base64 and appended to AuthService URL
* AuthService performs custom user authentication based on Service and required security level
* AuthService stores Client session with random 256-bit ID
** There must be a limit of sessions per Service
* AuthService redirects Client to Service with payload:
** Payload is also regular FutoIn request message, encoded in JSON+Base64 and appended to Service callback URL
** Client session ID is encrypted with shared secret, **the same as used for HMAC**
** Client token provided by Service
** AuthService specified Time-To-Live (Service must re-validate Client session)
* Service
** Verifies HMAC
** Verifies if original random Client token matches current token
** Session ID is decrypted
** Service gets session parameters and constraints from AuthService by Session ID
** Service checks any provided constraints (X509 CN, public key, IP address, etc.)
* Service continuous normal interaction with Client

### 2.3.1. Security Levels

In some cases, Client may be allowed to get read-only information without deep verification,
but it becomes really important for all modification type of requests.

* Info - read-only access to private information
* SafeOps - Info + access to operation, which should not seriously compromise the system
* PrivilegedOps - SafeOps + access to operations, which may compromise the system
* ExceptionalOps - PrivilegedOps + access to very sensitive operations, like password change
** At Service discretion, should be one-time access with immediate downgrade to PrivilegedOps level



## 2.4. Stateless user authentication

This authentication method is designed for stateless API calls with
limited authorization capabilities as it is not always possible to establish
secure credentials management and/or implement a statefull client.

Credentials information is sent along-side API request.


## 2.5. User authentication methods

*Note: Service or AuthService is determined based Stateless or Stateful
authentication type*

Client password is stored in hash with salt.

### 2.5.1. Auth by clear text credentials

* Client credentials are sent in clear-text to Service/AuthService.
* AuthService hashes clear-text password with stored salt
* Authentication successfully completes if hash matches stored password hash

*Note 1: This mechanism is allowed ONLY for Stateless user authentication.*
*Note 2: This mechanism is allowed only for SafeOps and lower security level*
*Note 3: Password must be unique for every Service configured for Client*

### 2.5.2. Auth by Challenge-Response Authentication

* Client requests session auth random token and salt from Service/AuthService
* Service generates random token, stores in session and sends it with salt to Client
* Client hashes its password with salt
* Client generates HMAC of random token using hash above
** Potential vulnerability as hash can be deduces, followed by password being exposed
* Client sends HMAC to Service/AuthService for validation
* Service/AuthService also generates HMAC based on stored password hash and random string
* Authentication successfully completes if both HMACs match

### 2.5.3. Auth by X509 certificate through Service

* Allowed Client's X509 CN fields are known to AuthService
* Service/AuthService requests X509 certificate from Client on transport level
* Client sends its X509 certificate
* Authentication successfully completes if X509 CN fields matches configured one

### 2.5.4. Auth by public key through Service

* Allowed Client's public keys are known to AuthService
* Client sends public key on transport level to Service/AuthService
* Authentication successfully completes if public key matches any configured one

### 2.5.5. Auth by IPv4/IPv6 address

* Allowed Client's IPv4/IPv6 addresses are known to AuthService
* Authentication successfully completes if IPv4/IPv6 matches any configured one


## 2.6. Multi-method user authentication

There must be one or more sets of authentication methods.
In every set, there can be one or more authentication method.

Authentication succeeds only if all methods pass of any set.

## 2.7. HMAC generation

See [HMAC][] for details

### 2.7.1 Rules of HMAC generation for payload

* Payload has a tree structure and coded in JSON or any alternative format
* All keys and fields are feed to HMAC generator in text representation
* HMAC security fields is skipped, if present (in case of request validation)
* For each nested level, starting from the very root of tree-like payload structure:
** Key-value pairs are processing in ascending order based on Unicode comparison rules
** Key is feed into HMAC generator
** If value is sub-tree, then recurse this algorithm
** Otherwise, feed textual representation to HMAC generator


## 2.8. Client information exposed from AuthService to Service

Service can inform AuthService which Client information fields must be
approved by Client to be exposed to Service. Client authentication
cannot succeed unless Client approves fields being exposed to specific Service.
This functionality is available only Stateful authentication.

*Note: AuthService must stored list of approved fields per Client-Service pair.
Service must re-send Client for authentication, if more fields need to be approved*

### 2.8.1. List of standard field identifiers

* FirstName - a short name to be used in greetings, etc.
* FullName - full name to be used in official documents, implies access to FirstName
* DateOfBirth - ISO "YYYY-MM-DD" format
* TimeOfBirth - ISO "HH:mm:ss" format, can be truncated to minutes
* ContactEmail
* ContactPhone - full international number, starting with "+"
* HomeAddress
* WorkAddress
* Citizenship - list of countries of citizenship names
* GovernmentRegID - list of objects with country name, ID type and ID value fields ({country,idtype,value})
* AvatarURL


## 2.9. Client authentication invalidation event

* AuthService must notify all Services if Client authentication configuration changes
** On authentication set getting deleted
** On password, X509 CN, public key and other authentication method parameter changes* 
* Service must re-authenticate all active Client sessions on subsequent request or earlier


## 2.10. Foreign user authentication

If Client is foreign user then AuthService acts as Service to user "domestic" AuthService,
performing all communication transparently to original Service and Client.

For security reasons, only authentication requests from pre-approved Service list should
be forwarded to another AuthService.



# 3. Interface definitions

## 3.1. MasterService provider

`Iface{`

        {
            "iface" : "futoin.master.provider",
            "version" : "0.DV",
            "funcs" : {
                "register" : {
                    "params" : {
                        "callback" :  {
                            "type" : "string",
                            "desc" : "Consumer callback URL, implementing futoin.master.consumer interface"
                        },
                        "secret" : {
                            "type" : "string",
                            "Initial shared secret",
                        },
                    },
                    "result" : {
                        "ok" : {
                            "type" : "boolean",
                            "desc" : "Always true, if no exception"
                        }
                    },
                    "throws" : [
                        "AlreadyRegistered",
                        "InvalidCallback",
                        "InvalidSecret",
                        "KeyRotationFailure"
                    ]
                },
                "unRegister" : {
                    "params" : {
                        "callback" :  {
                            "type" : "string",
                            "desc" : "Original value from registration request"
                        }
                    },
                    "result" : {
                        "ok" : {
                            "type" : "boolean",
                            "desc" : "Always true, if no exception"
                        }
                    },
                    "throws" : [
                        "UnknownCallback"
                    ]
                }
            },
            "requires" : [
                "AllowAnonymous",
                "SecureChannel"
            ],
            "desc" : "MasterService Provider interface"
        }

`}Iface`


## 3.2. MasterService consumer

`Iface{`

        {
            "iface" : "futoin.master.consumer",
            "version" : "0.DV",
            "funcs" : {
                "newSharedKey" : {
                    "params" : {
                        "key_id" :  {
                            "type" : "string",
                            "desc" : "Shared secret ID"
                        },
                        "enc_key" : {
                            "type" : "string",
                            "desc" : "Key, encrypted with the same key as used for HMAC",
                        },
                    },
                    "result" : {
                        "ok" : {
                            "type" : "boolean",
                            "desc" : "Always true, if no exception"
                        }
                    }
                }
            },
            "requires" : [
                "SecureChannel"
            ],
            "desc" : "MasterService Provider interface"
        }

`}Iface`

## 3.3. AuthService backend provider (Service interface)

`Iface{`

        {
            "iface" : "futoin.auth.backend",
            "version" : "0.DV",
            "funcs" : {
                "getClientInfo" : {
                    "params" : {
                        "session" : {
                            "type" : "string",
                            "desc" : "Session token from futoin.auth.consumer.complete.ssn"
                        }
                    },
                    "result" : {
                        "info" : {
                            "type" : "map",
                            "desc" : "Map of Private Info fields, allowed by Client to be sent"
                        }
                    },
                    "throws" : {
                        "InvalidSessionID"
                    }
                },
                "validate" : {
                    "params" : {
                        "session" : {
                            "type" : "string",
                            "desc" : "Session token from futoin.auth.consumer.complete.essn"
                        }
                    },
                    "result" : {
                        "constraints" : {
                            "type" : "array",
                            "desc" : "Array of object sets of constraints"
                        }
                    },
                    "throws" : {
                        "InvalidSessionID"
                    }
                },
            },
            "requires" : [
                "SecureChannel"
            ],
            "desc" : "AuthService Backend Provider interface"
        }

`}Iface`

## 3.4. AuthService frontend provider (Client interface)

`Iface{`

        {
            "iface" : "futoin.auth.frontend",
            "version" : "0.DV",
            "funcs" : {
                "signIn" : {
                    "params" : {
                        "lvl" : {
                            "type" : "string",
                            "desc" : "Required Security Level",
                        },
                        "pf" : {
                            "type" : "array",
                            "desc" : "List of private field access to request"
                        },
                        "tkn" : {
                            "type" : "string",
                            "desc" : "Requesting Service provided client token"
                        }
                    },
                    "desc" : "Special handling. Service and its callback must be determined from sec.ki parameter. Client is 'transport'",
                },
                "authBySecret" : {
                    "params" : {
                        "client_id" : {
                            "type" : "string",
                            "desc" : "Unique Client ID"
                        },
                        "secret" : {
                            "type" : "string",
                            "desc" : "Client secret"
                        }
                    },
                    "result" : {
                        "ok" : {
                            "type" : "boolean",
                            "desc" : "Always true, if no exception"
                        }
                    },
                    "throws" : {
                        "InvalidClientID",
                        "InvalidSecret",
                        "Blocked"
                    },
                    "desc" : "Authorize by ID/secret pair. Can be called by Service, if allowed"
                },
                "completeSignIn" : {
                    "result" : {
                        "redirect" : {
                            "type" : "string",
                            "desc" : "Redirect URL to return to requesting Service"
                        }
                    }
                }
            },
            "requires" : [
                "AllowAnonymous",
                "SecureChannel"
            ],
            "desc" : "AuthService Backend Provider interface"
        }

`}Iface`

## 3.5. AuthConsumer

`Iface{`

        {
            "iface" : "futoin.auth.consumer",
            "version" : "0.DV",
            "funcs" : {
                "complete" : {
                    "params" : {
                        "essn" : {
                            "type" : "string",
                            "desc" : "Encrypted session token ID"
                        },
                        "ttl" : {
                            "type" : "string",
                            "desc" : "Time-to-Live for Client session"
                        }
                    }
                }
            },
            "requires" : [
                "AllowAnonymous"
            ],
            "desc" : "AuthService Backend Provider interface"
        }

`}Iface`



# 4. Defense system integration

Security is common responsibility. Every node of the system must be a defense barrier for
both attacks and simple misconfiguration.

Typically, more farther node from actual attacker should have a little higher failure rate
limit to avoid a closer node being banned, leading to Denial of Service of specific 
functionality.

Each service must detect attacking Clients/Services and deny access before security limit
is triggered on another host.

*Note: all hit or approaching limits must be reported to administration for actions to be 
taken*

**Any error, which never happens by race condition, mistake, etc. must immediately trigger
defense system action** Example: session token validation by other Service.

# 4.1. Possible limit types

* Limit per period from the same client and/or host and/or network
** Request count
** Security failures
* Dynamic limits
** Limit can be risen and lowered dynamically (e.g. AuthService rices limits per Services
    based on number of active users)

    

# 5. Detailed encryption and authentication requirements

SHA-3 was desired as a start, but SHA-2 is more widespread at the moment.
So, SHA-2 is to be used until SHA-3 is penetrated into most technologies.

SHA-384, SHA-512 or its truncated version SHA-512/224, SHA-512/256 is to be used
at the moment. Dependant peer must deduce actual hash function based on
hash length.

AES-256 is to be used as encryption cipher. Therefore minimal shared secret
length is 256-bit. Longer keys should be truncated.


* MasterService is responsible for choosing the right key and hash lengths
* Later, it can be extended with other length types
* All raw binary strings must be encoded in Base64 according to [base64][]
* JSON sent as GET path and/or parameter is also encoded in Base64
* There must be blacklist rules for forbidden keys (derived from respective hash/cipher function considerations)
** Shared secret must be re-generated
** Derived key must be skipped
* Key ID must be unique per each MasterService and normally used to determine Service

# 5.1. Message "sec" field sub-schema for HMAC

`Schema(futoin-sec-hmac){`

        {
            "title" : "FutoIn 'sec' field - HMAC",
            "type" : "object",
            "additionalProperties" : false,
            "required" : [ "ksn", "hmac" ],
            "properties" : {
                "ki" : {
                    "type" : "string",
                    "description" : "Base shared secret ID"
                },
                "di" : {
                    "type" : "string",
                    "description" : "Derived key sequence ID"
                },
                "hmac" : {
                    "type" : "string",
                    "description" : "Base64 encoded HMAC"
                },
            }
        }

`}Schema`

# 5.2. Message "sec" field sub-schema for Stateless authentication

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
                    "description" : "Optional. Any type of secret, typically password"
                },
            }
        }

`}Schema`



# 6. Examples

## 6.1. Typical web case

## 6.2. Clear-text credentials in automation case



[hmac]: http://en.wikipedia.org/wiki/Hash-based_message_authentication_code "HMAC"
[base64]: http://www.faqs.org/rfcs/rfc2045.html "RFC2045 section 6.8"

