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

**STLCT-1** - STLCT authentication must be rejected, if it is not enabled in AuthService.

**STLCT-2** - STLCT authentication must be rejected, if User has no inidividual secret
configured for specific Service.

**STLCT-3** - STLCT authentication must be rejected, if User is not found.

**STLCT-4** - STLCT authentication must be rejected, if User secret for
specific Service mismatches.

**STLCT-5** - all STLCT rejections must have artificial delay to prevent time-based
User existence exposure.

Executor-related:

**STLCT-6** - Service must send all available Client fingerprints to AuthService, so
it can enforce additional constraint checks.

**STLCT-7** - local and global user ID must be set in RequestInfo on accepted
authentication.

**STLCT-8** - "Info" security level must be set in RequestInfo on accepted
authentication.

## 3.2. Stateless MAC authentication

See [FTN8.1](./ftn8.1\_stateless\_auth.md).

*Note: "STLMC" stays for Stateless Message athentication Code.*

AuthService-related:

**STLMC-1** - STLMC authentication must be rejected, if it is not enabled in AuthService.

**STLMC-2** - STLMC authentication must be rejected, if MAC of request message mismatches.

**STLMC-3** - STLMC authentication must be rejected, if User is not found.

**STLMC-4** - all STLMC rejections must have artificial delay to prevent time-based
User existence exposure.

Executor-related:

**STLMC-5** - Service must send all available Client fingerprints to AuthService, so
it can enforce additional constraint checks.

**STLMC-6** - local and global user ID must be set in RequestInfo on accepted
authetnication.

**STLMC-7** - "SafeOps" security level must be set in RequestInfo on accepted
authentication.

## 3.3. Master Secret authentication

See [FTN8.2](./ftn8.2\_master\_auth.md).

*Note: MSMAC states for Master Secret Message Authentication Code.*

Service-related:

**MSMAC-1** - a new secure public/private key pair must get generated before every
new Secret exchange.

**MSMAC-2** - Service must always use peer GlobalServiceID as HKDF0 salt parameter.

**MSMAC-3** - Service must always use HKDF0-MAC strategy for message signing.

**MSMAC-4** - Service must always use HKDF0-EXPOSED strategy for payload signing
in untrusted delivery channel.

**MSMAC-5** - Service must always use a new HKDF-ENC strategy salt parameter for
encryption of any data.

**MSMAC-6** - Service must use the same derived key for signing of response as used
for signing of the related request.

AuthService-related:

**MSMAC-7** - AuthService must ensure that HKDF0 salt parameter matches GlobalServiceID
of validating Service to protect from easy key leaks.

**MSMAC-8** - AuthService may cache derived keys only after successfull authentication
of message to protect from DoS using wrong salt cache.

**MSMAC-9** - shared Secret must use random source of acceptable
quality for cryptographic purposes.

**MSMAC-10** - AuthService must allow up to two active Secrets per Service per Scope
to allow smooth new Secret rollout without interruptions.

**MSMAC-11** - AuthService must leave exactly the Secret used for signing the
exchange message as the old active key even when a newer one exists to
protected for errors during response of the exchange processing.

**MSMAC-12** - "PrivilegedOps" security level must be set in RequestInfo on accepted
authentication.

**MSMAC-13** - AuthService must expose derived key to Service only after related
authentication of data using the derived key to prevent easy key leaks.


## 3.4. Client authentication

See [FTN8.3](./ftn8.3\_client\_auth.md).

## 3.5. Access Control

See [FTN8.4](./ftn8.4\_access\_control.md).

## 3.6. Authentication rejection limits

=END OF SPEC=
