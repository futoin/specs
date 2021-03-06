<pre>
FTN13: FutoIn Secure Vault
Version: 1.1
Date: 2018-05-31
Copyright: 2014-2018 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

* v1.1 - 2018-05-31 - Andrey Galkin
    - NEW: PWD key type
    - NEW: MAC processing
    - NEW: MAC aliases
    - NEW: optional prefix search for key listing
    - NEW: event stream description
* v1.0 - 2018-02-13 - Andrey Galkin
    - Final
* v0.3 - 2018-02-12 - Andrey Galkin
    - CHANGED: revised futoin.secvault.keys iface
* v0.2 - 2018-01-15 - Andrey Galkin
    - NEW: interface definitions & extended concept
* v0.1 - 2014-09-26 - Andrey Galkin
    - Initial draft

# 1. Intro

It is not a new concept, but standardization of higher level interface for
Host Security Modules and similar pure software or hardware components.

The main idea is that critical sensitive data is accessible only to a small peace of
software/hardware effectively limiting scope of source code, hardware design and/or
infrastructure required to be audited for security issues in first place. Most flaws in
other software parts of larger project should have less impact on sensitive data
disclosure.

Critical sensitive data: private or shared cryptography secrets, keys for tokenization
of data, etc.

# 2. Concept

Secure Vault (SV) is assumed to be a FutoIn service with the following characteristics:

1. Sensitive data must never get exposed outside of service in unencrypted form.
    - However, it may be allowed to expose it for performance reasons, if it does not
        jeopardize not related security scopes.
2. All sensitive data stored externally must be encrypted and decrypted inside
    the SV itself.
3. There must be a small enough secret to unlock the rest of data. Management of such
    secret is out of scope and should be a secret by nature.
4. Two different SV instances may share one or more common secrets used for authentication
    and encryption.
5. Security and durability of SV is out of scope. SV can be implemented both as regular
    application vulnerable to many types of local system attacks or as a firmware for
    hardware security module.

## 2.1. Secret key management

The following features are required:

1. Generation & storage of any supported key type internally.
2. Clear separation of private and shared keys purpose (not depending on type).
3. Exposure of shared keys as:
    - encrypted data with provided public key.
    - encrypted data with provided symmetric key.
    - encrypted data with key already stored in SV.
    - unencrypted as is.
4. Injection of keys using the same format as for exposure.
5. Persistent and temporary derived key operations.

## 2.2. Data operations

1. Encryption of any arbitrary data with any of stored keys.
2. Decryption of previously encrypted data.
3. Data signing.
4. Signature verification.

## 2.3. Supported keys & ciphers

Each implementation may choose to support any subset of all availables types.

## 2.4. Naming

The specifications tries to cover only commonly used algorithms, but actual implementation
may add custom constants.

Specification intentionally does not list specific types to be as generic as possible.

Suggested list, self-explanatory:

* Key types & parameters:
    * Symmetric like AES, GOST 34.12, RAW
        * integer bits as parameter
    * `RSA`
        * integer bits as parameter
    * `EdDSA`
        * string curve name as parameter
    * `GOST3410` - GOST 34.10 PKI
        * map as parameter:
            * `version` - string:
                - '2012-256'
                - '2012-512'
            * `paramset` - set:
                - A, B, C, XA, XB - string items
    * `Password` - plain unicode password secret
    * `HMAC` - key to be used for Hash-based Message Authentication Code
    * `KMAC` - key to be used for Kessac Message Authentication Code
* Symmetric encryption/decryption:
    * `AES-CBC`
    * `AES-CTR`
    * `AES-GCM`
    * `GOST3412-CBC`
    * `GOST3412-CTR`
    * `GOST3412-CFB`
* Asymmetric encryption/decryption:
    * `GOST3410`
    * `RSA`
* Message Authentication:
    * HMAC:
        * "HMAC-MD5" or "HMD5"
        * GOST3411 family:
            * "HMAC-GOST3411-256" or "HG256"
            * "HMAC-GOST3411-512" or "HG512"
        * SHA v2 family:
            * "HMAC-SHA-224" or "HS224"
            * "HMAC-SHA-256" or "HS256"
            * "HMAC-SHA-384" or "HS384"
            * "HMAC-SHA-512" or "HS512"
    * KMAC:
        * "KMAC-128" - Keccak MAC 128-bit
        * "KMAC-256" - Keccak MAC 256-bit
* Key Derivation:
    * `HKDF`
    * `PBKDF2`

## 2.5. Key usage constraints

SV must obey key constraints:

