<pre>
FTN8.3: FutoIn Security Concept - Client Authentication
Version: 0.4DV
Date: 2018-02-27
Copyright: 2014-2018 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v0.3 - 2018-02-27 - Andrey Galkin
    - NEW: local session ID suggestion
* v0.2 - 2017-12-30 - Andrey Galkin
    - CHANGED: heavily revised & split into sub-specs
    - NEW: Client Single Sign-On
* v0.1 - 2014-06-03 - Andrey Galkin
    - Initial draft

# 1. Intro

This sub-specification of [FTN8](./ftn8_security_concept.md) covers
Client authentication and Service authorization.

Client is assumed to be a software under control of User.
User is a living being like human.

The ultimate goal is to concentrate primary User and Client authentication logic
in AuthService as defined in the main spec while Service itself has minimal
responsibility.

# 2. Concept

## 2.1. User registration

There is an _open_ list of possible use cases:

1. By adminstrator of AuthService.
2. Via self-registration form.
3. By Service which creates users on demand.

## 2.2. Client authentication and sessions

### 2.2.1. Authentication of Client requests

At least for HTTP-based Clients, there is doubtful security of using
stateless or MAC-based request signing authentication as modern browsers
support protection of cookies from exposure to applications on page.

Therefore, this sub-spec is focused on cookie-based authentication. The cookie
must be bound to particular Service. It must not be possible to re-use it in
other Service.

1. Each non-anonymous request must be undoubtedly associated with User account.
    - Especially important when single Client session has multiple User sessions.
    - Selection of active session token is responsibility of Service implementation.
        - One strategy is to switch profiles to always have a single active token:
            * It may be dangerous when some of the windows/tabs is in outdated state.
        - Another strategy, is to identify sessions in API.
            * Actual API should be agnostics to multi-sessions.
            * So, prefer a separate API endpoint associated with cookie index.
    - The session token generation and validation is duty of AuthService.
2. Service passes active session token to AuthService.
3. AuthService does authentication implementation-defined way:
    - User must be active,
    - User session must still be valid.
    - For performance and scalability reasons, local proxy AuthService can be
        used, if it ensures proper global session invalidation.
4. AuthService returns user local and global IDs for further processing
    - otherwise, `PleaseReauth` standard error is thrown

### 2.2.2. `PleaseReauth` handling in Client code

1. Client must immediately request signed redirect URL for login page.
2. Client must follow the URL as is.
2. Upon successful authentication and return to Service, implementation
    may restore session state and continue execution as if no
    interruption occured.

*Note: this logic does not apply to Service-to-Service calls*

### 2.2.3. User authentication in Client

1. If Client comes from Service redirect (Auth Query):
    - validate Service signature first
2. Client passes implementation-defined authentication procedure on AuthService page.
3. HTTP session cookie or its equivalent may be set on Client in scope of AuthService.
    - Optional persistent cookie may be set, implementation-defined.
3. If the Service has not been Authorized to access user's resource yet then
    user is prompted for that.
3. If Client comes from Service redirect (Auth Query):
    - Client is redirected back with "session start token"
    - Client gets back to Service
    - Service verifies redirect signature and starts new user session with AuthService
        using the start token
    - AuthService returns new session token and session persistence requirements
    - HTTP cookie or its equivalent is set on Client based on response details

#### 2.2.3.1. "session token" vs. "session start token"

* Session start token:
    - is exposed in redirect URLs,
    - must not be stored in cookie,
    - must be used only for a tiny period of new session initiation,
    - must not be re-usable - one-time policy,
    - must be bound to specific Client fingerprints and
        NOT allow source address roaming.
* Session token:
    - must never be exposed anywhere except for HTTP headers (HTTP-only cookie policy),
    - assumed to be stored in cookie,
    - must be used for entire User [persistent] session,
    - must not be re-usable once session is invalidated,
    - must be ignored, if HTTP "Referer" header mismatches allowed URLs,
    - must be bound to specific Client fingerprints, but
        MAY allow source address roaming.
* Both:
    - must be bound to target Service.

### 2.2.4. User session persistence

* Depends on AuthService implementation and/or configuration,
* Should have absolute time-to-live to require re-authentication (e.g. day, week, month, etc.),
* May support "remember me" logic,
* Should have idle timeout for automatic logout, if not "remember me",
* Should be stored and survive Client shutdown, if "remember me" logic is activated,
* May be invalidated at any time, if AuthService and/or DefenseService detect suspicious activity.

### 2.2.5. Multiple User sessions in the same Client

It's assumed that single Client can have multiple User sessions at the same time.

Therefore:

1. Both Service and AuthService must be aware of possible multiple session cases.
2. Login as different user must always be available to add additional sessions,
    unless there are opposite business requirements - prevention of multiple accounts.
