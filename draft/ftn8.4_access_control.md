<pre>
FTN8.4: FutoIn Security Concept - Access Control
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
Access Control specification.



# 5. Access Control Service

In many cases, there is a fixed number of object types, like users, posts, files, etc.
And there is a variable size of objects per type, many users, posts and files. Every
object can have Create/Read/Update/Delete action.

We can see a hierarchy here: Service -> Object Types -> Individual Objects -> Individual Object Action.

Another type of hierarchy can be: Service -> Interface -> Function.

In all cases it is possible to unify access control system to operate on neutral
tree-like structure of identifiers. On low level, Client access is controlled on specific
end-object+action. The details of how access is granted (e.g. roles, individual permissions, ownership, etc.)
are AccessControlService implementation details. However, access can be granted by parent node and/or
access control tree mask, where some of parent nodes can be "any".

Doing an API call for every action may produce a significant overhead. It is important to design
effective caching mechanism with stable invalidation for security reasons.

## 5.1. Access Control descriptor

There must be a common notation to identify object of checked control. In API, the access notation is
an ordered array, where the first item is the top most in scope.

Descriptor scope is specific to context. In Service context, scope is the Service. In Access Control Service,
the scope is a common set of all Services registered to the system (meaning the first element is Service identifier).

*Example: ["root_node", "object_type", "action"]*

In some cases, wildcard is desired for some items. Example: grant update access to all users.
Wildcard is marked as null value in place of item in the descriptor array.

*Example: ["root_node", null, "action"]*

For human readable purpose, the same descriptor can be written in string form, each item being separated by
dot "." and wildcard null being replaced by star "*".

*Example: "root.object_type.action", "root.*.action"*

## 5.2. Access Control check

* Client performs a request to Service
* Service calls AccessControlService providing client ID and access descriptor
* AccessControlService checks access implementation-dependent way
* If access is not granted, AccessControlService returns "Forbidden" exception
* AccessControlService returns
    * matched access control descriptor (access can be granted by parent item)
    * cache Time-to-Live
    * required auth security level
* Service caches response by descriptor to optimize checks next time
* Service checks if current auth security level satisfy requirements
* Service continues request processing

## 5.3. Example

        Client                     Service                      AccessControlService
           |                          |                              |
           |-------- request -------> |                              |
           |                          |--------- checkAccess ------> |
           |                          | <-- validation constraints --|
           | <------ response --------|                              |
           |                          |                              |           



# 3. Interface.

To be revised.

=END OF SPEC=

