<pre>
FTN3.1: FutoIn Interface - Common Types
Version: 1.0DV
Date: 2017-12-29
Copyright: 2017-2018 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.0 - 2018-01-02 - Andrey Galkin
    - NEW: Locales & translations
* DV - 2017-12-29 - Andrey Galkin
    - Initial spec

# 1. Intro

Many specifications require the same basic types like UUID
or Base64 string. This standalone specification under main
FTN3 provides such complex basic types.

# 2. Concept

Most of the defined types are self-explanatory. Clarifications
for some of them are done as sub-sections of the Concept.

## 2.1. Locale handling & translations

If `FTNLocal` is passed as parameter then the following logic is used:

1. If locale contains region part:
    - Try full match first (e.g. "en_US")
2. If language code is longer than 2 symbols
    - Try match based on full language name (e.g. "eng")
3. Otherwise, try match based on first two symbols (e.g. "en")

The logic above should provide easy way of specific basic translations with
possibility to fine tune that for various regional dialects.

Definition of native language translations should keep in mind the algorithm
above. Two possible approaches are suggested:

1. item - sub-tree
    * locale = translation pairs
2. locale - sub-tree
    * item_name = translation pairs

The first one is suggested for translations provided in scope of API calls
bound to specific parameters like "name" or "description".

## 2.1. Local handling convention

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
            "Timestamp" : {
                "type" : "string",
                "regex": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"
            },
            "MicroTimestamp" : {
                "type" : "string",
                "regex": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z[0-9]{0,6}$"
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
            "Phone" : {
                "type" : "string",
                "regex" : "^\\+[1-9][0-9]{1,14}$",
                "desc" : "Based on ITU-T E.164 with forced leading '+' for clarity"
            },
            "LatinName" : {
                "type" : "string",
                "regex" : "^[a-zA-Z0-9-]{1,50}$"
            },
            "NativeName" : {
                "type" : "string",
                "regex" : "^\\w{1,50}$"
            },
            "FullLatinName" : {
                "type" : "string",
                "regex" : "^[a-zA-Z0-9 -]{1,100}$"
            },
            "FullNativeName" : {
                "type" : "string",
                "regex" : "^\\w{1,100}$"
            },
            "FTNFace" : {
                "type" : "string",
                "regex" : "^([a-z][a-z0-9]*)(\\.[a-z][a-z0-9]*)*$"
            },
            "FTNVersion" : {
                "type" : "string",
                "regex" : "^[0-9]+\\.[0-9]+$"
            },
            "FTNFunction" : {
                "type" : "string",
                "regex" : "^[a-z][a-zA-Z0-9]*$"
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
            },
            "IPAddress4" : {
                "type" : "string",
                "regex" : "^[0-9]{1,3}(\\.[0-9]{1,3}){3}$",
                "desc" : "Just basic check to look like IPv4 address"
            },
            "IPAddress6" : {
                "type" : "string",
                "regex" : "^[0-9a-fA-F:]*:[0-9a-fA-F]*:[0-9a-fA-F:.]*$",
                "desc" : "Just basic check to look like IPv6 address (including IPv4 coded in IPv6)"
            },
            "IPAddress" : {
                "type" : "string",
                "regex" : "^([0-9]{1,3}(\\.[0-9]{1,3}){3}|[0-9a-fA-F]*:[0-9a-fA-F]*:[0-9a-fA-F.]*)$",
                "desc" : "Just basic check to look like IPv4 or IPv6 address"
            },
            "GenericIdentifier" : {
                "type" : "string",
                "regex" : "^[a-zA-Z]([a-zA-Z0-9_-]*[a-zA-Z0-9])?$",
                "desc" : "Use maxlen to limit"
            },
            "ISO639A2" : {
                "type" : "string",
                "regex" : "^[a-z]{2}$",
                "desc" : "Language: ISO 639 Alpha 2 Code"
            },
            "ISO639A3T" : {
                "type" : "string",
                "regex" : "^[a-z]{3}$",
                "desc" : "Language: ISO 639 Alpha 3 Code T(erminology)"
            },
            "FTNLocale" : {
                "type" : "string",
                "regex" : "^[a-z]{2,3}(_[A-Z]{2})?$",
                "desc" : "FutoIn Locale"
            },
            "ItemTranslations" : {
                "type" : "map",
                "elemtype" : "string",
                "desc" : "FTNLocale key to native translation"
            },
            "LocaleTranslations" : {
                "type" : "map",
                "elemtype" : "string",
                "desc" : "Item names to single local translations"
            },
            "AllTranslations" : {
                "type" : "map",
                "elemtype" : "LocaleTranslations",
                "desc" : "FTNLocale key to map of item translations"
            }
        }
    }

`}Iface`

=END OF SPEC=