* `encrypt` - allow encryption and decryption
* `sign` - allow signing and verification
* `derive` - allow key deriving
* `shared` - allow key to be exposed externally
* `temp` - allow auto-purge after common configured time-to-live

## 2.6. Statistics collection

SV must collect key usage statistics as a hint to regenerate keys
and/or block possible attacks.

## 2.7. External key ID

Any key is created for some purpose. So, external ID is mandatory and can be
used implementation-defined way to recover from errors like timeouts without
unused key artifacts hanging in SV.

## 2.8. Additional encryption & decryption parameters

Initialization Vector (IV) is required for most cases of data encryption. There is
known flexibility with padding strategy. Authentication tag passing is required for
authenticated data decryption.

As it's very easy to mess up and this spec also definitely has some flaws,
the spec tries to minimize user's decision making on encryption.

General strategy:

1. Control generation of IV in cluster environment - random data.
    - If needed, IV may be HKDF-derived from public parameter in cipher mode variations.
    - It should be possible to pass custom IV though.
2. Control re-use of IV based on:
    - dummy probability - limit times the same key is used and total bytes encrypted.
    - save the last used IV per key in single process:
        - fail on duplicate in CTR-like
        - fail on minor difference in CBC-like
    - CTR, CCM, GCM and EAX should be avoided due to drawbacks on IV collision unless
        properly unique IV are ensured.
3. Pack all parts in predefined format.
    - Choose to append non-data values as they should be shorter in most cases.
        So, inefficient buffer operations in some implementations would need to
        move less data.
    - Append IV and then AuthTag
        - both assumed to be fixed length even for GCM/EAX
    - Notes:
        - AES must use fixed 128-bit IV for all modes, except:
            - 96-bit for GCM
        - GCM/CCM must use full 128-bit AuthTag
4. Use common PKCS#5/PKCS#7 padding unless fundamental issues are found.
5. In general, authentication is achieved through overall FutoIn message MAC.
    - Authenticating encryption should be used for non-message cases and/or
        interfaces without `MessageSignature` constraint.

## 2.9. Key data formats

Implementation should use the following defaults for key transport representation.

* Asymmetric (RSA, DH, EC, etc.) - ASN.1 DER in byte buffer
* Symmetric - Raw byte buffer

## 2.10. Internal UUID vs. External ID

From pure SV point of view, use of two identification approaches may look like overkill, but
it has important meaning out of scope:

1. External ID assumed to be descriptive - it exposes information.
2. Internal UUID is assumed to be transfered over network - shorter in size and
    obscured.

So, "External ID" is really a string internal to SV which creates internal references to
external entities. Meanwhile, Internal UUID is unique per SV, but is exposed. So, other
entities can refence Internal UUID of particular SV instance.

## 2.11. Plain Password handling

It must be possible to securely generate, inject, expose and verify password.

Verification must be a secure comparison of signature against the key itself.
Any data passed is to be ignored.

## 2.12. Message Authentication Code processing

There must be a dedicated "MAC" key type,

It must be possible to securely generate, inject, expose, sign and verify.

## 2.13. Event names

The following events to be generated. Precise description is in interfaces.

* `SV_NEW` - new SecureVault key
* `SV_DEL` - removal of SecureVault key
* `SV_UPD` - usage update for SecureVault

# 3. Interface

## 3.1. Common types


`Iface{`

    {
        "iface" : "futoin.secvault.types",
        "version" : "{ver}",
        "ftn3rev" : "1.9",
        "imports" : [
            "futoin.types:1.0"
        ],
        "types" : {
            "KeyID" : "UUIDB64",
            "ExtID" : {
                "type" : "string",
                "minlen" : 1,
                "maxlen" : 128
            },
            "KeyType" : {
                "type" : "GenericIdentifier",
                "minlen" : 1,
                "maxlen" : 32
            },
            "KeyUsage" : {
                "type" : "set",
                "items" : [
                    "encrypt",
                    "sign",
                    "derive",
                    "shared",
                    "temp"
                ]
            },
            "GenParams" : [
                "string",
                "integer",
                "map"
            ],
            "KeyInfo" : {
                "type" : "map",
                "fields" : {
                    "id" : "KeyID",
                    "ext_id" : "ExtID",
                    "usage" : "KeyUsage",
                    "type" : "KeyType",
                    "params" : "GenParams",
                    "created" : "Timestamp",
                    "times" : "NotNegativeInteger",
                    "bytes" : "NotNegativeInteger",
                    "failures" : "NotNegativeInteger",
                    "used_times" : {
                        "type" : "NotNegativeInteger",
                        "desc" : "Deprecated"
                    },
                    "used_bytes" : {
                        "type" : "NotNegativeInteger",
                        "desc" : "Deprecated"
                    },
                    "sig_failures" : {
                        "type" : "NotNegativeInteger",
                        "desc" : "Deprecated"
                    }
                }
            },
            "KeyIDList" : {
                "type" : "array",
                "elemtype" : "KeyID"
            },
            "RawData" : {
                "type" : "data",
                "maxlen" : 1048576
            },
            "KeyData" : {
                "type" : "data",
                "maxlen" : 16384
            },
            "PublicKeyData" : {
                "type" : "data",
                "maxlen" : 16384
            },
            "PublicKey" : {
                "type" : "map",
                "fields": {
                    "type" : "KeyType",
                    "data" : "PublicKeyData"
                }
            },
            "HashType" : {
                "type" : "string",
                "regex" : "^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$",
                "maxlen" : 16
            },
            "CipherMode" : {
                "type" : "string",
                "regex" : "^[A-Z0-9][A-Z0-9_]{1,14}[A-Z0-9]$",
                "desc" : "CBC, CTR, GCM, CFB and others"
            },
            "KeyDerivationFunction" : "KeyType",
            "InitializationVector" : {
                "type" : "data",
                "maxlen" : 128,
                "desc" : "Most ciphers accept only block size, e.g. 16 bytes"
            }
        }
    }

