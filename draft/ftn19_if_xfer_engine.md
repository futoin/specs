<pre>
FTN19: FutoIn Interface - Transaction Engine
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

Absolutely any project involving any type of money or credit processing
requires financial engine to manage user accounts, process transactions
and support in-depth history and analytics.

Very common, "hand made" transaction processing approaches quickly run into
serious bugs, have scalability and sustainability issues.

Therefore, a standard interface for account management and transaction processing
is required. Based on project scale, it can have different background implementation
being loosely coupled to other business logic.

Possible use cases:

* Online banking system
* In-game economics simulation
* Accounting & billing
* Stock & trading
* Any other case of credits management & reporting

It is assumed there is always single authoritative operator of transaction engine
instance. For multi-tenancy, there must be a separate instance. When multiple
timezones, legislations, regions and other type of segregation are involved,
several instance of transaction engines may be present in scope of single operator
similar to bank branches.

# 2. Concept

There are two fundamental types of objects: accounts and transactions
between the accounts.

The nature of many long-running projects is to have many accounts actively used
only in relatively short period of time. Some accounts may be used only for single
transaction.

Another important object type is account holder. Transaction processing constraints
may apply based on account type and/or account holder type.

Most international project operate with different type of currency, so two more
important object types are currencies and exchange rates.

In most cases, financial system is not closed loop and it requires interaction with
external systems. So, each database object should support external references
with clear distinction of ID source.

## 2.1. Sub-specifications

* [FTN19.1 Transaction Engine - Currencies](./ftn19.1\_if\_currencies.md).
* [FTN19.2 Transaction Engine - Limits](./ftn19.2\_if\_xfer\_limits.md).
* [FTN19.3 Transaction Engine - Accounts](./ftn19.3\_if\_xfer\_accounts.md).
* [FTN19.4 Transaction Engine - Transactions](./ftn19.4\_if\_xfers.md).
* [FTN19.5 Transaction Engine - Messages](./ftn19.5\_if\_xfer_msg.md).

## 2.2. Security considerations

User authentication & authorization is out of scope of this spec. It should be defined
in scope of [FTN8: Security](./ftn8\_security\_concept.md).

Some withdrawal, purchase and peer-to-peer transactions may require extra account holder
confirmation based on Soft limit. The way to verify user confirmation should be also
derived from FTN8.

In other cases, when additional confirmation does not make any sense (e.g. in-game bets)
Soft limit should cause transaction rejection.

# 3. Interface (Common types)

Common types to use in other interfaces of this spec.

`Iface{`

        {
            "iface" : "futoin.xfer.types",
            "version" : "{ver}",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.types:1.0",
                "futoin.currency.types:{ver}"
            ],
            "types" : {
                "AccountID" : "UUIDB64",
                "AccountHolderID" : "UUIDB64",
                "AccountExternalID" : {
                    "type" : "string",
                    "minlen" : 1,
                    "maxlen" : 64
                },
                "AccountHolderExternalID" : {
                    "type" : "string",
                    "minlen" : 1,
                    "maxlen" : 128
                },
                "AccountAlias" : {
                    "type" : "string",
                    "minlen" : 1,
                    "maxlen" : 20
                },
                "Amount" : {
                    "type" : "string",
                    "regex" : "^[0-9]{1,12}(\\.[0-9]{1,8})?$"
                },
                "Balance" : {
                    "type" : "string",
                    "regex" : "^-?[0-9]{1,12}(\\.[0-9]{1,8})?$"
                },
                "XferID" : "UUIDB64",
                "XferExtID" : {
                    "type" : "string",
                    "minlen" : 1,
                    "maxlen" : 32
                },
                "XferExtInfo" : "map",
                "Reason" : {
                    "type" : "string",
                    "maxlen" : 128
                },
                "LimitGroup" : {
                    "type" : "string",
                    "regex" : "^[a-zA-Z0-9_-]{1,32}$"
                },
                "LimitDomain" : {
                    "type" : "enum",
                    "items" : [
                        "Retail",
                        "Deposits",
                        "Payments",
                        "Gaming",
                        "Misc",
                        "Personnel"
                    ]
                },
                "LimitAmount" : "Amount",
                "LimitCount" : {
                    "type" : "integer",
                    "min" : 0
                },
                "LimitValue" : [ "LimitAmount", "LimitCount" ],
                "LimitValues" : {
                    "type" : "map",
                    "elemtype" : "LimitValue"
                },
                "Fee" : {
                    "type" : "map",
                    "fields" : {
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "reason" : "Reason"
                    }
                },
                "XferTimestamp" : {
                    "type" : "string",
                    "regex": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"
                },
                "XferType" : {
                    "type" : "enum",
                    "items" : [
                        "Deposit",
                        "Withdrawal",
                        "Purchase",
                        "Refund",
                        "PreAuth",
                        "Bet",
                        "Win",
                        "Bonus",
                        "ReleaseBonus",
                        "CancelBonus",
                        "Fee",
                        "Settle",
                        "Generic"
                    ]
                }
            }
        }

`}Iface`


=END OF SPEC=
