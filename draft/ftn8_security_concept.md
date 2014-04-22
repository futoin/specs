<pre>
FTN3: FutoIn Security Concept
Version: 0.DV
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# Warning

* Unfortunately. At the moment of writing this specification, the author
knows quite little about Security to judge the strength of proposed algorithms.
Every single part of that requires deep analysis of experts. *

# 1. Intro

Security concept is required to build a unified authentication and
authorization model across security domains with separate control
in open environment like internet.

There is no global trusted party is allowed. Chain of trust must be
fully distributed.

## 1.1. Security Contexts

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

## 1.2. Service and AuthService interaction

### 1.2.1. Establishing interaction
* Service must be able to self-register against any AuthService it trusts (only one)
    providing Service callback URL and initial shared secret (true randomly generated)
* AuthService must verify registration request through provided callback
** AuthService must reject non-secure callback connection in open environment
** Verification is performed through shared secret rotation

### 1.2.2. Shared secret

* There must be a persistent shared secret between Service and AuthService
* Special considerations are required as some messages can be passed
    through insecure third party (e.g Client), requiring encryption or
    at least verification to prevent certain type of attacks
* AuthService is responsible for shared secret rotation
** Every shared secret must have a sequential ID
** The previous shared secret must be active for transition period
    specified by AuthService and then discarded
* Shared secret must not be used for any encryption directly
** A derived key must be generated
** Derived can be re-used at any peer discretion based on Severity vs. Performance considerations.
*** There must be a limit imposed for total count of derived key reuse on each side
* So, each message must contain shared secret ID, derived key ID and actual encrypted data/hmac
** Shared secret ID is overflowing monotonically incrementing hexdigit value in range 0-F
** Derived key ID is in similar range 000-FFF
* Key management policy is out of scope of this specification


## 1.3. User authentication





* Auth by Login and clear text Pass
** Login is globally unique (with domain name)
** Pass - is specialized for each service (not a global one) - must be enforced by AuthService
** Generally, allowed only for cases of process automation with HTTP Basic authentication or similar clear text
** This type is NOT allowed for foreign AuthService users

* Auth by credentials at AuthService
** Should be most common token-based 3 peer authentication
** Service asks Client to provide logon token
** Client authenticated with AuthService, if not already done
** Client asks AuthService to generate and return logon token for specific Service
** Client provides token to Service
** Service validates token against AuthService
** Note: Client and Service may talk to different AuthServices, which commuinication in background transparently.

* Auth by public key
** Service requests client sertificate using CA certificate provided by AuthService
** Service gets user name by Client's certificate and then checks access against AuthService (also checks for revocation)
** This type is NOT allowed for foreign users

* Auth by credentials types
** Simple Login/clear-text-pass over secure connection
** Login/digest-Pass over insecure or secure connection
** Certificate-based authentication
** Code card or code calculator based authentication
** mix of above
** Type of verification can be specific to Service and access level type

* Predefined auth security levels - each Service determines one
** Info - read-only access to private information
** SafeOps - Info + access to operation, which should not seriously compromise the system
** PrivilegedOps - SafeOps + access to operations, which may compromise the system
** ExceptionalOps - PrivilegedOps + access to very sensitive operations, like password change
*** At Service discretion, should be one-time access with immediate invalidation after use

* Predefined user information fields, which can be requests for exposure from AuthService to Service
** FirstName
** FullName
** DateOfBirth
** TimeOfBirth
** ContactEmail
** ContactPhone
** HomeAddress
** WorkAddress
** Citizenship
** GovernmentRegID
** AvatarURL



* Service registration against AuthService
** Service must be able to self-register self against any AuthService it trusts (many-to-one AuthService)
** AuthService must verify registration request through Service callback
** There must be established shared secret between AuthService and Service, which should be used as a first-level
    of defense in encryption of data passed through Client. Shared secret must be a sort of Master Key or Base Derivation Key
    - it must not be used to encrypt data directly to minimize effect of compromised encryption key for single message.
    AuthService must periodically trigger shared secret rotation. The previous shared secret must still be workable
    for a short transition period and then detected as deprecated.
** Service must accept key rotation requests from AuthService
** Service must accept user invalidation event
*** Service must re-verify all active user sessions on any subsequent request from Client or earlier, if possible
** AuthService should be able to act as simple Service when it validates User against foreign AuthService
*** For security reason, only requests from Admin-allowed Services must be forwarded to foreign AuthServices

* Defense systems
** Limit number of any failures at every node. Security is common responsibility.
** Services must detect attacking Clients and Services and deny access before affecting other services (e.g. AuthService)
** Type of limits:
*** Requests per period from the same client/host/network 
*** Requests by type per period from --""--
*** Number of security failures from --""--
** Dynamically set limits
*** AuthService can individually rise limits per Service depending on number of active users