3. If multiple user sessions are authenticated in Client then current
    User selection must be available.

### 2.2.5. Sessions of foreign users

1. Foreign user's home AuthService must be aware of all related sessions and be able to invalidate them.
1. Service-local AuthService must listen to foreign user updates from user's home AuthService.

More details are provided in FTN8.6 sub-spec.


## 2.3. Service Authorization

More details of Service authorization to access User's resources on different Services
is described in the main FTN8 spec and FTN8.4 sub-spec.

### 2.3.1. Auth Queries from Client by Service through AuthService

"Auth Query" stays both for "Authentication" and for "Authorization" query. The second
always depends on the first one, but plain authentication query without asking for any
resource authorization can be done. In scope of the spec, User authentication can be
seen as authorization of Service to get basic User's local and global ID.

User private information available in AuthService is accessible through dedicated interface.
So, there is no special handling compared to any other resources.

To request User authorization for some resources, Service may request
AuthService to ask User to grant access of owned and/or controlled resources
in another location.

The important aspects:

1. Service must have pre-existing Master Secret exchange with AuthService
2. Service/AuthService may want to protect from potential DoS attacks caused
    by other peer redirects either intentional or due to software bug or due to
    attacks from Client itself.
    - All redirects must be signed by derived key with "EXPOSED" purpose
    - Do not make direct requests to another peer for obviously faked redirects.
3. AuthService must ask user for actions initiated by Service:
    - Only if query really comes from Service based on redirect signature.
    - Any Auth Query must be based on a persistent template created in advance
        by Service in AuthService.
    - Each Auth Query must have unique not reusable ID (UUID is acceptable).
    - Client redirection must only execute a known template associated with
        requesting Service.
    - Upon Client return to Service, Service must check result in AuthService.
    - Service must keep track of initiated Auth Queries to avoid obviously
        fake checks to AuthService.
    - Service must be ready for User to only partially reject Auth Query.

### 2.3.2. Auth Query signing details

1. It's assumed ServiceA and ServiceB are paired to AuthService based on Master Secret auth.
2. It's assumed `declareAccessControl()` is called by Services once per new software version.
3. It's assumed Services and AuthService are in time sync.
4. ServiceA generates a random nonce (e.g. UUID).
5. ServiceA creates `AuthQueryRequest` payload with access control descriptors of ServiceB.
6. ServiceA derives `EXPOSED` signing key from Master Secret and signed the payload with the key.
7. ServiceA uses `auth_url` concatenated with the payload encoded in Base64.
8. ServiceA redirects Clients based on result URL.
8. AuthService decodes the request payload and verifies its content:
    - DoS protection:
        - timestamp must not be older than 600 seconds.
        - pair of nonce value and template ID must not be seen in the expected age period.
    - signature must belong to the owner of AuthQuery request template.
    - AuthQuery template must be valid.
9. AuthService authenticates User, if needed.
10. AuthService asks User to approve ServiceA access, if needed.
    - The prompting can be skipped for trusted service (e.g. same company).
    - User selected language translations are used for prompting.
    - Requesting service must be shown.
    - The list of requested access groups with icons and descriptions must be shown.
    - User is asked to confirm.
11. AuthService creates `AuthQueryResponse` using new timestamp, but the same nonce and signing key.
12. AuthService redirects user to `result_url` concatenated with Base64 encoded payload.
13. ServiceA decodes the result payload and varifies its content:
    - DoS protection:
        - timestamp must not be older than 600 seconds.
        - pair of nonce value and template ID must not be seen in the expected age period.
    - signature must belong to the owner of AuthQuery request template.
    - AuthQuery template must be valid.
14. ServiceA start User session:
    - request is sent to AuthService.
    - response session token is saved in Client.
15. Optional, ServiceA can make requests to ServiceB on behalf of the user.

### 2.3.3. User session handling

