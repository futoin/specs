<pre>
FTN19.2: FutoIn Interface - Transaction Engine - Limits
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

# 2. Concept (Limits)

Limits are important to minimize consequences of potential design & software issues,
to comply with AML/CTF requirements and to protect against risks of unreliable
personnel and partners.

Any action in system must have reasonable limits. Some limits may be used to trigger
additional checks and/or blocking risk analysis.

Periods are accounted per calendar with operator configured timezone. Per account
holder limits are accounted in base currency.

*Note: risk assessment must be done for all activity even if limits are not hit, but that should be done asynchronously.*

## 2.1. Limit groups

It's not feasible to configure most limits individually as it may eventually lead to configuration errors. It would
also make limits practically unmanageable. Therefore, only a small number of limit groups (sets) should be present.

Each account holder must be associated with one of the global limit groups.

## 2.2. Limit domains

Transaction engine assumes different domains of operations. Each domain
has quite specific limit requirements.

General naming convention:

* `_amt` postfix means amount limit
* `_cnt` postfix means count limit
* `_daily_`, `_weekly_`, `_monthly_` suffixes mean daily/weekly/monthly periods
* prefixes define domain/scope of the limit

Continuous accounting must be present based on the following criteria per account holder.

1. `Retail` - purchase of goods and services
    - Limit types:
        - `retail_daily_amt`
        - `retail_daily_cnt`
        - `retail_weekly_amt`
        - `retail_weekly_cnt`
        - `retail_monthly_amt`
        - `retail_monthly_cnt`
    - Accounting for affected transactions:
        - On blocking of balance - increase Used for blocked part
        - On unblocking of balance - decrease Used for unblocked part
        - On decreasing balance - increase Used
        - On increasing balance - no action
2. `Deposits` - in/out transfers of own money
    - Limit types:
        - Deposits:
            - `deposit_daily_amt`
            - `deposit_daily_cnt`
            - `deposit_weekly_amt`
            - `deposit_weekly_cnt`
            - `deposit_monthly_amt`
            - `deposit_monthly_cnt`
        - Withdrawals:
            - `withdrawal_daily_amt`
            - `withdrawal_daily_cnt`
            - `withdrawal_weekly_amt`
            - `withdrawal_weekly_cnt`
            - `withdrawal_monthly_amt`
            - `withdrawal_monthly_cnt`
    - Accounting for affected transactions: Deposits & Withdrawals
        - canceled transactions should decrease statistics
3. `Payments` - transfers to other users
    - Limit types:
        - Outbound:
            - `outbound_daily_amt`
            - `outbound_daily_cnt`
            - `outbound_weekly_amt`
            - `outbound_weekly_cnt`
            - `outbound_monthly_amt`
            - `outbound_monthly_cnt`
        - Inbound:
            - `inbound_daily_amt`
            - `inbound_daily_cnt`
            - `inbound_weekly_amt`
            - `inbound_weekly_cnt`
            - `inbound_monthly_amt`
            - `inbound_monthly_cnt`
    - Accounting for affected transactions: Deposits & Withdrawals
        - canceled transactions should decrease statistics
4. `Gaming` - in-game activity
    - Limit types:
        - Bets:
            - `bet_daily_amt`
            - `bet_daily_cnt`
            - `bet_weekly_amt`
            - `bet_weekly_cnt`
            - `bet_monthly_amt`
            - `bet_monthly_cnt`
        - Wins:
            - `win_daily_amt`
            - `win_daily_cnt`
            - `win_weekly_amt`
            - `win_weekly_cnt`
            - `win_monthly_amt`
            - `win_monthly_cnt`
        - Profitability:
            - `profit_daily_amt`
            - `profit_weekly_amt`
            - `profit_monthly_amt`
    - Accounting for affected transactions: Deposits & Withdrawals
        - canceled transactions should decrease statistics
5. `Misc` - not fitting other domains
    - Limit types:
        - Messages:
            - `message_daily_cnt`
            - `message_weekly_cnt`
            - `message_monthly_cnt`
        - Failure:
            - `failure_daily_cnt`
            - `failure_weekly_cnt`
            - `failure_monthly_cnt`
        - Limit hits:
            - `limithit_daily_cnt`
            - `limithit_weekly_cnt`
            - `limithit_monthly_cnt`
