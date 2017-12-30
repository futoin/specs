<pre>
FTN8.3: FutoIn Security Concept - Client Authentication
Version: 0.2DV
Date: 2017-12-27
Copyright: 2014-2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

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
* Should be stored and surive Client shutdown, if "remember me" logic is activated,
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

### 2.2.6. Auth Queries from Client by Service through AuthService

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
    by other peer redirects either intentional, due to software bug or due to
    attacks from Client itself.
    - All redirects must be signed by derived key with "EXPOSED" purpose
    - Do not make direct requests to another peer for obviously faked redirects.
3. AuthService must ask user for actions initiated by Service:
    - Only if query really comes from Service based on redirect signature.
    - Any Auth Query must be based on a common template created in advance
        by Service in AuthService.
    - Each Auth Query must have unique not reusable ID (UUID is acceptable).
    - Client redirection must only execute a known template associated with
        requesting Service.
    - Upon Client return to Service, Service must check result in AuthService.
    - Service must keep track of initiated Auth Queries to avoid obviously
        fake checks to AuthService.
    - Service must be ready for User to only partially reject Auth Query.

# 3. Interface


=END OF SPEC=
