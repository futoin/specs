<pre>
FTN8.3: FutoIn Security Concept - Client Authentication
Version: 0.2DV
Date: 2017-12-27
Copyright: 2014-2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v0.2 - 2017-12-27 - Andrey Galkin
    - CHANGED: heavily revised & split into sub-specs
* v0.1 - 2014-06-03 - Andrey Galkin
    - Initial draft

# WARNING

**INCOMPLETE: just peaces from old FTN8 v0.1**

To be revised

# 1. Intro

This sub-specification of [FTN8](./ftn8_security_concept.md) covers
Client authentication.

Client is assumed to be a living being like human - limited number of requests
through software running under Client's control.

The ultimate goal is to concentrate primary Client authentication logic
in AuthService as defined in the main spec while Client-to-Service authentication
is derived and perhaps more difficult to break.

# 2. Concept

## 2.1. Client registration

There is an _open_ list of possible use cases:

1. By adminstrator of AuthService.
1. Via self-registration form.
1. By Service which creates users on demand.

## 2.2. Client Authentication

### 2.2.1. Authentication of requests

1. Each non-anonymous request must be undoubtedly associated with user account
    - especially important when single Client session has multiple user accounts
1. Service passes request to AuthService for authentication
1. AuthService does authentication implementation-defined way
    - user must be active
    - user session must still be valid
1. AuthService returns user local and global IDs for further processing
    - otherwise, `PleaseReauth` standard error is thrown

### 2.2.2. `PleaseReauth` handling in Client code

1. Client must be immediately redirected to associated AuthService login page.
1. Upon successful authentication and return, implementation may restore state and
    continue execution as if no interruption occured.

*Note: this logic does not apply to Service-to-Service calls*

### 2.2.3. Login page logic

1. Client passes implementation-defined authentication procedure on AuthService page.
1. HTTP session cookie or its equivalent is set on Client's device.

### 2.2.4. Multiple user accounts

It's assumed that single Client can use multiple user accounts at the same time. Therefore:

1. Both Service and AuthService must be aware of possible multiple account cases.
1. Login as different user must always be available.
1. If multiple user accounts are authenticated in session then current account selection must be available.

### 2.2.5. Sessions of foreign users

1. Foreign user's home service must be aware of all related session and be able to invalidate them
1. Local AuthService must listen to foreign user updates from user's home AuthService

### 2.2.6. Secure redirection between Service and AuthService

The important aspects:

1. AuthService may want to protect from potential DoS attacks caused by Service redirects
1. AuthService may want to ask user only for action on behalf of Service only if

# 3. Interface


=END OF SPEC=
