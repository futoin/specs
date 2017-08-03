<pre>
FTN2: FutoIn Specification Versioning
Version: 1.1
Date: 2017-08-03
Copyright: 2014-2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.1 - 2017-08-03 - Andrey Galkin
    - NEW: "6. Specification content requirements" section
    - NEW: "2.3.3. Non-concept fixes in released versions" section
* v1.0 - 2014-09-07 - Andrey Galkin
    - Initial spec

# 1. Version format

There are two version components MAJOR and MINOR, separated by point.

For released specifications, both components are not negative integer number, monotonically increasing from zero.

    Example: 1.0, 1.1, 2.0


The latest up-to-date version in development/draft is to be marked with special "DV" component in place of MINOR, concatenated with draft number equal to the next
expected version.

    Example: 0.DV1, 1.DV1, 2.DV1, 2.DV2



# 2. Linear Versioning

FutoIn specification versioning is linear - no branching is allowed.

"(n+1).x" version is guaranteed to be newer than any "n.y", where x, y - any value

As exception, it is allowed to released new versions of previous MAJOR version until the first release of new MAJOR version

## 2.1. Initial Specification Design

MAJOR is set to 0, minor is incremented with every draft

## 2.2. Initial Release

MAJOR is set to 1, MINOR - to 0.

## 2.3. Specification revise

### 2.3.1. Backward compatible draft
Existing specification is updated and versioned as draft (MAJOR.DVn).
New version is released as "MAJOR.(MINOR+1)".

### 2.3.2. Draft with broken backward compatibility
Broken backward compatibility is versioned as "(MAJOR+1).DVn" and then releases as "(MAJOR+1).0".

The previous version should be available with "_vMAJOR" postfix/suffix in filename for easy accessibility purposes.

### 2.3.3. Non-concept fixes in released versions
Sometimes, issues are found right after release of new spec.

When changes only fix spelling, typos and similar errors, it's allowed
to apply them without spec version update. However, changelog must
have a dedicated entry with third "patch" component of version.


# 3. Requirements for specification release

1. Specification must be approved (see note below)
2. At least one reference implementation must exist, if applicable
3. At least one full [automatic] test suite must exist, if applicable

*Note: Review & Approval process is out of scope of this document.*

# 4. Backward compatibility

"x.(n+1)" is guaranteed to be backward compatible with any "x.n". Specification bug fix is not subject for backward compatibility.

    Example: 1.1 with 1.0, 1.2 with 1.1 and 1.0, etc.


"(n+1).0" version increment is allowed only, if there is backward incompatible change.
Typically, such releases are allowed only after deep revise process to drop deprecated features.
Exception is when MAJOR=0 - initial development.



# 5. Specification deprecation

Whole specification can be marked deprecated, if its features are fully covered by another specification.
The goal is to avoid alternative specs for the same area.

# 6. Specification content requirements

* "CHANGES" section with listing:
    - first level in format "v{version} - {date} - {author}"
    - second level - list of changes (in this order):
        - "Initial spec" - for v1.0
        - "BREAKING: {desc}" - backward incompatible change
        - "FIXED: {desc}" - fixes of issues found
        - "CHANGED: {desc}" - backward compatible change
        - "NEW: {desc}" - new features
* "1. Intro" - brief introduction on purpose
* "2. Concept" - main ideas behind
* "3. Interface" - related interface definitions, if applicable
* others as required

*Note: historical and specific cases may have another headings*



=END OF SPEC=