`}Iface`

## 3.2. Key management

`Iface{`

    {
        "iface" : "futoin.secvault.keys",
        "version" : "{ver}",
        "ftn3rev" : "1.9",
        "imports" : [
            "futoin.secvault.types:{ver}"
        ],
        "funcs" : {
            "unlock" : {
                "params" : {
                    "secret" : "KeyData"
                },
                "result" : "boolean",
                "throws" : [
                    "InvalidSecret"
                ]
            },
            "lock" : {
                "result" : "boolean"
            },
            "generateKey" : {
                "params" : {
                    "ext_id" : "ExtID",
                    "usage" : "KeyUsage",
                    "key_type" : "KeyType",
                    "gen_params" : "GenParams"
                },
                "result" : "KeyID",
                "throws" : [
                    "UnsupportedType",
                    "OrigMismatch"
                ]
            },
            "injectKey" : {
                "params" : {
                    "ext_id" : "ExtID",
                    "usage" : "KeyUsage",
                    "key_type" : "KeyType",
                    "gen_params" : "GenParams",
                    "data" : "KeyData"
                },
                "result" : "KeyID",
                "throws" : [
                    "UnsupportedType",
                    "OrigMismatch",
                    "InvalidKey"
                ]
            },
            "injectEncryptedKey" : {
                "params" : {
                    "ext_id" : "ExtID",
                    "usage" : "KeyUsage",
                    "key_type" : "KeyType",
                    "gen_params" : "GenParams",
                    "data" : "KeyData",
                    "enc_key" : "KeyID",
                    "mode" : "CipherMode"
                },
                "result" : "KeyID",
                "throws" : [
                    "UnsupportedType",
                    "OrigMismatch",
                    "UnknownKeyID",
                    "NotApplicable",
                    "InvalidKey"
                ]
            },
            "deriveKey" : {
                "params" : {
                    "ext_id" : "ExtID",
                    "usage" : "KeyUsage",
                    "key_type" : "KeyType",
                    "gen_params" : "GenParams",
                    "base_key" : "KeyID",
                    "kdf" : "KeyDerivationFunction",
                    "hash" : "HashType",
                    "salt" : "KeyData",
                    "other" : "map"
                },
                "result" : "KeyID",
                "throws" : [
                    "UnknownKeyID",
                    "UnsupportedKey",
                    "UnsupportedDerivation",
                    "InvalidParams",
                    "NotApplicable",
                    "OrigMismatch"
                ]
            },
            "wipeKey" : {
                "params" : {
                    "id" : "KeyID"
                },
                "result" : "boolean"
            },
            "exposeKey" : {
                "params" : {
                    "id" : "KeyID"
                },
                "result" : "KeyData",
                "throws" : [
                    "UnknownKeyID",
                    "NotApplicable"
                ]
            },
            "encryptedKey" : {
                "params" : {
                    "id" : "KeyID",
                    "enc_key" : "KeyID",
                    "mode" : "CipherMode"
                },
                "result" : "KeyData",
                "throws" : [
                    "UnknownKeyID",
                    "NotApplicable"
                ]
            },
            "pubEncryptedKey" : {
                "params" : {
                    "id" : "KeyID",
                    "pubkey" : "PublicKey"
                },
                "result" : "KeyData",
                "throws" : [
                    "UnknownKeyID",
                    "NotApplicable"
                ]
            },
            "publicKey" : {
                "params" : {
                    "id" : "KeyID"
                },
                "result" : "PublicKey",
                "throws" : [
                    "UnknownKeyID",
                    "NotApplicable"
                ]
            },
            "keyInfo" : {
                "params" : {
                    "id" : "KeyID"
                },
                "result" : "KeyInfo",
                "throws" : [
                    "UnknownKeyID"
                ]
            },
            "extKeyInfo" : {
                "params" : {
                    "ext_id" : "ExtID"
                },
                "result" : "KeyInfo",
                "throws" : [
                    "UnknownKeyID"
                ]
            },
            "listKeys" : {
                "params" : {
                    "ext_prefix" : {
                        "type" : "ExtID",
                        "default" : null
                    }
                },
                "result" : "KeyIDList"
            },
            "addStats" : {
                "params" : {
                    "id" : "KeyID",
                    "times" : "NotNegativeInteger",
                    "bytes" : "NotNegativeInteger",
                    "failures" : "NotNegativeInteger"
                },
                "result" : "boolean",
                "throws" : [
                    "UnknownKeyID"
                ]
            }
        },
        "requires" : [
            "SecureChannel",
            "BinaryData"
        ]
    }

