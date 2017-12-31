<pre>
FTN8: FutoIn Security Concept
Version: 0.2DV
Date: 2017-12-29
Copyright: 2014-2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v0.2 - 2017-12-29 - Andrey Galkin
    - CHANGED: heavily revised & split into sub-specs
    - CHANGED: moved HMAC logic from FTN6 spec to MAC section here
    - NEW: added different MAC schemes support
    - NEW: completed of local authentication & authorization spec
    - NEW: completed Client Single Sign-On
* v0.1 - 2014-06-03 - Andrey Galkin
    - Initial draft

# 1. Intro

Security concept is required to build a unified authentication and
authorization model across security domains and use cases with separate control
in open environment like internet.

There is no global trusted party is allowed. Chain of trust must be
fully distributed.

## 1.1. Sub-specifications

* [FTN8.1: Stateless Authentication](./ftn8.1\_stateless\_auth.md)
* [FTN8.2: Master Secret Authentication](./ftn8.2\_master\_auth.md)
* [FTN8.3: Client Authentication](./ftn8.3\_client\_auth.md)
* [FTN8.4: Access Control](./ftn8.4\_access\_control.md)
* [FTN8.5: Defense System](./ftn8.5\_defense.md)
* [FTN8.6: Foreign Users](./ftn8.6\_foreign\_users.md)
* [FTN8.7: End-to-End Encryption](./ftn8.7\_e2ee.md)
* [FTN8.8: QA Requirements](./ftn8.8\_qa\_requirements.md)


# 2. Concept

## 2.1. General guidelines

1. External parties to particular system must never hold internal security-related
    data even if it is encrypted and/or signed to prevent theoritical falsification
    attacks.
    - User passwords and similar secrets are not internal data - they belong to user.
    - Session tokens must hold only session ID with session-related secrets - no other info.
        - two parts are required to detect bruteforcing
    - Even only informational purpose user IDs, secrets, access levels, etc.
        must never be stored in untrusted party as it may eventually be used as trusted
        data source and be subject for attack.
    - Use tokens only to reference actual access grants - do not use them as passphrases
2. There must be limit for failed attempts of bruteforcing any secret
    - authenticated attackers must be blocked by user ID - reject all requests
    - attackers must be blocked by source IP first of all
    - then object under attack has to be disabled (higher limit)
        - users and resources to be temporary locked
        - sessions, keys, temporaries to be destroyed
    - to prevent DoS of particular user/resource:
        - minimize use of easily guessable IDs
        - require authorization for most cases of guessing
3. Check authentication and authorization in online mode
    - allow caching only if proper real-time invalidation event handling is active
4. Centralize authentication and authorization
    - user must be able to overview everything from single dashboard
5. Often used secrets must be updated in reasonable period
    - both usage time and number of secret applications must be taken into account
6. Avoid information leaks
    - Do not use sequential IDs
    - Do not expose object existence on error
        - Always throw general "SecurityError" with generic error info
        - Prevent time-based attacks - make consistent delays on any SecurityError
    - Do not use descriptive identifiers in tokens
    - Prevent attacks which expose ID existence on authentication
7. Forward Secrecy
    - use modern TLS, SSH, IPSec or other type of secure channel with
        perfect forward secrecy characteristics
    - use secure symmetric key exchange
    - use derived keys for each use occurence
        * use derivation with extra parameter when extra safety is required
            (e.g. key serial number for dervied encryption keys)
    - End-to-End Encryption API

## 2.2. Security Contexts

There are three major security contexts:

* Service - Both execution environment and executable code is 
    under full control of the owner.
    - This security context exists on servers.
    - Service is a logic unit represented by a union of related
        FutoIn specs provided by one or many related end-points.
* Client - Execution environment is under control of owner, but
    executable code is loaded from Service.
* Authentication Service (AuthService) - A special authentication &
    authorization service trusted by Service and/or by Client.

Each Service and each Client must trust only one AuthService.

The standard auth mechanism does not allow Client code to access
protected resources in another Service directly. Such feature may be
implemented as sub-spec.

In addition, the following optional services exist:

* Defense System (DefenseService) - A special service which helps to detect
    and fight attacks. Its context is implementation-defined.

## 2.3. Holistic pictures

### 2.3.1. Request Processing

