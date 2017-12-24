<pre>
FTN19.3: FutoIn Interface - Transaction Engine - Accounts
Version: 1.0DV
Date: 2017-12-24
Copyright: 2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* DV - 2017-12-24 - Andrey Galkin
    - Split into sub-specs
* DV - 2017-08-27 - Andrey Galkin
    - Initial draft

# 1. Intro

This is sub-specification of main [FTN19: Transaction Engine](./ftn19\_if\_xfer\_engine.md).

# 2. Concept (Accounts)

Each account must have the following properties:

1. `Currency`
2. `Balance`
3. `Reservation`
4. `Overdraft`

## 2.1. Types

The following types of accounts are assumed:

1. `System` - internal source & sink which have no limit restrictions
2. `Regular` - used for accumulation of funds, supports operation limits
3. `Transit` - similar to Regular, but forbids direct operations by account holder
4. `External` - similar to Transit, but used for accounting of external systems
5. `Bonus` - a temporary account used for bonus amounts processing

## 2.2. Events

* `ACCT_NEW` - on account being created
* `ACCT_UPD` - on account information being updated, but not balance
* `ACCT_BAL` - on account balance change
* `ACCT_CONV` - on account currency being converted to another one
* `ACCT_CLOSE` - on account being closed

## 2.3. Account holder

There is strict Know Your Customer (KYC) and related limit requirements for financial
systems in scope of AML/CTF efforts. It's the primary reason to introduce such entity.

As account holder information varies across the Globe, it should be abstract enough
to hold arbitrary data provided by actual implementation.

However, if data type is already defined as part of spec - it must be used instead of
optional extensions.

### 2.3.1. Known data types

All data may be in national Unicode format. However, some fields may have
restrictions.

* `full_name`
* `other_names` = {} - other names, if applicable
    * `first`
    * `last`
    * `middle`
    * `father`
    * `latin_first` - first name in latin as in ICAO ID
    * `latin_last` - last name in latin as in ICAO ID
* `dob` - date of birth
* `sex` = [M, F, O] - Male, Female, Other
* `title` - arbitrary string like 'Mr.', 'Dr.', 'Sir', etc.
* `citizenship` = [] - Country List
* `resident` = [] - Country List
* `home_address` = {} - primary contact address
    * `country`
    * `region` = null - state, province, etc. if applicable
    * `city`
    * `street`
    * `building`
    * `room`
* `other_addresses` = [ {} ] - list of other contact addresses
* `main_email` - primary contact email
* `other_emails` = [] - list of contact emails
* `main_phone` - primary contact phone
* `other_phones` = [] - list of contact phones
* `ids` = [ {}, ... ] - list of IDs
    * `type` - arbitrary string
        * `ICAO` - ICAO-compliant ID/passport
        * `NATID` - national ID
        * `DL` - Driver License
    * `num` - arbitrary string identifying document ID
    * `country` - the country issued the document
    * `issuer`
    * `iss_date` - date issued
    * `exp_date` - valid through date
    * `doc_ids` = [] - list of associated uploaded documents
    * `comment` - user supplied comment
* `tax_id`

### 2.3.2. Known internal data types

* `api` - define peer API configuration
    * `{iface}` - interface name without version as key
        * `flavour=default` - custom implementation
        * `version={latest}` - assume latest known version of interface
        * `endpoint` - endpoint URL
        * `credentials=null` - credentials string
        * `options={}` - any options to pass for registration

### 2.3.3. Events

* `AH_NEW` - new account holder
* `AH_UPD` - update of account holder
* `AH_BLOCK` - on account holder being blocked

# 3. Interface (Accounts)

Account management API for internal use only.

Merge functionality should be rarely used to workaround multiple registrations per single person
which may happen in some scenarios.

It's assumed there is a unique Account Alias per Account Holder - it should be used to create
accounts and prevent duplicates.

External Account ID is optional, but can be set only at creation time.

Transit and Bonus account types must have related External accounts.
Related account can be set only at creation time with exception below.

When bonus account is closed all out-of-band cancels and wins gets redirected to related account.
Therefore, when bonus amount is released. The main Regular account becomes related.


