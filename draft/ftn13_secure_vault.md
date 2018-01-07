<pre>
FTN13: FutoIn Secure Vault
Version: 0.DV2
Date: 2018-01-06
Copyright: 2014-2018 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

* v0.2 - 2018-01-06 - Andrey Galkin
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

1. Generation & storage of any support key type internally.
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

* Key types & params:
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
            * 'paramset' - set:
                - A, B, C, XA, XB - string items
* Container Formats:
    * `DER` - ASN.1
    * `DERB64` - ASN.1 encoded in Base64
    * `PEM`
    * `PKCS11` - PKCS#11
    * `PKCS11B64` - PKCS#11 encoded in Base64
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
        * "HMAC-MD5"
        * GOST3411 family:
            * "HMAC-GOST3411-256"
            * "HMAC-GOST3411-512"
        * SHA v2 family:
            * "HMAC-SHA-224"
            * "HMAC-SHA-256"
            * "HMAC-SHA-384"
            * "HMAC-SHA-512"
        * SHA v3 family:
            * "HMAC-SHA3-224"
            * "HMAC-SHA3-256"
            * "HMAC-SHA3-384"
            * "HMAC-SHA3-512"
    * KMAC:
        * "KMAC128" - Keccak MAC 128-bit
        * "KMAC256" - Keccak MAC 256-bit
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

# 3. Interface

## 3.1. Common types


`Iface{`

    {
        "iface" : "futoin.secvault.types",
        "version" : "{ver}",
        "ftn3rev" : "1.8",
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
            "ContainerFormat" : {
                "type" : "GenericIdentifier",
                "minlen" : 1,
                "maxlen" : 32
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
                    "usage" : "KeyUsage",
                    "type" : "KeyType",
                    "params" : "GenParams",
                    "created" : "Timestamp",
                    "used_times" : "NotNegativeInteger",
                    "used_bytes" : "NotNegativeInteger",
                    "sig_failures" : "NotNegativeInteger"
                }
            },
            "KeyInfoList" : {
                "type" : "array",
                "elemtype" : "KeyInfo"
            },
            "PublicKey" : {
                "type" : "map",
                "fields": {
                    "key_type" : "KeyType",
                    "format" : "ContainerFormat",
                    "data" : "string"
                }
            },
            "CipherType" : {
                "type" : "string",
                "regex" : "^[a-Z0-9][a-Z0-9-]*[a-Z0-9]$",
                "maxlen" : 64
            },
            "KeyDerivationFunction" : "CipherType"
        },
        "requires" : [ "SecureChannel" ]
    }

`}Iface`

## 3.2. Key management

`Iface{`

    {
        "iface" : "futoin.secvault.keys",
        "version" : "{ver}",
        "ftn3rev" : "1.8",
        "imports" : [
            "futoin.secvault.types:{ver}"
        ],
        "funcs" : {
            "unlock" : {
                "params" : {
                    "secret" : "string"
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
                    "format" : "ContainerFormat",
                    "data" : "string"
                },
                "result" : "KeyID",
                "throws" : [
                    "UnsupportedType",
                    "OrigMismatch"
                ]
            },
            "injectEncryptedKey" : {
                "params" : {
                    "ext_id" : "ExtID",
                    "usage" : "KeyUsage",
                    "key_type" : "KeyType",
                    "gen_params" : "GenParams",
                    "format" : "ContainerFormat",
                    "data" : "string",
                    "enc_key" : "KeyID"
                },
                "result" : "KeyID",
                "throws" : [
                    "UnsupportedType",
                    "OrigMismatch"
                ]
            },
            "deriveKey" : {
                "params" : {
                    "ext_id" : "ExtID",
                    "base_key" : "KeyID",
                    "kdf" : "KeyDerivationFunction",
                    "key_len" : "RandomBits",
                    "salt" : "string",
                    "other" : "map"
                },
                "result" : "string",
                "throws" : [
                    "UnknownKeyID",
                    "UnsupportedDerivation",
                    "InvalidParams",
                    "NotApplicable"
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
                    "id" : "KeyID",
                    "format" : "ContainerFormat"
                },
                "result" : "string",
                "throws" : [
                    "UnknownKeyID",
                    "UnsupportedFormat",
                    "NotApplicable"
                ]
            },
            "encryptedKey" : {
                "params" : {
                    "id" : "KeyID",
                    "format" : "ContainerFormat",
                    "enc_key" : "KeyID"
                },
                "result" : "string",
                "throws" : [
                    "UnknownKeyID",
                    "UnsupportedFormat",
                    "NotApplicable"
                ]
            },
            "pubEncryptedKey" : {
                "params" : {
                    "id" : "KeyID",
                    "format" : "ContainerFormat",
                    "pubkey" : "PublicKey"
                },
                "result" : "string",
                "throws" : [
                    "UnknownKeyID",
                    "UnsupportedFormat",
                    "NotApplicable"
                ]
            },
            "publicKey" : {
                "params" : {
                    "id" : "KeyID",
                    "format" : "ContainerFormat"
                },
                "result" : "string",
                "throws" : [
                    "UnknownKeyID",
                    "UnsupportedFormat",
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
            "listKeys" : {
                "result" : "KeyInfoList"
            }
        },
        "requires" : [ "SecureChannel" ]
    }

`}Iface`

## 3.3. Data operations

`Iface{`

    {
        "iface" : "futoin.secvault.data",
        "version" : "{ver}",
        "ftn3rev" : "1.8",
        "imports" : [
            "futoin.secvault.types:{ver}"
        ],
        "funcs" : {
            "encrypt" : {
                "params" : {
                    "id" : "KeyID",
                    "data" : "string",
                    "cipher" : "CipherType"
                },
                "result" : "string",
                "throws" : [
                    "UnsupportedType",
                    "UnsupportedCipher",
                    "NotApplicable"
                ]
            },
            "decrypt" : {
                "params" : {
                    "id" : "KeyID",
                    "data" : "string",
                    "cipher" : "CipherType"
                },
                "result" : "string",
                "throws" : [
                    "UnsupportedType",
                    "UnsupportedCipher",
                    "InvalidData",
                    "NotApplicable"
                ]
            },
            "sign" : {
                "params" : {
                    "id" : "KeyID",
                    "data" : "string",
                    "cipher" : "CipherType"
                },
                "result" : "string",
                "throws" : [
                    "UnsupportedType",
                    "UnsupportedCipher",
                    "InvalidData",
                    "NotApplicable"
                ]
            },
            "verify" : {
                "params" : {
                    "id" : "KeyID",
                    "data" : "string",
                    "sig" : "string",
                    "cipher" : "CipherType"
                },
                "result" : "boolean",
                "throws" : [
                    "UnsupportedType",
                    "UnsupportedCipher",
                    "InvalidData",
                    "InvalidSignature",
                    "NotApplicable"
                ]
            }
        },
        "requires" : [ "SecureChannel" ]
    }

`}Iface`

=END OF SPEC=
