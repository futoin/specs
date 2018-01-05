<pre>
FTN8.8: FutoIn Security Concept - QA requirements
Version: 0.2DV
Date: 2017-12-31
Copyright: 2014-2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v0.2 - 2017-12-31 - Andrey Galkin
    - CHANGED: heavily revised & split into sub-specs
    - NEW: QA requirements
* v0.1 - 2014-06-03 - Andrey Galkin
    - Initial draft

# 1. Intro

This sub-specification of [FTN8](./ftn8_security_concept.md) covers
Quality Assurance requirements/test cases in scope of FTN8.

As authentication & authorization is one of fundamental aspects of
whole FutoIn project, it is very important to explicitely list all
essential test cases.

# 2. Concept

QA requirements are split into test suites under "Requirements" section.
Each section is organized in paragraph - test case written in style of
User or Job Story and starting from associative identifier.

Format:
```
{SCOPE}-{ID} - {story}
```

Example:

**REQ-1** - The requirement must be short and simple, so it can be easily covered
in single test case.

# 3. Requirements

## 3.1. Stateless clear text authentication

See [FTN8.1](./ftn8.1\_stateless\_auth.md).

*Note: "STLCT" stays for STateLess Clear Text.*

AuthService-related:

**STLCT-A1** - STLCT authentication must be rejected, if it is not enabled in AuthService.

**STLCT-A2** - STLCT authentication must be rejected, if User has no inidividual secret
configured for specific Service.

**STLCT-A3** - STLCT authentication must be rejected, if User is not found.

**STLCT-A4** - STLCT authentication must be rejected, if User secret for
specific Service mismatches.

**STLCT-A5** - all STLCT rejections must have artificial delay to prevent time-based
User existence exposure.

Executor-related:

**STLCT-E1** - Executor must send all available Client fingerprints to AuthService, so
it can enforce additional constraint checks.

**STLCT-E2** - local and global user ID must be set in RequestInfo on accepted
authentication.

**STLCT-E3** - "Info" security level must be set in RequestInfo on accepted
authentication.

## 3.2. Stateless MAC authentication

See [FTN8.1](./ftn8.1\_stateless\_auth.md).

*Note: "STLMC" stays for Stateless Message athentication Code.*

AuthService-related:

**STLMC-A1** - STLMC authentication must be rejected, if it is not enabled in AuthService.

**STLMC-A2** - STLMC authentication must be rejected, if MAC of request message mismatches.

**STLMC-A3** - STLMC authentication must be rejected, if User is not found.

**STLMC-A4** - all STLMC rejections must have artificial delay to prevent time-based
User existence exposure.

Executor-related:

**STLMC-E1** - Executor must send all available Client fingerprints to AuthService, so
it can enforce additional constraint checks.

**STLMC-E2** - local and global user ID must be set in RequestInfo on accepted
authetnication.

**STLMC-E3** - "SafeOps" security level must be set in RequestInfo on accepted
authentication.

## 3.3. Master Secret authentication

See [FTN8.2](./ftn8.2\_master\_auth.md).

*Note: MSMAC states for Master Secret Message Authentication Code.*

Invoker-related:

**MSMAC-I1** - a new secure public/private key pair must get generated before every
new Secret exchange.

**MSMAC-I2** - Invoker must always use peer GlobalServiceID as HKDF0 salt parameter.

**MSMAC-I3** - Invoker must always use HKDF0-MAC strategy for message signing.

**MSMAC-I4** - Invoker must always use HKDF0-EXPOSED strategy for payload signing
in untrusted delivery channel.

**MSMAC-I5** - Invoker must always use a new HKDF-ENC strategy salt parameter for
encryption of any data.

Executor-related:

**MSMAC-E1** - Executor must send all available Client fingerprints to AuthService, so
it can enforce additional constraint checks.

**MSMAC-E2** - Executor must re-retrieve derived key from AuthService on
Client fingerprints change, if local key caching is used.

**MSMAC-E3** - Executor must use the same derived key for signing of response as used
for signing of the related request.

AuthService-related:

**MSMAC-A1** - AuthService must ensure that HKDF0 salt parameter matches GlobalServiceID
of validating Service to protect from easy key leaks.

**MSMAC-A2** - AuthService may cache derived keys only after successfull authentication
of message to protect from DoS using wrong salt cache.

**MSMAC-A3** - shared Secret must use random source of acceptable
quality for cryptographic purposes.

**MSMAC-A4** - AuthService must allow up to two active Secrets per Service per Scope
to allow smooth new Secret rollout without interruptions.

**MSMAC-A5** - AuthService must leave exactly the Secret used for signing the
exchange message as the old active key even when a newer one exists to
protected for errors during response of the exchange processing.

**MSMAC-A6** - "PrivilegedOps" security level must be set in RequestInfo on accepted
authentication.

**MSMAC-A7** - AuthService must expose derived key to Service only after related
authentication of data using the derived key to prevent easy key leaks.

**MSMAC-A8** - AuthService must allow new key exchange only when signing key is
derived from Master Secret with empty of the same `scope` as requested for exchange.


## 3.4. Client authentication

See [FTN8.3](./ftn8.3\_client\_auth.md).

*Note: CLCSA states for CLient Cookie Session Authentication.*

Service-related:

**CLCSA-S1** - Service must undoubtedly associate request with session cookie.

**CLCSA-S2** - Service must forbid cross-domain requests based on HTTP 'Referal'
header whitelist, if applicable.

**CLCSA-S3** - Service should forbid CORS requests with credentials.

**CLCSA-S4** - Service must set session as "HTTP-only" to avoid API exposure.

**CLCSA-S5** - Service must sign & verify set cookies with private secret to
mitigate proxied AuthService DoS with forged sessions.

**CLCSA-S6** - Service must limit cookie time-to-live based on signed timestamp
embedded in cookie value.

**CLCSA-S7** - Executor must send all available Client fingerprints to AuthService, so
it can enforce additional constraint checks during session start/sesson resume.

**CLCSA-S8** - Executor must start a new session after successfull Auth Query.

**CLCSA-S9** - Executor must resume session with AuthService every 10 minutes or
more often while session is actively used.

**CLCSA-S10** - Executor must force session resume with AuthService on every
Client fingerprints change.

**CLCSA-S11** - Executor must check signature of all incoming redirects.

**CLCSA-S12** - Executor must create "EXPOSED" signature of all outcoming redirects.


Client-related:

**CLCSA-C1** - Client should support HTTP-only cookies.

**CLCSA-C2** - Client should obey CORS.

AuthService-related:

**CLCSA-A1** - AuthService must check signature of all incoming redirects.

**CLCSA-A2** - AuthService must create "EXPOSED" signature of all outcoming redirects.

**CLCSA-A3** - AuthService should support multi-factor authentication for Users.

**CLCSA-A4** - AuthService must ensure that Auth Query belongs to requesting Service.

**CLCSA-A5** - AuthService must ensure that session-related tokens are associated
to requesting Service.

**CLCSA-A6** - AuthService must ask User based on Auth Query request, if requested access
has not been granted before.

**CLCSA-A7** - AuthService should skip asking User based on Auth Query request, if
requested access has been granted before.


## 3.5. Access Control

See [FTN8.4](./ftn8.4\_access\_control.md).

## 3.6. Authentication rejection limits

=END OF SPEC=
