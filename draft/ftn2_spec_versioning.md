<pre>
FTN2: FutoIn Specification Versioning
Version: 0.DV
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>


# Version format

There are two version components MAJOR and MINOR, separated by point.

For released specifications, both components are not negative integer number, monotonically increasing from zero.
<pre>
Example: 1.0, 1.1, 2.0
</pre>

The latest up-to-date version in development/draft is to be marked with special "DV" component in place of MINOR, concatenated with draft number
<pre>
Example: 0.DV1, 1.DV1, 2.DV1, 2.DV2
</pre>


# Linear Versioning

FutoIn specification versioning is linear - no branching is allowed.

"(n+1).x" version is guaranteed to be newer than any "n.y", where x, y - any value

As exception, it is allowed to released new versions of previous MAJOR version until the first release of new MAJOR version

## Initial Specification Design

MAJOR is set to 0, minor is incremented with every draft

## Initial Release

MAJOR is set to 1, MINOR - to 0.

## Specification revise

### Backward compatible draft
Existing specification is updated and versioned as draft (MAJOR.DVn).
New version is released as released as "MAJOR.(MINOR+1)".

### Draft with broken backward compatibility
Broken backward compatibility is released as "(MAJOR+1).0"


# Requirements for specification release

1. Specification must be approved (see note below)
2. At least one full [automatic] test suite must exist
3. At least one reference implementation must exist

Note: Review & Approval process is out of scope of this document.

# Backward compatibility

"x.(n+1)" is guaranteed to be backward compatible with any "x.n". Specification bug fix is not subject for backward compatibility.
<pre>
Example: 1.1 with 1.0, 1.2 with 1.1 and 1.0, etc.
</pre>

"(n+1).0" version increment is allowed only, if there is backward incompatible change.
Typically, such releases are allowed only after deep revise process to drop deprecated features.


# Specification deprecation

Whole specification can be marked deprecated, if its features are fully covered by another specification.
The goal is to avoid alternative specs for the same area.


