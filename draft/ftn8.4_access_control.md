<pre>
FTN8.4: FutoIn Security Concept - Access Control
Version: 0.2DV
Date: 2018-01-05
Copyright: 2014-2018 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v0.2 - 2018-01-05 - Andrey Galkin
    - CHANGED: heavily revised & split into sub-specs
* v0.1 - 2014-06-03 - Andrey Galkin
    - Initial draft

# 1. Intro

This sub-specification of [FTN8](./ftn8_security_concept.md) covers
Access Control specification.

Introduction is done in the main spec.

# 2. Concept

There are two goals:

1. Check if particular User is allowed to access API with particular parameters.
2. Allow one Service(A) to access API of another Service(B) on behalf of
User who grants such access through AuthService based on Auth Query of the first Service(A).

Details of Auth Query are defined in [FTN8.3](./ftn8.3\_client\_auth.md) sub-spec.

## 2.1. Access Control Descriptor (ACD)

This is low level concept which is used to grant and check dynamic access in runtime.

Access hierarchy: Service -> Interface -> Version -> Function -> Parameters.
Such combination is called "Access Control Descriptor" in this spec.

ACD can be partially defined to act like a "mask". In most cases, parameters and functions are omitted.

Service builds a full ACD based on actual request to be checked using related AuthService.

Doing an API call for every action may produce a significant overhead. It is important to design
effective caching mechanism with stable invalidation for security reasons.

## 2.2. Access Groups

It's not user-friendly to ask for particular API details. Instead, providing Service
registers named groups of ACDs with detailed description in multiple languages.

User grants access based on such named Access Groups. Associated ACDs may get updated,
but user should not be asked re-confirm access unless Access Group identifier changes.

## 2.3. Access Control check procedure

* ServiceA performs request to ServiceB on behalf of User
* ServiceB authenticates requests through AuthService
* Of on-behalf-of request field is present
    - ServiceB checks against AuthService if ServiceA is allowed to access
        ServiceB on behalf of particular User
    - AuthService performs necessary checks and returns optional constraints
    - ServiceB validated the constraints
    - ServiceB caches ACD, if it is able to invalidate it properly
    - ServiceB continues processing the request like is done by User
* Request is processed as normal

## 2.4. Access control of resources

In many cases, there is a fixed number of object types, like users, posts, files, etc.
And there is a variable size of objects per type, many users, posts and files. Every
object can have actions like Create/Read/Update/Delete.

A hierarchy is seen: Service -> Object Types -> Individual Objects -> Individual Object Action.

However, as all FutoIn operations are done through interfaces, it's possible to map
those to ACDs described above. This specification does not limit such flexibility and
the way such access get granted internally, but it's assumed that access is checked
through `checkAccess()` call.

## 2.5. Events

* `ACD_UPD` - update of ACDs per user
    - `local_id` - local user ID

## 2.6. Example

### 2.6.1. Regular call

       User/ServiceA              ServiceB                      AuthService
           |                          .                              .
           |-------- request -------> |                              .
           .                          |-------- checkAccess() -----> |
           .                          | <-- validation constraints --|
           | <------ response --------|                              .
           |                          .                              .           

### 2.6.2. On-Behalf-oF calls

        ServiceA                  ServiceB                      AuthService
           |                          .                              .
           |-------- request -------> |                              .
           .                          |-------- checkOBF() --------> |
           .                          | <-- validation constraints --|
           .                          |-------- checkAccess() -----> |
           .                          | <-- validation constraints --|
           | <------ response --------|                              .
           |                          .                              .           



# 3. Interface.

## 3.1. Access check interface

`Iface{`

    {
        "iface" : "futoin.auth.access",
        "version" : "{ver}",
        "ftn3rev" : "1.8",
        "imports" : [
            "futoin.ping:1.0",
            "futoin.auth.types:{ver}"
        ],
        "funcs" : {
            "checkOBF" : {
                "params" : {
                    "obf" : "AuthInfo",
                    "iface" : "FTNFace",
                    "ver" : "FTNVersion",
                    "func" : "FTNFunction"
                },
                "result" : {
                    "params" : "ParamConstraint"
                }
            },
            "checkAccess" : {
                "params" : {
                    "user" : "AuthInfo",
                    "iface" : "FTNFace",
                    "ver" : "FTNVersion",
                    "func" : "FTNFunction"
                },
                "result" : {
                    "params" : "ParamConstraint"
                }
            }
        },
        "requires" : [
            "SecureChannel",
            "MessageSignature"
        ]
    }

`}Iface`


=END OF SPEC=

