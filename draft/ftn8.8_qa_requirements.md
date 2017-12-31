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

## 3.4. Access Control

## 3.5. Authentication rejection limits

=END OF SPEC=