It may look as too much overhead for a single request processing, but
any decent system does exactly the same in fact. However, instead of
modules are used instead of separate microservices. FutoIn converts
modules to services by fundamental design. There should be efficient
in-process calling mechanism to minimize penalties.


    Client         Service        AuthService   DefenseService
        |             .                  .            .
        |-- request ->|                  .            .
        .             |----------- onCall() --------->|
        .             .                  .     [may fail early]
        .             |<------ defense action --------|
        .             |-- checkAuth() -->|            .
        .             |<-- auth rsp -----|            .
        .             |- checkAccess() ->|            .
        .             .           [fail on error]     .
        .       [defense action]         .            .
        .         [process]              .            .
        .             |----------- onResult() ------->|
        |<- response -|                  .            .
        |             .                  .            .

### 2.3.2. Service to AuthService registration

It's assumed that one of Message Authentication Code approaches
are used which require a preshared secret and secure updates
of that.

Initial manual registration:

    Operator                AuthService
        |                        .
        |--- register Service -->|
        .                 [gen initial secret]
        |<-- clear text secret --|
    [manually configure Service] .
        .                        .

Initial automatic registration through secure channel, if allowed:

    Service                            AuthService
       |                                   .
    [gen temporary assymetric key]         .
       |----- request registration ------->|
       .                [depend on transport's MitM security]
       .                    [save request for approval]
       |<-------- get ticket ID -----------|
       .                                   .
    [reasonable delay]               [wait approval]
       .                                   .
       |-- try to complete registration -->|
       |<- "pending" or "rejected" error --|
       .                                   .
    [reasonable delay]         [operator/auto approval]
       .                                   .
       |-- try to complete registration -->|
       .                         [generate new secret]
       |<-- return new encrypted secret ---|
    [decrypt secret and discard key]       .
    [use new secret]                       .
       |                                   .

Shared secret secure exchange:

    Service                            AuthService
       |                                   .
    [gen temporary assymetric key]         .
       |----- request new secret --------->|
       .             [use current secret for MitM security]
       .                         [generate new secret]
       |<-- return new encrypted secret ---|
    [decrypt secret and discard key]       .
    [use new secret]                       .
       |                                   .

        

### 2.3.3. Single Sign-On (SSO)

General goal is to concentrate user authentication and access grants
in single place - AuthService. See below for description of Access
Request Templates.

Register authorization access request templates:

    Service                           AuthService
       |                                   .
       |-------- create template --------->|
       .                 [register template of required access requests]
       |<----- return redirect details ----|
    [use secret to sign & check redirects on both peers]
       |                                   .

First visit of Service ever:

    Client                Service                AuthService
        |                    .                        .
        |------ visit ------>|                        .
        .      [create signed redirect from template]
        |<---- redirect -----|                        .
        |----- provide signed payload --------------->|
        .                    .                     [verify sig]
        .                    .     [drive user registration/login process]
        .                    .       [ask user for access]
        |<---- redirect user back --------------------|
        |-- signed result -->|                        .
        .              [verify sig]                   .
        .                    |-- register session --->|
        .                    |<-------- OK -----------|
        |<--- logged in -----|                        .
    [use of Service]         .                        .
        .               [periodic renew]              .
        .                    |--- renew session ----->|
        .                    |<-------- OK -----------|
    [use of Service]         .                        .    
        |---- logout ------->|                        .
        .                    |----- end session ----->|
        .                    |<-------- OK -----------|
        |<--- logged out ----|                        .
        |                    .                        .

Second visit of Service from known device:

    Client          Service                 AuthService
        |               .                        .
        |---- visit --->|                        .
        .        [check known user]              .
        .               |--- renew session ----->|
        .               |<-------- OK -----------|
        |<- logged in --|                        .
    [use of Service]    .                        .
        |               .                        .
    
Immediate logout:

    Service                 AuthService
       |                          .
       |---- listen for events -->|
       .                          .
       .                          .
       |<--- invalidate session --|
    [invalidate local session]    .
       .                          .
       
Foreign users (local AuthService acts as proxy):

    Client          Service                 AuthService         ForeignAuthService
        .               .                        .                      .
        .               .                        |---- register self -->|
        .               .                        .                      .
        .               |-- listen for events -->|                      .
        .               .                        |- listen for events ->|
        |---- visit --->|                        .                      .
        .           [unknown user]               .                      .
        |<-- redirect --|                        .                      .
        |--- provide signed payload ------------>|                      .
        .               .                     [verify sig]              .
        .               .                [user chooses extral auth]     .
        |<----- redirect to foreign -------------|                      .
        |-------------------------- provide signed payload ------------>|
        .               .                        .                [verify sig]
        .               .                        .              [process user auth]
        |<--------- return back local AuthService ----------------------|
        |--- provide signed return ------------->|                      .
        .               .                   [verify sig]                .
        .               .                        |-- register session ->|
        .               .                        |<------ OK -----------|
        |<-- return back Service ----------------|                      .
        |-- get back -->|                        .                      .
        .          [verify sig]                  .                      .
        .               |-- register session --->|                      .
        .               |<-------- OK -----------|                      .
        |<- logged in --|                        .                      .
    [use of Service]    .                        .                      .
        |               .                        .                      .


### 2.3.4. Access on behalf of user

On-behalf-of calls is standard feature of [FTN3][].

Each Service registers a list of generic access descriptors it provides
which can be granted by user to another user(service).

Another Service creates Access Request Templates as a list of generic
access descriptors it wants to ask from User. When user grants the 
required access, Service can call another Service on behalf of user.

It's assumed that user has full access to own resources
protected only by required security levels. User can grant resource access
to another user or Service based on Access Control descriptors.

Local user:

    Client         Service1     Service2                 AuthService
        .             .             .                         .
        .             .             |- register descriptors ->|
        .             .             .                         .
        .             |-- create template ------------------->|
        .             .             .                         .
        |-- visit --->|             .                         .
        |<- redirect -|             .                         .
        |----- provide signed payload ----------------------->|
        .             .             .                   [verify sig]
        .             .             .                    [ask user]
        .             .             .                  [grant access]
        |<----- signed redirect back -------------------------|
        |- return --->|             .                         .
        .        [verify sig]       .                         .
        .             |- API call ->|                         .
        .             .     [request checking]                .
        .             .             |---- checkAuth() ------->|
        .             .             |--- checkAccess() ------>|
        .             .     [request processing]              .
        .             |<-- result --|                         .
        .             .             .                         .
        
Foreign user access just adds extra complexity:

1. Both user authentication and other user/service authorization is done
    in foreign AuthService
2. User can review & control all grants in home services
3. Local to Service AccessControl has to consult with foreign AccessControl
    for access, cache it and revoke events similar to user sessions.
4. AuthService acts as proxy:
    - authoritative to local Service
    - represents Service for foreign AuthService
    - consults and keep in sync with foreign

### 2.3.5. Exceptional operation confirmation

In many cases Service needs to securely confirm some action like bank transfer
approval. For that reason, Service creates special confirmation request
in AuthService and redirects the user there.

    Client               Service                 AuthService
        |                   .                         .
        |- request action ->|                         .
        .                   |- prepare confirmation ->|
        .                   .               [store with timeout]
        .                   |<-- provide URL ---------|
        |<---- redirect ----|                         .
        |------ use the AuthService URL ------------->|
        .                   .            [ask user confirmation]
        .                   .                  [store result]
        |<---- signed redirect back ------------------|
        |-- return -------->|                         .
        .               [verify sig]                  .
        .                   |-- verify confirmation ->|
        .                   |<----- OK ---------------|
        .            [complete action]                .
        .                   .                         .
    


## 2.4. AuthService and scope of identification

The scope of AuthService is arbitrary - it is formed by AuthService itself.
However, AuthService should have a single domain name which is used as
global scope identifier.

## 2.5. User identification

Each user has a unique local ID and global ID.

Local ID is arbitrary and assigned by AuthService.

Global ID based on local ID and scope name of home AuthService.
Typically, email address is the global identifier.

## 2.6. Foreign users

If the Service or Client trust different AuthServices then it is responsibility
of AuthService to establish communication to another AuthService. In such case,
Client is called *foreign AuthService user* or simply *foreign user*.

Foreign users are detected based on mismatch of associated global ID scope name and
current AuthService scope name.

Theoretically, AuthService can auto-discover and establish registration to any other
foreign AuthService. However, it may be undesired from security point of view.
So, only whitelisted foreign AuthServices should be allowed. Whitelist can be either
local or global in form of association of AuthService providers.

## 2.7. Service to Service interaction (and Service to AuthService in particular)

Each Service as logical entity assumes to have own user ID in scope of related AuthService.
Therefore, communication authentication follows the same pattern as Client-to-Service pattern.

## 2.8. Authentication assumptions

Client-to-Service and Service-to-Service communication has different natural aspects:

* Service-to-Service:
    - assumes much larger number of calls
    - requires throughput & latency efficient secure message authentication
    - should be able to update secrets periodically unattended way
    - should seamlessly transition to new secrets without service interruption
* Client-to-Services:
    - assumes roaming
    - requires multi-factor authentication per session and/or important action
    - should support authentication secret recovery self-service
    - should utilize HTTP cookie, if applicable
    - should immediately break sessions on authentication secret change or logout
* Common:
    - should avoid authentication secrets exposure in messages
    - should avoid message authentication re-use and replay attacks
    - should have separate secrets for each pair of peers in communication
    - should support additional constraints:
        - source IP address
        - x509 client certificates
        - SSH public keys

Therefore, specification is separated for Client(human) and Service(software) cases.

## 2.9. Interoperation with non-compliant AuthService scopes

There are many OpenID, OAuth, SAML and other single sign-on alternatives. Particular
AuthService may easily integrate with those.

## 2.10. Service & AuthService in single instance

It's assumed that each Service is accompanied by unified AuthService logic to
efficiently process requests on scale. Such AuthService can be either full-featured
or limited to support of only foreign users.

## 2.11. General MAC generation requirements

MAC stays for Message Authentication Code which prevents decryptable transmission of
authentication secrets and helps to ensure message integrity.

### 2.11.1 Rules of MAC payload generation

*Note 1: MAC logic must be abstract of JSON as far as possible to be efficiently used in other
message coding methods.*

*Note 2: research to be done to support TupleHash and non-JSON representation of fields as an option.*

* Payload has a tree structure and coded in JSON or any alternative format
* All keys and fields are feed to MAC generator in text representation
* Top level "sec" field is skipped
* For each nested level, starting from the very root of tree-like payload structure:
    * Key-value pairs are processed in ascending order based on Unicode comparison rules
    * Key is feed into MAC generator
    * ':' separator is feed into MAC generator
    * If value is subtree then recurse this algorithm
    * else if value is string then feed into MAC generator
    * Otherwise, feed textual JSON representation to MAC generator
    * ';' separator is feed into MAC generator

### 2.11.2. Predefined MAC algorithms

Executor may refuse to support any MAC algo and throw SecurityError.

* HMAC series are based on [HMAC][] method
    * "HMAC-MD5" - HMAC MD5 128-bit (acceptably secure, even though MD5 itself is weak)
    * "HMAC-SHA-224" - SHA v2 224-bit (acceptably secure)
    * "HMAC-SHA-256" - SHA v2 256-bit (acceptably secure)
    * "HMAC-SHA-384" - SHA v2 384-bit (acceptably secure)
    * "HMAC-SHA-512" - SHA v2 512-bit (acceptably secure)
    * "HMAC-SHA3-224" - SHA v3 224-bit (high secure at the moment)
    * "HMAC-SHA3-256" - SHA v3 256-bit (high secure at the moment)
    * "HMAC-SHA3-384" - SHA v3 384-bit (high secure at the moment)
    * "HMAC-SHA3-512" - SHA v3 512-bit (high secure at the moment)
* KMAC series for SHA v3 - more efficient than HMAC
    * "KMAC128" - Keccak MAC 128-bit (high secure at the moment)
    * "KMAC256" - Keccak MAC 256-bit (high secure at the moment)

### 2.11.3. Response "sec" field with MAC

If request comes signed with any MAC then response must also be signed
with MAC using exactly the same secret key and MAC algorithm.

Invoker must validate response "sec" field and fail on mismatch or absence of one.

### 2.11.4. Key derivation strategies

It is called "Strategy", but not "Function" on purpose as the same KDF may be used
different ways.

#### 2.11.4.1. General derived key ID

Derived Key ID must be transmitted as Base64 encoding string without padding. Key ID or
salt should be of recommended size, if applicable.

Based on strategy, no key ID or a fixed minimal derived key ID may be used for current
version of the specification to minimize performance impact and simplify Executor's
derived key caching logic. Master Secret itself should provide enough entropy to ensure
derived key's quality. So, key update gets bound to frequency of Master Secret update.
Key derivation would be used only to get different keys based on purpose.

#### 2.11.4.2. Key purpose name

Below is list of ASCII values to use for altering key derivation logic.

* `MAC` - for message signing.
* `ENC` - for general encryption.
* `EXPOSED` - for signature generating which definitely goes through untrusted exposed
    channel (e.g. user's web browser).

#### 2.11.4.3. Performance tradeoff

In most cases, it's not feasibile to generate a new derived key for every message,
so Invoker should be able to reuse the key at own discretion.

As a defensive measure, Executor peer is allowed to reject requests, if derived key
either changes too often or used for too long. Executor should cache derived keys
for reasonable time, but still prevent their leaking outside. Executor should consider
that Invoker may be clustered with unique derived key at every node.

Executor can be configured to support only certain types of strategies named below and
to reject requests with "SecurityError" on mismatch.

#### 2.11.4.4. Key derivation strategies names

1. `HKDF0` - use [HKDF][] with empty "salt" and purpose name for "info" to
    derive unique keys per purpose from shared Master Secret.
    - empty salt should be OK with quality Master Secret
    - "prm" must not be sent or be empty
    - default for `MAC` and `EXPOSED` purpose
2. `HKDF` - use [HKDF][] with UUID for "salt" and purpose name for "info" to
    derive unique keys per purpose from shared Master Secret.
    - "salt" must be sent in "prm" field
    - default for `ENC` purpose

## 2.12. Security Levels

It's important to understand characteristics of performed user authentication in many cases.

* `Anonymous` - placeholder for not authenticated user
* `Info` - read-only access to private information
* `SafeOps` - Info + access to operation, which should not seriously compromise the system
* `PrivilegedOps` - SafeOps + access to operations, which may compromise the system. Requires SecureChannel
* `ExceptionalOps` - PrivilegedOps + access to very sensitive operations, like password change
    * At Service discretion, should be one-time access with immediate downgrade to PrivilegedOps level
* `System` - internal calls inside the same Service (can be cross-process)

## 2.13. Client fingerprints

The following fingerpints are essential to enforce extra level of protection.

* `user_agent` - refers to HTTP 'User-Agent' or similar
* `source_ip` - refers ot IPv4/IPv6 source address of Client
* `x509` - X.509 certificate, if provided by client
* `ssh_pubkey` - SSH public key, if provided by client
* `misc` - implementation-defined map
    * `flavour` - implementation type
    * any - any arbitrary field like, used ciphers or other details

## 2.14. Authentication rejection limits and blocking

The specification suggests the following limits to be enforced. Hit of the limits must
block any processing. The blocking must be done for entire period of enforcement.

* Subject of blocking:
    - IPv4/32 or IPv6/64 addresses of Client calls
        - 10 failed auth attempts in 24 hours
        - 30 failed auth attempts in 7 days
        - 100 failed auth attempts in 30 days
    - IPv4/24 or IPv6/48 addresses of Client calls
        - 100 failed auth attempts in 24 hours
        - 300 failed auth attempts in 7 days
        - 1000 failed auth attempts in 30 days
    - Untrusted User (Service) which may fake Client fingeprints for bruteforcing:
        - 100 failed auth attempts in 24 hours
        - 300 failed auth attempts in 7 days
        - 1000 failed auth attempts in 30 days
    - Verified User (Service) which may fake Client fingeprints for bruteforcing:
        - 10000 failed auth attempts in 24 hours
        - 30000 failed auth attempts in 7 hours
        - 100000 failed auth attempts in 30 hours
* Objects and actions:
    - User clear text authentication to be automatically regenerated per Service
        - 100 failed attempts in 24 hours
        - 300 failed attempts in 7 days
        - 1000 failed attempts in 30 days
        - User should be notified to retrieve and setup a new clear text secret
    - User stateless MAC authentication to be automatically regenerated
        - 1000 failed attempts in 24 hours
        - 3000 failed attempts in 7 days
        - 10000 failed attempts in 30 days
        - User should be notified to retrieve and setup a new MAC Secret
    - Master Secret to be disabled
        - 10 failed attempts in 24 hours
        - 30 failed attempts in 7 days
        - 100 failed attempts in 30 days
        - Master Secret ID should be difficult to guess UUID
        - Fallback to previous still active Master Secret can be done for
            automatic recovery
        - Otherwise, manual re-initialization is required
    - Client authentication using session token
        - Immediate session invalidation on session secret mismatch
        - Immediate session invalidation on non-IP Client fingerprints change
        - Immediate session invalidation on suspicious Client IP changes
        - Session token has to contain two parts: session ID and session secret
        - Session ID should not be easily guessable - any mismatch is a sign of attack
    - User login at AuthService
        - 1000 failed attempts in 24 hours
        - 3000 failed attempts in 7 days
        - 10000 failed attempts in 30 days

# 3. Interface

## 3.1. Common types

`Iface{`

    {
        "iface" : "futoin.auth.types",
        "version" : "{ver}",
        "ftn3rev" : "1.8",
        "imports" : [
            "futoin.types:1.0"
        ],
        "types" : {
            "LocalUserID" : "UUIDB64",
            "LocalUser" : {
                "type" : "string",
                "regex" : "^[a-zA-Z]([a-zA-Z0-9_.-]{0,30}[a-zA-Z0-9])?$"
            },
            "GlobalUserID" : "Email",
            "ClearSecret" : {
                "type" : "string",
                "minlen" : 8,
                "maxlen" : 32
            },
            "MACAlgo" : {
                "type" : "enum",
                "items" : [
                    "HMAC-MD5",
                    "HMAC-SHA-224",
                    "HMAC-SHA-256",
                    "HMAC-SHA-384",
                    "HMAC-SHA-512",
                    "HMAC-SHA3-224",
                    "HMAC-SHA3-256",
                    "HMAC-SHA3-384",
                    "HMAC-SHA3-512",
                    "KMAC128",
                    "KMAC256"
                ]
            },
            "MACSecret" : {
                "type" : "Base64",
                "minlen" : 32,
                "maxlen" : 128
            },
            "MACValue" : {
                "type" : "Base64",
                "minlen" : 1,
                "maxlen" : 128
            },
            "MACBase" : {
                "type" : "string",
                "minlen" : 8
            },
            "MasterSecretID" : "UUIDB64",
            "KeyDerivationStrategy" : {
                "type" : "enum",
                "items" : [
                    "HKDF",
                    "HKDF0"
                ]
            },
            "KeyPurpose" : {
                "type" : "enum",
                "items" : [
                    "MAC",
                    "ENC",
                    "EXPOSED"
                ]
            },
            "PublicKeyType" : {
                "type" : "enum",
                "items" : [
                    "RSA-2048",
                    "RSA-4096",
                    "ED25519"
                ]
            },
            "PublicKey" : {
                "type" : "Base64",
                "minlen" : 1
            },
            "EncryptedMasterSecret" : {
                "type" : "Base64",
                "minlen" : 1
            },
            "ClientFingerprints" : {
                "type" : "map",
                "fields" : {
                    "user_agent" : {
                        "type" : "string",
                        "optional" : true
                    },
                    "source_ip" : {
                        "type" : "IPAddress",
                        "optional" : true
                    },
                    "x509" : {
                        "type" : "Base64",
                        "optional" : true
                    },
                    "ssh_pubkey" : {
                        "type" : "string",
                        "optional" : true
                    },
                    "misc" : {
                        "type" : "map",
                        "optional" : true
                    }
                }
            }
        }
    }

`}Iface`

## 3.2. AuthService management

`Iface{`

    {
        "iface" : "futoin.auth.manage",
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
                    },
                    "master_auth" : {
                        "type" : "boolean",
                        "default" : true
                    },
                    "master_auto_reg" : {
                        "type" : "boolean",
                        "default" : false
                    }
                },
                "result" : "boolean"
            },
            "genConfig" : {
                "result" : {
                    "domain" : "Domain",
                    "clear_auth" : "boolean",
                    "mac_auth" : "boolean",
                    "master_auth" : "boolean",
                    "master_auto_reg" : "boolean"
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
            }
        },
        "requires" : [
            "SecureChannel",
            "MessageSignature"
        ]
    }

`}Iface`



[hmac]: http://www.ietf.org/rfc/rfc2104.txt "RFC2104 HMAC"
[ssh-pubkey]: http://www.ietf.org/rfc/rfc4716.txt "RFC4716 The Secure Shell (SSH) Public Key File Format"
[FTN3]: ./ftn3_iface_definition.md

=END OF SPEC=