6. `Personnel` - limits of operations done by specific employee
    - Limit types:
        - Messages:
            - `message_daily_cnt`
            - `message_weekly_cnt`
            - `message_monthly_cnt`
        - Manual transactions:
            - `manual_daily_amt`
            - `manual_daily_cnt`
            - `manual_weekly_amt`
            - `manual_weekly_cnt`
            - `manual_monthly_amt`
            - `manual_monthly_cnt`

## 2.3. Limit types:

### 2.3.1. Per account limits

Such limit is set per single account in currency of the account.

1. Overdraft - negative balance limit set by system

### 2.3.2. Account holder limits

These are personal user limits which user configures based on own will. Such limits are bound
by system limits and act as threshold value.

1. Extended verification - requires system to get implementation-defined additional confirmation
    of user activity. For example, input of Two-Factor Authentication code.
    * `retail_daily_amt`
2. Soft limits - user configured restrictions
    * `retail_daily_amt`
    * `withdrawal_daily_amt`
    * `bet_daily_amt`
    * `outbound_daily_amt`

### 2.3.3. Group system limits

1. Hard limits
    * All fields of the same name as statitics field act as maximum limit
    * `Retail`
        - `retail_min_amt` - minimal transaction amount
    * `Deposits`
        - `deposit_min_amt` - minimal deposit amount
        - `withdrawal_min_amt` - minimal withdrawal amount
    * `Payments` 
        - `outbound_min_amt` - minimal outbound payment amount
    * `Gaming`
        - `bet_min_amt` - minimal bet amount
2. Synchronous risk assessment
    * All fields of the same name as statitics field act as threshold value
    * `Retail`
    * `Deposits`
    * `Payments`
3. Extended confirmation
    * All fields of the same name as statitics field act as threshold value
    * `Retail` - only for purchases
    * `Deposits` - only for withdrwals
    * `Payments` - only for outbound payments

## 2.4. Events

* `LIM_NEW` - on new limits group
* `LIM_SET` - update of account holder limits

# 3. Interface (Limits)

Internal API for limits configuration & processing.