`}Iface`

## 3.3. Data operations

`Iface{`

    {
        "iface" : "futoin.secvault.data",
        "version" : "{ver}",
        "ftn3rev" : "1.9",
        "imports" : [
            "futoin.secvault.types:{ver}"
        ],
        "funcs" : {
            "encrypt" : {
                "params" : {
                    "id" : "KeyID",
                    "data" : "RawData",
                    "mode" : {
                        "type" : "CipherMode",
                        "default" : null
                    },
                    "iv" : {
                        "type" : "InitializationVector",
                        "default" : null
                    },
                    "aad" : {
                        "type" : "RawData",
                        "default" : null
                    }
                },
                "result" : "RawData",
                "throws" : [
                    "UnsupportedType",
                    "UnsupportedCipher",
                    "NotApplicable"
                ],
                "maxreqsize" : "1100K",
                "maxrspsize" : "1100K"
            },
            "decrypt" : {
                "params" : {
                    "id" : "KeyID",
                    "data" : "RawData",
                    "mode" : {
                        "type" : "CipherMode",
                        "default" : null
                    },
                    "aad" : {
                        "type" : "RawData",
                        "default" : null
                    }
                },
                "result" : "RawData",
                "throws" : [
                    "UnsupportedType",
                    "UnsupportedCipher",
                    "InvalidData",
                    "NotApplicable"
                ],
                "maxreqsize" : "1100K",
                "maxrspsize" : "1100K"
            },
            "sign" : {
                "params" : {
                    "id" : "KeyID",
                    "data" : "RawData",
                    "hash" : "HashType"
                },
                "result" : "RawData",
                "throws" : [
                    "UnsupportedType",
                    "UnsupportedHash",
                    "InvalidData",
                    "NotApplicable"
                ],
                "maxreqsize" : "1100K"
            },
            "verify" : {
                "params" : {
                    "id" : "KeyID",
                    "data" : "RawData",
                    "sig" : "RawData",
                    "hash" : "HashType"
                },
                "result" : "boolean",
                "throws" : [
                    "UnsupportedType",
                    "UnsupportedHash",
                    "InvalidData",
                    "InvalidSignature",
                    "NotApplicable"
                ],
                "maxreqsize" : "1100K"
            }
        },
        "requires" : [
            "SecureChannel",
            "BinaryData"
        ]
    }

`}Iface`

## 3.4. Events

`Iface{`

    {
        "iface" : "futoin.secvault.events",
        "version" : "{ver}",
        "ftn3rev" : "1.9",
        "imports" : [
            "futoin.secvault.types:{ver}"
        ],
        "types" : {
            "SvNew" : {
                "type" : "map",
                "fields" : {
                    "id" : "KeyID",
                    "ext_id" : "ExtID",
                    "type" : "KeyType"
                }
            },
            "SvDel" : {
                "type" : "map",
                "fields" : {
                    "id" : "KeyID"
                }
            },
            "SvUpd" : {
                "type" : "map",
                "fields" : {
                    "id" : "KeyID",
                    "times" : {
                        "type" : "NotNegativeInteger",
                        "optional" : true
                    },
                    "bytes" : {
                        "type" : "NotNegativeInteger",
                        "optional" : true
                    },
                    "failures" : {
                        "type" : "NotNegativeInteger",
                        "optional" : true
                    }
                }
            }
        }
    }

`}Iface`

=END OF SPEC=
