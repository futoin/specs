<pre>
FTN8.2: FutoIn Security Concept - Service Authentication
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
Service authentication.

Service is assumed to be a standalone software or equal - high number of
unattended requests.

# 2. Concept

## 2.1. Overall goals

1. 

## 2.x. Secure symmetric key exchange

Symmetric key is assumed under "Secret"

1. Service makes initial call:
    - generates a temporary assymetric key
    - requests a new key from AuthService providing:
        - the temporary public key for response encryption
        - current active key ID
        - list of supported Secret types
        - purpose of Secret (HMAC, Documents, AuthPayload, etc.)
1. AuthService processes the request:
    - ensures request is authentic based on HMAC signature
    - generates a new secret
    - cleans up old secrets ensuring active key ID remains
    - sends back the new key encrypted by the temporary public key
1. Service processes response:
    - decrypts the payload using the temporary private key
    - injects the new secret key as primary
1. Service gradually starts using the new Secret
1. Both the new Secret and the previous Secret are active

Goals met:

* Forward secrecy even if any key gets compromised
* Works over unencrypted/untrusted channels
* Ensure rolling Secret updates without communication interruptions
* AuthService controls Secret quality
* Resource-heavy assymetric key generation is responsibility of Service to
    protected AuthService
* Initiating Service (acting as Invoker) is responsible for periodic key exchange
    - It can not do that at all to reduce complexity, if acceptable
    - It avoids overcomplicating design with AuthService-to-Service callbacks

## 2.x. HTTP notes

1. HTTP `Referer` header must be empty

# 3. Interface

=END OF SPEC=