`Iface{`

        {
            "iface" : "futoin.xfer.limits",
            "version" : "{ver}",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:{ver}"
            ],
            "types" : {
                "OptionalLimitValues" : [ "LimitValues", "boolean" ],
                "LimitGroups" : {
                    "type" : "array",
                    "elemtype" : "LimitGroup"
                },
                "RetailLimitValues" : {
                    "type" : "LimitValues",
                    "fields" : {
                        "retail_daily_amt" : "LimitAmount",
                        "retail_daily_cnt" : "LimitCount",
                        "retail_weekly_amt" : "LimitAmount",
                        "retail_weekly_cnt" : "LimitCount",
                        "retail_monthly_amt" : "LimitAmount",
                        "retail_monthly_cnt" : "LimitCount",
                        "retail_min_amt" : "LimitAmount",
                        "preauth_daily_amt" : "LimitAmount",
                        "preauth_daily_cnt" : "LimitCount",
                        "preauth_weekly_amt" : "LimitAmount",
                        "preauth_weekly_cnt" : "LimitCount",
                        "preauth_monthly_amt" : "LimitAmount",
                        "preauth_monthly_cnt" : "LimitCount",
                        "preauth_min_amt" : "LimitAmount"
                    }
                },
                "DepositsLimitValues" : {
                    "type" : "LimitValues",
                    "fields" : {
                        "deposit_daily_amt" : "LimitAmount",
                        "deposit_daily_cnt" : "LimitCount",
                        "withdrawal_daily_amt" : "LimitAmount",
                        "withdrawal_daily_cnt" : "LimitCount",
                        "deposit_weekly_amt" : "LimitAmount",
                        "deposit_weekly_cnt" : "LimitCount",
                        "withdrawal_weekly_amt" : "LimitAmount",
                        "withdrawal_weekly_cnt" : "LimitCount",
                        "deposit_monthly_amt" : "LimitAmount",
                        "deposit_monthly_cnt" : "LimitCount",
                        "withdrawal_monthly_amt" : "LimitAmount",
                        "withdrawal_monthly_cnt" : "LimitCount",
                        "deposit_min_amt" : "LimitAmount",
                        "withdrawal_min_amt" : "LimitAmount"
                    }
                },
                "PaymentsLimitValues" : {
                    "type" : "LimitValues",
                    "fields" : {
                        "outbound_daily_amt" : "LimitAmount",
                        "outbound_daily_cnt" : "LimitCount",
                        "inbound_daily_amt" : "LimitAmount",
                        "inbound_daily_cnt" : "LimitCount",
                        "outbound_weekly_amt" : "LimitAmount",
                        "outbound_weekly_cnt" : "LimitCount",
                        "inbound_weekly_amt" : "LimitAmount",
                        "inbound_weekly_cnt" : "LimitCount",
                        "outbound_monthly_amt" : "LimitAmount",
                        "outbound_monthly_cnt" : "LimitCount",
                        "inbound_monthly_amt" : "LimitAmount",
                        "inbound_monthly_cnt" : "LimitCount",
                        "outbound_min_amt" : "LimitAmount"
                    }
                },
                "GamingLimitValues" : {
                    "type" : "LimitValues",
                    "fields" : {
                        "bet_daily_amt" : "LimitAmount",
                        "bet_daily_cnt" : "LimitCount",
                        "win_daily_amt" : "LimitAmount",
                        "win_daily_cnt" : "LimitCount",
                        "profit_daily_amt" : "LimitAmount",
                        "bet_weekly_amt" : "LimitAmount",
                        "bet_weekly_cnt" : "LimitCount",
                        "win_weekly_amt" : "LimitAmount",
                        "win_weekly_cnt" : "LimitCount",
                        "profit_weekly_amt" : "LimitAmount",
                        "bet_monthly_amt" : "LimitAmount",
                        "bet_monthly_cnt" : "LimitCount",
                        "win_monthly_amt" : "LimitAmount",
                        "win_monthly_cnt" : "LimitCount",
                        "profit_monthly_amt" : "LimitAmount",
                        "bet_min_amt" : "LimitAmount"
                    }
                },
                "MiscLimitValues" : {
                    "type" : "LimitValues",
                    "fields" : {
                        "message_daily_cnt" : "LimitCount",
                        "failure_daily_cnt" : "LimitCount",
                        "limithit_daily_cnt" : "LimitCount",
                        "message_weekly_cnt" : "LimitCount",
                        "failure_weekly_cnt" : "LimitCount",
                        "limithit_weekly_cnt" : "LimitCount",
                        "message_monthly_cnt" : "LimitCount",
                        "failure_monthly_cnt" : "LimitCount",
                        "limithit_monthly_cnt" : "LimitCount"
                    }
                },
                "PersonnelLimitValues" : {
                    "type" : "LimitValues",
                    "fields" : {
                        "message_daily_cnt" : "LimitCount",
                        "manual_daily_amt" : "LimitAmount",
                        "manual_daily_cnt" : "LimitCount",
                        "message_weekly_cnt" : "LimitCount",
                        "manual_weekly_amt" : "LimitAmount",
                        "manual_weekly_cnt" : "LimitCount",
                        "message_monthly_cnt" : "LimitCount",
                        "manual_monthly_amt" : "LimitAmount",
                        "manual_monthly_cnt" : "LimitCount"
                    }
                }
            },
            "funcs" : {
                "setLimits" : {
                    "params" : {
                        "group" : "LimitGroup",
                        "domain" : "LimitDomain",
                        "currency" : "CurrencyCode",
                        "hard" : "LimitValues",
                        "check" : "OptionalLimitValues",
                        "risk" : "OptionalLimitValues"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownGroup",
                        "UnknownCurrency"
                    ]
                },
                "getLimits" : {
                    "params" : {
                        "group" : "LimitGroup",
                        "domain" : "LimitDomain"
                    },
                    "result" : {
                        "currency" : "CurrencyCode",
                        "hard" : "LimitValues",
                        "check" : "OptionalLimitValues",
                        "risk" : "OptionalLimitValues"
                    },
                    "throws" : [
                        "UnknownGroup",
                        "UnknownCurrency",
                        "LimitsNotSet"
                    ]
                },
                "addLimitGroup" : {
                    "params" : {
                        "group" : "LimitGroup"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "AlreadyExists"
                    ]
                },
                "getLimitGroups" : {
                    "result" : "LimitGroups"
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`


=END OF SPEC=
