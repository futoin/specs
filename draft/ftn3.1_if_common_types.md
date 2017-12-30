<pre>
FTN3.1: FutoIn Interface - Common Types
Version: 1.0DV
Date: 2017-12-29
Copyright: 2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.0 - 2017-12-29 - Andrey Galkin
    - Initial spec

# 1. Intro

Many specifications require the same basic types like UUID
or Base64 string. This standalone specification under main
FTN3 provides such complex basic types.

# 2. Concept

Just a standard spec with common types.

# 3. Interfaca

`Iface{`

    {
        "iface" : "futoin.types",
        "version" : "{ver}",
        "ftn3rev" : "1.8",
        "types" : {
            "Base64" : {
                "type" : "string",
                "regex" : "^[a-zA-Z0-9+/]*$",
                "desc" : "Use min/maxlen to control length"
            },
            "UUIDB64" : {
                "type" : "Base64",
                "minlen" : 22,
                "maxlen" : 22,
                "desc" : "UUID in Base64 without padding"
            },
            "UUID" : {
                "type" : "string",
                "regex" : "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$",
                "desc" : "Canonical UUID with separators"
            },
            "NotNegativeInteger" : {
                "type" : "integer",
                "min" : 0
            },
            "PositiveInteger" : {
                "type" : "integer",
                "min" : 1
            },
            "Domain" : {
                "type" : "string",
                "regex" : "^[a-z0-9-]+(\\.[a-z0-9-]+)*\\.[a-z]{2,}$"
            },
            "Email" : {
                "type" : "string",
                "regex" : "^[a-zA-Z0-9._%+-]+@[a-z0-9-]+(\\.[a-z0-9-]+)*\\.[a-z]{2,}$",
                "maxlen" : 254
            },
            "FTNRequest" : {
                "type" : "map",
                "fields" : {
                    "f" : "string",
                    "p" : "map",
                    "rid" : {
                        "type" : "string",
                        "optional" : true
                    },
                    "sec" : {
                        "type" : "any",
                        "optional" : true
                    },
                    "obf" : {
                        "type" : "any",
                        "optional" : true
                    },
                    "forcersp" : {
                        "type" : "boolean",
                        "optional" : true
                    }
                }
            },
            "FTNResponse" : {
                "type" : "map",
                "fields" : {
                    "r" : "any",
                    "rid" : {
                        "type" : "string",
                        "optional" : true
                    },
                    "sec" : {
                        "type" : "any",
                        "optional" : true
                    },
                    "e" : {
                        "type" : "string",
                        "optional" : true
                    },
                    "edesc" : {
                        "type" : "string",
                        "optional" : true
                    }
                }
            }
        }
    }

`}Iface`

=END OF SPEC=
