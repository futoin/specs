<pre>
FTN8: FutoIn Security Concept
Version: 0.4DV
Date: 2018-05-04
Copyright: 2014-2018 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v0.3 - 2018-05-04 - Andrey Galkin
    - CHANGED: rewritten general guidelines for better readability.
    - CHANGED: minor revise.
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

### 2.1.1. Exposed data best practices

External parties to particular system must never hold internal security-related
data even if it is encrypted and/or signed to prevent theoritical falsification
attacks in the future.

Notes:

- User passwords and similar secrets are not internal data - they belong to user.
- Session tokens must hold only session ID with session-hardening secrets - no other info.
    - Extra session-hardening secret must be used only to detect and protect from
      session ID brute-forcing attacks.
- The same applies to data stored only for informational purpose as it may be used for
  authorization purpose by mistake of inexperienced/incompetent developers.
    - If that is still required then related object must be tokenized and obfuscated to minimize
      possible harm.

### 2.1.2. Brute-force prevention

Any authentication and authorization functionality should  be accounted for failures per exercised
security resource (e.g. user password, session ID, signing key, etc.). System must forcibly disable
such resource at reasonable failure count threshold to prevent the attack succeeding.

As such behavior allows easy Denial-of-Service for target resource, System must block attackers earlier
than it blocks the target. Also, target identifiers must not be easily guessable (e.g. avoid sequential
or derived identifiers).

All thresholds must be specific to time period like day, week, month, quarter, year.

Notes:

- Once threshold limit is reached, related object (password, key, session ID, etc.) must be destroyed to prevent even legit use.
- Consider using UUID v4 whenever possible.


### 2.1.3. Filtering attackers

Each unsuccessful attempt to exercise security operation must be accounted per client source address
and other meaningful identifiers. Such accounting should be also aggregated based on network range and/or
domain to protect from distributed attacks.

However, such behavior can harm legit users. Therefore, complete blocking should be the last resort.
Instead, System should take more light measurements like throttling requests per minute and preliminary
verification if session is run by real human. Such light measurements are mandatory, if System is aware
of legit user.

Notes:

- Attackers must be blocked by source address first of all.
- Authenticated attackers must be blocked by user ID.


### 2.1.4. Online verification

Online verification must always be enforced even if it complicates processing, imposes scalability issues
and/or increases latency. FutoIn Security Concept is strictly against any token-based authentication where
not trusted party like Client is part of communication channel between Service and AuthService.

Caching is essential to achieve performance and scalability similar to pure token-based approaches. However,
such caching is allowed only if reliable cache invalidation is implemented.

### 2.2.5. Centralized authentication and authorization

All fully compliant Services must use AuthService for security meaningful decisions.

Such AuthService must have allow a complete overview and control of granted accesses in the given Service
or on behalf of the User.

### 2.1.6. Rotation of secrets

All secrets used in automated contexts should be rotated based on both usage time and usage count thresholds.
This is a simple measurement for possible leak of secrets.

User-defined secrets like password, historical One-Time-Password solution and similar secrets are not required
to be rotated.

### 2.1.7. Prevent indirect information exposure

Some "not important" characteristics may be used to plan attacks and/or to extract businness secrets.

- Do not use sequential IDs
- Do not expose object existence on error
    - Always throw general "SecurityError" with generic error info
    - Prevent time-based attacks - make consistent delays on any SecurityError
- Do not use descriptive identifiers in tokens
- Prevent attacks which expose ID existence on authentication

### 2.1.8. Forward Secrecy

General rules well-known cryptography practices apply here:

- Use modern TLS, SSH, IPSec or other type of secure channel with  perfect forward secrecy characteristics.
- Use only secure symmetric key exchange.
- Use derived keys for each use occurrence.
    * Use derivation with extra parameter when extra safety is required
      (e.g. key serial number for derived encryption keys)
- Use End-to-End Encryption API for sensitive information exchange even if it is already done
  through secure channel.

## 2.2. Security Contexts

There are three major security contexts:

* **Service** - Both execution environment and executable code is 
  under full control of the owner.
    - This security context exists on servers.
    - Service is a logical unit represented by a union of related
        FutoIn specs provided by one or many related end-points.
* **Client** - Execution environment is under control of owner, but
  executable code is loaded from Service.
* **AuthService** - A special authentication & authorization service
  trusted by Service and/or by Client.

Each Service and each Client must trust only one AuthService.

The standard authorization mechanism does not allow Client code to access
protected resources in another Service directly. Such feature may be
implemented as sub-spec.

In addition, the following optional services exist:

* **DefenseSystem** - A special service which helps to detect
  and fight attacks. Its context is implementation-defined.

## 2.3. Holistic pictures

### 2.3.1. Request Processing

It may look as too much overhead for a single request processing, but any decent system does
exactly the same in fact: security processing is centralized in some application module.

FutoIn converts modules to )micro-)services by fundamental design. There should be efficient
in-process calling mechanism to minimize penalties.

It is known that symmetric cryptography is much faster to process than asymmetric. Therefore,
message signing is based on automatically rotated shared symmetric secrets which unique to each
pair of peers. However, asymmetric cryptography is used for key rotation to ensure forward secrecy.


    Client         Service        AuthService   DefenseSystem
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
are used requiring a preshared secret and secure updates
of that.

Initial manual registration:

    Operator                AuthService
        |                        .
        |--- register Service -->|
        .                 [gen initial secret]
        |<-- clear text secret --|
    [manually configures Service] .
        .                        .