`Iface{`

        {
            "iface" : "futoin.xfer.accounts",
            "version" : "{ver}",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:{ver}"
            ],
            "types" : {
                "AccountType" : {
                    "type" : "enum",
                    "items": [
                        "System",
                        "Regular",
                        "Transit",
                        "External",
                        "Bonus"
                    ]
                },
                "RelatedAccountID" : [
                    "AccountID",
                    "boolean"
                ],
                "AccountHolderData" : {
                    "type" : "map"
                },
                "AccountHolderInternalData" : {
                    "type" : "map"
                },
                "AccountHolderInfo" : {
                    "type" : "map",
                    "fields" : {
                        "id" : "AccountHolderID",
                        "ext_id" : "AccountHolderExternalID",
                        "group" : "LimitGroup",
                        "enabled" : "boolean",
                        "kyc" : "boolean",
                        "data" : "AccountHolderData",
                        "internal" : "AccountHolderInternalData",
                        "created" : "XferTimestamp",
                        "updated" : "XferTimestamp"
                    }
                },
                "AccountInfo" : {
                    "type" : "map",
                    "fields" : {
                        "id" : "AccountID",
                        "holder" : "AccountHolderID",
                        "type" : "AccountType",
                        "currency" : "CurrencyCode",
                        "alias" : "AccountAlias",
                        "enabled" : "boolean",
                        "balance" : "Balance",
                        "reserved" : "Amount",
                        "overdraft" : "Amount",
                        "ext_id" : {
                            "type" : "AccountExternalID",
                            "optional" : true
                        },
                        "rel_id" : {
                            "type" : "RelatedAccountID",
                            "optional" : true
                        },
                        "created" : "XferTimestamp",
                        "updated" : "XferTimestamp"
                    }
                },
                "AccountInfoList" : {
                    "type" : "array",
                    "elemtype" : "AccountInfo"
                }
            },
            "funcs" : {
                "addAccount" : {
                    "params" : {
                        "holder" : "AccountID",
                        "type" : "AccountType",
                        "currency" : "CurrencyCode",
                        "alias" : "AccountAlias",
                        "enabled" : {
                            "type" : "boolean",
                            "default" : true
                        },
                        "ext_id" : {
                            "type" : "AccountExternalID",
                            "default" : null
                        },
                        "rel_id" :  {
                            "type" : "RelatedAccountID",
                            "default" : null
                        }
                    },
                    "result" : "AccountExternalID",
                    "throws" : [
                        "UnknownHolderID",
                        "UnknownCurrency",
                        "Duplicate"
                    ]
                },
                "updateAccount" : {
                    "params" : {
                        "id" : "AccountID",
                        "alias" : {
                            "type" : "AccountAlias",
                            "default" : null
                        },
                        "enabled" : {
                            "type" : "boolean",
                            "default" : null
                        }
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownAccountID",
                        "Duplicate"
                    ]
                },
                "setOverdraft" : {
                    "params" : {
                        "id" : "AccountID",
                        "currency" : "CurrencyCode",
                        "overdraft" : "Amount"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownAccountID",
                        "CurrencyMismatch"
                    ]
                },
                "getAccount": {
                    "params" : {
                        "id" : "AccountID"
                    },
                    "result" : "AccountInfo",
                    "throws" : [
                        "UnknownAccountID"
                    ]
                },
                "getAccountExt": {
                    "params" : {
                        "holder" : "AccountID",
                        "ext_id" : "AccountExternalID"
                    },
                    "result" : "AccountInfo",
                    "throws" : [
                        "UnknownAccountID"
                    ]
                },
                "listAccounts": {
                    "params" : {
                        "holder" : "AccountHolderID"
                    },
                    "result" : "AccountInfoList",
                    "throws" : [
                        "UnknownHolderID"
                    ]
                },
                "convertAccount" : {
                    "params" : {
                        "id" : "AccountID",
                        "currency" : "CurrencyCode"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownHolderID",
                        "UnknownCurrency"
                    ],
                    "desc" : "For rare cases when some currency needs to be disabled"
                },
                "addAccountHolder" : {
                    "params" : {
                        "ext_id" : "AccountHolderExternalID",
                        "group" : "LimitGroup",
                        "enabled" : "boolean",
                        "kyc" : "boolean",
                        "data" : "AccountHolderData",
                        "internal" : "AccountHolderInternalData"
                    },
                    "result" : "AccountHolderID",
                    "throws" : [
                        "UnknownLimitGroup",
                        "DuplicateExtID"
                    ]
                },
                "updateAccountHolder" : {
                    "params" : {
                        "id" : "AccountHolderID",
                        "group" : {
                            "type" : "LimitGroup",
                            "default" : null
                        },
                        "enabled" : {
                            "type" : "boolean",
                            "default" : null
                        },
                        "kyc" : {
                            "type" : "boolean",
                            "default" : null
                        },
                        "data" : {
                            "type" : "AccountHolderData",
                            "default" : null
                        },
                        "internal" : {
                            "type" : "AccountHolderInternalData",
                            "default" : null
                        }
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownHolderID",
                        "UnknownLimitGroup"
                    ]
                },
                "getAccountHolder" : {
                    "params" : {
                        "id" : "AccountHolderID"
                    },
                    "result" : "AccountHolderInfo",
                    "throws" : [
                        "UnknownHolderID"
                    ]
                },
                "getAccountHolderExt" : {
                    "params" : {
                        "ext_id" : "AccountHolderExternalID"
                    },
                    "result" : "AccountHolderInfo",
                    "throws" : [
                        "UnknownHolderID"
                    ]
                },
                "mergeAccountHolders" : {
                    "params" : {
                        "id" : "AccountHolderID",
                        "other_id" : "AccountHolderID"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownHolderID"
                    ]
                },
                "getLimitStats" : {
                    "params" : {
                        "holder" : "AccountHolderID",
                        "domain" : "LimitDomain"
                    },
                    "result" : {
                        "currency" : "CurrencyCode",
                        "stats" : "LimitValues"
                    },
                    "throws" : [
                        "UnknownHolderID"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

=END OF SPEC=