1. After successful Auth Query, Service must call `startSession()`.
2. Service should call `resumeSession()` once in 10 minutes, if session is used.
3. If User is logged out from the Service then `closeSession()` must be called.
4. Service must call `resumeSession() on every client fingerprints change and/or
    service may force logout.

### 2.3.4. Session invalidation

Service should listen to AuthService events through [FTN18 Event Stream](./ftn18\_if\_eventstream.md)
interface.

* `SESS_END` - event type:
    - `local_id`
    - `global_id`
    - `session_token`

### 2.3.5. Local Session ID suggestion

Session ID must meet the following criteria:

1. Must be difficult to bruteforce/
2. Must be invalidated on detected bruteforce.
3. Invalidation on bruteforce detection must not lead to Denial of Service.
4. Must be as short as possible.

Therefore, default implementation should:

1. Use 128-bit UUID v4 as primary identifier.
2. Use 64-bit random secret for bruteforce detection.
3. Encode in Base64 for total of 32 bytes.
4. Use short session cookie identifier, like "FSI".
5. Reset cookie on invalid session to avoid its reuse.
5. Ban bruteforce attacker detected based on random secret.
6. Ban bruteforce attacker detected based on 10 session ID misses per day.
7. Progressively increase ban period based on attack recurrence: 24 hours, 7 days, 30 days.


# 3. Interface

## 3.1. Service interface

`Iface{`

    {
        "iface" : "futoin.auth.service",
        "version" : "{ver}",
        "ftn3rev" : "1.9",
        "imports" : [
            "futoin.ping:1.0",
            "futoin.auth.types:{ver}"
        ],
        "types" : {
            "TemplateName" : {
                "type" : "GenericIdentifier",
                "maxlen" : 32
            },
            "SessionStartToken" : {
                "type" : "Base64",
                "minlen" : 22,
                "maxlen" : 171
            },
            "SessionToken" : {
                "type" : "Base64",
                "minlen" : 22,
                "maxlen" : 171
            },
            "AuthQueryID" : "UUIDB64",
            "AuthQueryNonce" : {
                "type" : "Base64",
                "maxlen" : 22
            },
            "AuthQueryRequest" : {
                "type" : "map",
                "fields" : {
                    "id" : "AuthQueryID",
                    "ts" : "Timestamp",
                    "nonce" : "AuthQueryNonce",
                    "msid" : "MasterSecretID"
                }
            },
            "AuthQueryResponse" : {
                "type" : "map",
                "fields" : {
                    "token" : "SessionStartToken",
                    "ts" : "Timestamp",
                    "nonce" : "AuthQueryNonce",
                    "msid" : "MasterSecretID"
                }
            }
        },
        "funcs" : {
            "declareAccessControl" : {
                "params" : {
                    "access_groups" : "AccessGroupList"
                },
                "result" : "boolean"
            },
            "authQueryTemplate" : {
                "params" : {
                    "name" : "TemplateName",
                    "acds" : "ServiceAccessGroupList",
                    "result_url" : "RedirectURL"
                },
                "result" : {
                    "id" : "AuthQueryID",
                    "auth_url" : "RedirectURL"
                },
                "throws" : [
                    "SecurityError"
                ]
            },
            "startSession" : {
                "params" : {
                    "start_token" : "SessionStartToken",
                    "client" : "ClientFingerprints"
                },
                "result" : {
                    "token" : "SessionToken",
                    "info" : "AuthInfo"
                },
                "throws" : [
                    "InvalidStartToken",
                    "PleaseReauth"
                ]
            },
            "resumeSession" : {
                "params" : {
                    "start_token" : "SessionToken",
                    "client" : "ClientFingerprints"
                },
                "result" : "boolean",
                "throws" : [
                    "UnknownSession",
                    "PleaseReauth"
                ]
            },
            "closeSession" : {
                "params" : {
                    "start_token" : "SessionToken"
                },
                "result" : "boolean"
            }
        },
        "requires" : [
            "SecureChannel",
            "MessageSignature"
        ]
    }

`}Iface`

## 3.2. User interface for access grants

`Iface{`

    {
        "iface" : "futoin.info.me",
        "version" : "{ver}",
        "ftn3rev" : "1.9",
        "imports" : [
            "futoin.ping:1.0",
            "futoin.auth.types:{ver}"
        ],
        "funcs" : {
            "getEmail" : {
                "result" : "Email",
                "throws" : [
                    "NoValidatedEmail"
                ]
            },
            "getPhone" : {
                "result" : "Phone",
                "throws" : [
                    "NoValidatedPhone"
                ]
            },
            "getNames" : {
                "result" : {
                    "first" : "LatinName",
                    "middle" : "FullLatinName",
                    "last" : "LatinName",
                    "full" : "FullLatinName",
                    "n_first" : "NativeName",
                    "n_middle" : "FullNativeName",
                    "n_last" : "NativeName",
                    "n_full" : "FullNativeName"
                },
                "throws" : [
                    "NoValidatedNames"
                ]
            },
            "getAvatar" : {
                "rawresult" : true
            },
            "getDateOfBirth" : {
                "result" : "Datestamp"
            },
            "getPlaceOfBirth" : {
                "result" : {
                    "place" : "LatinLocation",
                    "n_place" : "NativeLocation"
                }
            },
            "getHomeAddress" : {
                "result" : {
                    "country" : "ISO3166A3",
                    "address" : "LatinLocation",
                    "n_address" : "NativeLocation"
                }
            }
        },
        "requires" : [
            "SecureChannel"
        ]
    }

`}Iface`


=END OF SPEC=