Initial automatic registration through secure channel, if allowed:

    Service                            AuthService
       |                                   .
    [gen temporary assymetric key]         .
       |----- request registration ------->|
       .                [depend on transport's MitM security]
       .                    [save request for approval]
       |<----- provide ticket ID ----------|
       .                                   .
    [put ticket ID in .well-known]         |
       .                                   .
       |-- try to complete registration -->|
       .                            [ticket is not validated]
       |<-- HTTPS GET .well-known ticket --|
       |------- return ticket ID --------->|
       .                            [ticket is validated]
       |<- "pending" or "rejected" error --|
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

User is generic term for security subject. It can be human, specific service,
group or even some object.

Each Service registers a list of generic access descriptors it provides
which can be granted by User to another User (Service).

Another Service creates Access Request Templates as a list of generic
access descriptors it wants to ask from User. When User grants the 
required access, Service can call another Service on behalf of the User.

It's assumed that user has full access to own resources
protected only by required security levels. User can grant resource access
to another User (Service) based on Access Control descriptors.

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
    in foreign AuthService.
2. User can review & control all grants in home services.
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

Local ID is arbitrary and assigned by AuthService. Base64-coded UUID without
padding is suggested.

Global ID based on local ID and scope name of home AuthService.
Typically, email address is the global identifier for users and
fully qualified domain name is the global identifier for services.

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

MAC stays for Message Authentication Code which helps to ensure message integrity.

### 2.11.1 Rules of MAC payload generation

*Note 1: MAC logic must be abstract of JSON as far as possible to be efficiently used in other
message coding methods.*

*Note 2: research to be done to support TupleHash and non-JSON representation of fields as an option.*

*Note 3: for performance and simplification a special FutoIn interface to be created for
message-in-signed-message-field approach.*

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
    * `HMD5` - HMAC MD5 128-bit (acceptably secure, even though MD5 itself is weak)
    * `HS256` - SHA v2 256-bit (acceptably secure)
    * `HS384` - SHA v2 384-bit (acceptably secure)
    * `HS512` - SHA v2 512-bit (acceptably secure)
* KMAC series for SHA v3 - more efficient than HMAC
    * `KMAC128` - Keccak MAC 128-bit (high secure at the moment)
    * `KMAC256` - Keccak MAC 256-bit (high secure at the moment)
    
*Note: current suggested default is either `HS256` or `HS512-256`*

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

In most cases, it's not feasible to generate a new derived key for every message,
so Invoker should be able to reuse the key at own discretion.

As a defensive measure, Executor peer is allowed to reject requests, if derived key
either changes too often or used for too long. Executor should cache derived keys
for reasonable time, but still prevent their leaking outside. Executor should consider
that Invoker may be clustered with unique derived key at every node.

Executor can be configured to support only certain types of strategies named below and
to reject requests with "SecurityError" on mismatch.

#### 2.11.4.4. Key derivation strategies names

1. `HKDF256` - HKDF with SHA-256
1. `HKDF512` - HKDF with SHA-512


#### 2.11.4.5. HKDF notes

[HKDF][] is well-known modern method which has the following parameters: hash function,
salt and info.

- Format `salt` as `{global user ID}:{purpose}`, where global user id is the Executor peer.
- Optional `prm` is passed to `info` parameter.
    - For `MAC` and `EXPOSED` case, use of current ISO
        date time in `YYYYMMDD` or more precise format is suggested.
    - For `ENC` case, use of UUID per encryption is suggested.
- Key length must match the length of master key
- Implementation caching should limit maximum number of derived keys
    per Master Secret ID and Global User ID pair.
- Defense system should be intelligent enough to protect from brute-forcing:
    - AuthService should blacklist offending Service,
    - Service should blacklist offending Client before that.


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
* `source_ip` - refers to IPv4/IPv6 source address of Client
* `x509` - X.509 certificate, if provided by client
* `ssh_pubkey` - SSH public key, if provided by client
* `client_token` - Service-specific identification of the Client device
    - the one should not be stored in clear on the device, but encrypted by
        a separate secret known only to the Service itself
* `misc` - implementation-defined map
    * `flavour` - implementation type
    * any - any arbitrary field like, used ciphers or other details

## 2.14. Authentication rejection limits and blocking

The specification suggests the following limits to be enforced. Hit of the limits must
block any processing. The blocking must be done for entire period of enforcement.

Advanced System should have more light protection measures first to protect legit user access.

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
    - Second-level domain for service auto-registrations:
        - 10 service auto-registrations in 30 days

### 2.15. Manage service events

* `USR_NEW` - new user is created
    * `local_id` - local user ID
* `USR_MOD` - user info updated
    * `local_id` - local user ID

# 3. Interface

## 3.1. Common types

`Iface{`

    {
        "iface" : "futoin.auth.types",
        "version" : "{ver}",
        "ftn3rev" : "1.9",
        "imports" : [
            "futoin.types:1.0"
        ],
        "types" : {
            "LocalUserID" : "UUIDB64",
            "LocalUser" : {
                "type" : "string",
                "regex" : "^[a-zA-Z]([a-zA-Z0-9_.-]{0,30}[a-zA-Z0-9])?$"
            },
            "LocalService" : "LocalUser",
            "GlobalService" : {
                "type" : "Domain",
                "maxlen" : 128
            },
            "GlobalUser" : {
                "type" : "Email",
                "maxlen" : 128
            },
            "GlobalUserID" : [ "GlobalUser", "GlobalService" ],
            "DomainList" : {
                "type" : "array",
                "elemtype" : "Domain",
                "minlen" : 1
            },
            "MACAlgo" : {
                "type" : "enum",
                "items" : [
                    "HMD5",
                    "HS256",
                    "HS384",
                    "HS512",
                    "KMAC128",
                    "KMAC256"
                ]
            },
            "Password" : {
                "type" : "string",
                "minlen" : 8,
                "maxlen" : 32
            },
            "PasswordLength" : {
                "type" : "integer",
                "min" : 8,
                "max" : 32
            },
            "KeyBits" : {
                "type" : "enum",
                "items" : [256, 512]
            },
            "MACKey" : {
                "type": "Base64",
                "minlen" : 42,
                "maxlen" : 87
            },
            "StatelessSecret": [ "Password", "MACKey" ],
            "MACValue" : {
                "type" : "Base64",
                "minlen" : 1,
                "maxlen" : 128
            },
            "MACBase" : {
                "type" : "data",
                "minlen" : 8
            },
            "MasterSecretID" : "UUIDB64",
            "MasterScope" : "Domain",
            "KeyDerivationStrategy" : {
                "type" : "enum",
                "items" : [
                    "HKDF256",
                    "HKDF512"
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
            "ExchangeKeyType" : {
                "type" : "enum",
                "items" : [
                    "RSA",
                    "X25519",
                    "X448"
                ]
            },
            "ExchangeKey" : {
                "type" : "Base64",
                "minlen" : 1,
                "maxlen" : 20000
            },
            "EncryptedKey" : {
                "type" : "Base64",
                "minlen" : 1,
                "maxlen" : 1000
            },
            "EncryptedMasterSecret" : "EncryptedKey",
            "UserAgent" : {
                "type" : "string",
                "maxlen" : 256
            },
            "X509Cert" : {
                "type" : "Base64",
                "maxlen" : 20000
            },
            "SSHPubKey" : {
                "type" : "string",
                "maxlen" : 1000
            },
            "ClientToken" : {
                "type" : "Base64",
                "maxlen" : 342,
                "desc" : "Unique per Service per Client device persistent token"
            },
            "ClientFingerprints" : {
                "type" : "map",
                "fields" : {
                    "user_agent" : {
                        "type" : "UserAgent",
                        "optional" : true
                    },
                    "source_ip" : {
                        "type" : "IPAddress",
                        "optional" : true
                    },
                    "x509" : {
                        "type" : "X509Cert",
                        "optional" : true
                    },
                    "ssh_pubkey" : {
                        "type" : "SSHPubKey",
                        "optional" : true
                    },
                    "client_token" : {
                        "type" : "ClientToken",
                        "optional" : true
                    },
                    "misc" : {
                        "type" : "map",
                        "optional" : true
                    }
                }
            },
            "AuthInfo" : {
                "type" : "map",
                "fields" : {
                    "local_id" : "LocalUserID",
                    "global_id" : "GlobalUserID"
                }
            },
            "RedirectURL" : {
                "type" : "string",
                "regex" : "^https?://[a-z0-9-]+(\\.[a-z0-9-]+)*\\.[a-z]{2,}/[a-Z0-9_/-]*(\\?[a-Z][a-Z0-9]*=)?$",
                "maxlen" : 128
            },
            "ResourceURL" : {
                "type" : "string",
                "regex" : "^https?://[a-z0-9-]+(\\.[a-z0-9-]+)*\\.[a-z]{2,}/[a-Z0-9_/?=%&;.-]*$",
                "maxlen" : 128
            },
            "ParamConstraint" : {
                "type" : "map",
                "elemtype" : "array"
            },
            "AccessControlDescriptor" : {
                "type" : "map",
                "fields" : {
                    "iface" : {
                        "type" : "FTNFace",
                        "optional" : true
                    },
                    "ver" : {
                        "type" : "FTNVersion",
                        "optional" : true
                    },
                    "func" : {
                        "type" : "FTNFunction",
                        "optional" : true
                    },
                    "params" : {
                        "type" : "ParamConstraint",
                        "optional" : true,
                        "desc": "Named paramater must match one of the values"
                    }
                },
                "desc" : "Granted API access constraints in scope of arbitrary Service"
            },
            "AccessControlDescriptorList" : {
                "type" : "array",
                "elemtype" : "AccessControlDescriptor",
                "desc" : "List of granted API access in scope of arbitrary Service"
            },
            "AccessGroupName" : {
                "type" : "GenericIdentifier",
                "maxlen" : 32,
                "desc" : "Service-specific arbitrary ACD grouping identifier"
            },
            "AccessGroup" : {
                "type" : "map",
                "fields" : {
                    "id" : "AccessGroupName",
                    "name" : "ItemTranslations",
                    "desc" : "ItemTranslations",
                    "acds" : "AccessControlDescriptorList",
                    "icon" : "ResourceURL"
                },
                "desc" : "Services-specific arbitrary ACD grouping definition"
            },
            "AccessGroupList" : {
                "type" : "array",
                "elemtype" : "ServiceAccessGroup",
                "desc" : "List of Service-specific ACD groupings"
            },
            "ServiceAccessGroup" : {
                "type" : "map",
                "fields" : {
                    "service" : "GlobalService",
                    "access_group" : "AccessGroupName"
                },
                "desc" : "Global pointer to ACD group of specific Service"
            },
            "ServiceAccessGroupList" : {
                "type" : "array",
                "elemtype" : "ServiceAccessGroup",
                "desc" : "List of global pointers to Service-specific ACD groups"
            }
        }
    }

`}Iface`

## 3.2. AuthService management

`Iface{`

    {
        "iface" : "futoin.auth.manage",
        "version" : "{ver}",
        "ftn3rev" : "1.9",
        "imports" : [
            "futoin.ping:1.0",
            "futoin.auth.types:{ver}"
        ],
        "funcs" : {
            "setup" : {
                "params" : {
                    "domains" : "DomainList",
                    "clear_auth" : {
                        "type" : "boolean",
                        "default" : null
                    },
                    "mac_auth" : {
                        "type" : "boolean",
                        "default" : null
                    },
                    "master_auth" : {
                        "type" : "boolean",
                        "default" : null
                    },
                    "master_auto_reg" : {
                        "type" : "boolean",
                        "default" : null
                    },
                    "auth_service" : {
                        "type" : "boolean",
                        "default" : null
                    },
                    "password_len" : {
                        "type" : "PasswordLength",
                        "default" : null
                    },
                    "key_bits" : {
                        "type" : "KeyBits",
                        "default" : null
                    },
                    "def_user_ms_max" : {
                        "type" : "NotNegativeInteger",
                        "default" : null
                    },
                    "def_service_ms_max" : {
                        "type" : "NotNegativeInteger",
                        "default" : null
                    }
                },
                "result" : "boolean",
                "seclvl" : "System"
            },
            "genConfig" : {
                "result" : {
                    "domains" : "DomainList",
                    "clear_auth" : "boolean",
                    "mac_auth" : "boolean",
                    "master_auth" : "boolean",
                    "master_auto_reg" : "boolean",
                    "auth_service" : "boolean",
                    "password_len" : "PasswordLength",
                    "key_bits" : "KeyBits",
                    "def_user_ms_max" : "NotNegativeInteger",
                    "def_service_ms_max" : "NotNegativeInteger"
                },
                "seclvl" : "System"
            },
            "ensureUser" : {
                "params" : {
                    "user" : "LocalUser",
                    "domain" : "GlobalService"
                },
                "result" : "LocalUserID",
                "seclvl" : "System"
            },
            "ensureService" : {
                "params" : {
                    "hostname" : "LocalService",
                    "domain" : "GlobalService"
                },
                "result" : "LocalUserID",
                "seclvl" : "System"
            },
            "getUserInfo" : {
                "params" : {
                    "local_id" : "LocalUserID"
                },
                "result" : {
                    "local_id" : "LocalUserID",
                    "global_id" : "GlobalUserID",
                    "is_local" : "boolean",
                    "is_enabled" : "boolean",
                    "is_service" : "boolean",
                    "ms_max" : "NotNegativeInteger",
                    "ds_max" : "NotNegativeInteger",
                    "created" : "Timestamp",
                    "updated" : "Timestamp"
                },
                "throws" : [
                    "UnknownUser"
                ],
                "seclvl" : "System"
            },
            "setUserInfo" : {
                "params" : {
                    "local_id" : "LocalUserID",
                    "is_enabled" : {
                        "type": "boolean",
                        "default": null
                    },
                    "ms_max" : {
                        "type": "NotNegativeInteger",
                        "default": null
                    },
                    "ds_max" : {
                        "type": "NotNegativeInteger",
                        "default": null
                    }
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



[hmac]: http://www.ietf.org/rfc/rfc2104.txt "RFC2104 HMAC"
[ssh-pubkey]: http://www.ietf.org/rfc/rfc4716.txt "RFC4716 The Secure Shell (SSH) Public Key File Format"
[FTN3]: ./ftn3_iface_definition.md

=END OF SPEC=
