<pre>
FTN19: FutoIn Interface - Transaction Engine
Version: 1.0DV
Date: 2017-09-17
Copyright: 2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* DV - 2017-09-17 - Andrey Galkin
    - Major rework

* DV - 2017-08-27 - Andrey Galkin
    - Initial draft

# 1. Intro

Absolutely any project involving any type of money or credit processing
requires financial engine to manage user accounts, process transactions
and support in-depth history and analytics.

Very common, "hand made" transaction processing approaches quickly run into
serious bugs, have scalability and suistainability issues.

Therefore, a standard interface for account management and transaction processing
is required. Based on project scale, it can have different background implementation
being loosely coupled to other business logic.

Possible use cases:

* Online banking system
* In-game economics simulation
* Accounting & billing
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

## 2.1. Currencies

### 2.1.1 Codes

There are known internationally accepted currencies with standardized codes, but that
does not cover widely known, but "unofficial" currencies. It's possible to have various
other virtual or closed loop currencies. Therefore, there must be a clear distinction
of currency code "sets". In current implementation, currency code is prefixed with the
following:

* "I:" - for ISO 4217 fiat currency codes of International Organization for Standardization
* "C:" - for so-called cryptocurrencies with de-facto code conventions
* "K:" - for currencies of Confederation of Reasonable Legal Freedom
* "L:" - for closed loop internal currencies or other type of credits (e.g. game minutes)

It should be possible to disable unusused or undesired currencies even if it was previously
registed or used for accounts and transactions.

### 2.1.2. Units

Each currency must have a minimal unit in decimal notation. All currency operations must
always have exact number of decimal places after dot in amounts used in interface. However,
internal database representation may use types without decimal places after dot based on
minimal unit per currency.

### 2.1.3. Exchange rates

Currency exchange rates are dynamic. Therefore, transaction engine must manage current
exchange rate and full history of changes, if applicable. However, each transaction must
contain used rate regardless of data available elsewhere.

It's assumed that exchange rates are constantly updated from authoritative source.

Exchange rate must be set with up to four extra decimal places after dot.

### 2.1.4. Base currency

Each currency may have own authoritative source of exchange rates. It may happen that
the same currency pair may have different rates based on authoritative source.

Due to legislation and other means, all conversion operations should specify the base
currency. Only associated authoritative source exchange rate must be used in such operation.

### 2.1.5. Buy/Sell margin & rounding

Due to imposed risks and rounding errors, the transaction engine operator may need to specify
different rates for conversion to and from base currency. The system should hold a spot rate
and a margin rate to be added to/subtracted from the spot rate.

Relative spread calculations to be done externally before spot & margin rate is set.

Rounding must be done in favor of transaction engine operator.

### 2.1.6. Events

* `CURRENCY` - update of existing currency
* `CURRENCY_NEW` - new currency
* `EXRATE` - change of existing exchange rate
* `EXRATE_NEW` - new pair of exchange rate

## 2.2. Accounts

Each account must have the following properties:
1. Currency
2. Balance
3. Reservation

### 2.2.1. Types

The following types of accounts are assumed:
1. System - internal source & sink which have no limit restrictions
2. Regular - used for accumulation of funds, supports operation limits
3. Transit - similar to Regular, but forbids direct operations by account holder
4. External - similar to Transit, but used for accounting of external systems
5. Bonus - a temporary account used for bonus amounts processing

### 2.2.2. Events

* `ACCT_NEW` - on account being created
* `ACCT_UPD` - on account information being updated, but not balance
* `ACCT_BAL` - on account balance change
* `ACCT_CONV` - on account currency being converted to another one
* `ACCT_CLOSE` - on account being closed

## 2.3. Transactions

### 2.3.1. Types

The following list is recommendation. Particular implementation may
omit some or add additional types. However, if type is already listed in the spec
then it must be used.

* Large amounts with extra checks:
    * Deposit - funds deposit from external source
    * Withdraw - funds withdrawal to external source
* Relatively small amounts with real-time transactions:
    * Bet - gaming bet
    * Win - gaming win
    * CancelBet - cancel gaming bet due to canceled game
* Goods and service purchase:
    * Purchase - purchase
    * CancelPurchase - cancel previous purchase
    * Refund - full or partial refund of Purchase
    * PreAuth - block account balance for later Purchase
    * ClearAuth - clear previous PreAuth balance
* Bonus & Loyalty:
    * Bonus - a special type of stimulation/promotion deposit which adds withdrawal block
    * ReleaseBonus - move bonus amount to regular account and free it of any restrictions
    * CancelBonus - close bonus account
* Misc.:
    * Fee - any type of fee which may force negative balance
    * Generic - generic transaction not related to others, e.g. peer-to-peer

### 2.3.2. Fees

As many transaction processing types involve expenses for operator they may be accompanied
by Fee transaction which should be atomically processed with relates transaction.

Fees due to operation initiatied by account holder action should not allow account
balance to become negative. Other type of fees may result in negative account balance,
if the cause is unavoidable.

### 2.3.3. Transaction processing & error recovery

1. Duplicate check must be performed based on pair of `rel_account` and `ext_id`.
    * All provided data must be checked for mismatch.
    * Original result must be returned without any other processing done.
2. If transaction is already canceled then "AlreadyCanceled" error must be raised.
    * This workaround cases when cancel is delivered before original request.
3. Transaction cancellation;
    * It must be possible to cancel only balance decreasing transactions due to external
        processing cancel (e.g. canceled game or not possible to complete withdrawal).
    * It must not be possible to cancel transaction, if there are related transactions done.
4. `orig_ts` and similar fields must always point to original initiation time in external system.
    * Transaction engine may refuse processing of too old requests which get archived

### 2.3.4. Transaction use case

In all cases, if not noted otherwise, Withdrawals, Refunds, Wins, ClearBonus go in opposite direction
of Deposits, Purchases, Bets and Bonus respectively. 

Pre-authorizations must be reserved only on Regular accounts.

#### 2.3.4.1. Online bank

1. Natural persons & companies have Regular accounts
2. Funds deposit in bank branch goes from System(Bank) to Regular(User) account
3. Transfers to another bank go from Regular(User) to External(OtherBank) correspondent account
4. Inter-bank settlement goes as transaction between External(OtherBank) and System(Bank) accounts
5. Purchases from Regular(Person) to Regular(Company) accounts
6. Fees go from Regular(User) to System(Bank) accounts
7. In-bank transfers go from Regular(User) to Regular(User)

#### 2.3.4.2. General integration of third-party service (Payments, Gaming, Retail, etc.)

Third-party service may be integrated through External(Service) accounts:
* Purchases go from Regular(User) to External(Service) accounts
* Deposits go from External(Service) to Regular(User) accounts
* Settlement is done from/to System(Bank) to External(Service)
* External(Service) account should be constrained by negative balance limit

### 2.3.4.3. Closed loop online gaming system

1. Players get single per currency Regular accounts and unlimited number of Bonus accounts
2. Deposits go from System(Service) to Regular(Player)
3. Bets go from Regular(Player) to System(Service)
    * Associated Bonus(Player) accounts are used in first place by time of claim
    * Bets go from Bonus(Player) to System(Service) account
    * It's possible to have more than one transaction per single bet
4. Purchases go from Regular(Player) to System(Service)
5. Bonus goes from System(Service) to Bonus(Player) accounts

### 2.3.4.4. Online gaming service provider

1. Players get Transit account, single per currency
2. No deposits or withdrawals are assumed
3. Bets go from External(Operator) to Transit(Player) to System(Service)
4. Purchases go from External(Operator) to Transit(Player) to System(Service)
5. Bonus amount is not processed separately in transaction, but should be availabe in extended
    info for fine reporting (out of scope)
6. Settlement is done between Externa(Operator) and System(Service) accounts
7. External(Operator) account should be constrained by negative balance limit

### 2.3.4.5. Online gaming operator

1. Players get single per currency Regular accounts and unlimited number of Bonus accounts
2. In-house Deposits go from System(Operator) to Regular(Player)
3. Payments Deposits go from External(Payments) to Regular(Player) accounts
4. Bets go from Regular(Player) to External(Service) accounts
5. Purchases go from Regular(Player) to External(Service) accounts
6. Purchases in Operator go from Regular(Player) to System(Operator) accounts
7. External(Payments) and External(Service) accounts should be constrained by negative balance limit
8. Settlement is done between System(Operator) and External accounts

### 2.3.4.6. Online gaming pass-through aggregator

The difference to Operator case, is that Operator has own system and Regular accounts are managed externally there.

Aggregator acts as a proxy. For Services, it shows as Operator, but for Operator it shows as Service. This allows
chaining multiple Aggregators - typical case in modern online gaming.

Even if aggregator supports Payments as part of business, it should be provided as separate Payments service on
architecture level.

1. For each Player a single per currency Transit account is created
2. No deposits or withdrawals are assumed
3. Bets go from External(Operator) to Transit(Player) to External(Service) accounts
5. Purchases follow Bets scheme, except Bonus processing
6. External(Operator) and External(Service) accounts should be constrained by negative balance limit
7. Settlement is done between System(Aggregator) and External accounts

### 2.3.4.7. Payments provider

1. For each User a Transit account is created, Operators have External account
2. No gaming or sales transactions are assumed
3. Deposits go from System(Payments) to Transit(User) to External(Operator) accounts
4. Settlement is done between System(Payments) and External(Operator) accounts
5. External(Operator) accounts should be constrained by negative balance limit

### 2.3.4.8. Payments aggregator

1. For each User a Transit account is created, Operators and Payment providers have External accounts
2. No gaming or sales transactions are assumed
3. Deposits go from External(Payments) to Transit(User) to External(Operator) accounts
4. Settlement is done between System(Aggregator) and External accounts
5. External accounts should be constrained by negative balance limit


### 2.3.5. Events

* `XFER_RISK` - on transaction waiting for risk analysis
* `XFER_WAIT` - on transaction waiting for external processing
* `XFER_DONE` - on transaction being completed
* `XFER_FEE` - on fee transaction
    * Note: it should follow related XFER_DONE, if applicable
* `XFER_REJ` - on transaction being rejected
* `XFER_BLOCK` - on transaction being blocked due inbound rejection of target account
    * Note: by limit, by external failure or by risk rejection

## 2.4. Limits

Limits are important to minimize consequences of potential design & software issues,
to comply with AML/CTF requirements and to protect against risks of unreliable
personnel and partners.

Any action in system must have reasonable limits. Some limits may be used to trigger
additional checks and/or blocking risk analysis.

Periods are accounted per calendar with operator configured timezone. Per account
holder limits are accounted in base currency.

*Note: risk assessment must be done for all activity even if limits are not hit, but that should be asynchronous.*

### 2.4.1. Limit groups

It's not feasible to configure most limits individually as it may eventually lead to configuration errors. It would
also make limits practically unmanageable. Therefore, only a smal number of limit groups (sets) should be present.

Each account holder must be associated with one of the global limit groups.

### 2.4.2. Limit domains

Transaction engine assumes different domains of operations. Each domain
has quite specific limit requirements.

Continuous accounting must be present based on the following creteria per account holder:

1. `Retail` - purchase of goods and services
    - Limit types:
        - Daily limits:
            - RetailDailyAmt - daily amount
            - RetailDailyCnt - daily count
        - Weekly limits:
            - RetailWeeklyAmt - weekly amount
            - RetailWeeklyCnt - weekly count
        - Monthly limits:
            - MaxMonthlyAmt - monthly amount
            - MaxMonthlyCnt - monthly count
    - Accounting for affected transactions:
        - On blocking of balance - increase Used for blocked part
        - On unblocking of balance - decrease Used for unblocked part
        - On decreasing balance - increase Used
        - On increasing balance - no action
2. `Deposits` - in/out transfers of own money
    - Limit types:
        - Daily limits:
            - DepositDailyAmt - daily deposit amount
            - DepositDailyCnt - daily deposit count
            - WithdrawalDailyAmt - daily withdrawal amount
            - WithdrawalDailyCnt - daily withdrawal count
        - Weekly limits:
            - DepositWeeklyAmt - weekly deposit amount
            - DepositWeeklyCnt - weekly deposit count
            - WithdrawalWeeklyAmt - weekly withdrawal amount
            - WithdrawalWeeklyCnt - weekly withdrawal count
        - Monthly limits:
            - DepositMonthlyAmt - monthly deposit amount
            - DepositMonthlyCnt - monthly deposit count
            - WithdrawalMonthlyAmt - monthly withdrawal amount
            - WithdrawalMonthlyCnt - monthly withdrawal count
    - Accounting for affected transactions: Deposits & Withdrawals
        - canceled transactions should decrease statistics
3. `Payments` - transfers to other users
    - Limit types:
        - Daily limits:
            - OutboundDailyAmt - daily outbound amount
            - OutboundDailyCnt - daily outbound count
            - InboundDailyAmt - daily inbound amount
            - InboundDailyCnt - daily inbound count
        - Weekly limits:
            - OutboundWeeklyAmt - weekly outbound amount
            - OutboundWeeklyCnt - weekly outbound count
            - InboundWeeklyAmt - weekly inbound amount
            - InboundWeeklyCnt - weekly inbound count
        - Monthly limits:
            - OutboundMonthlyAmt - monthly outbound amount
            - OutboundMonthlyCnt - monthly outbound count
            - InboundMonthlyAmt - monthly inbound amount
            - InboundMonthlyCnt - monthly inbound count
    - Accounting for affected transactions: Deposits & Withdrawals
        - canceled transactions should decrease statistics
4. `Gaming` - in-game activity
    - Limit types:
        - Daily limits:
            - BetDailyAmt - daily bet amount
            - BetDailyCnt - daily bet count
            - WinDailyAmt - daily win amount
            - WinDailyCnt - daily win count
            - ProfitDailyDelta - daily player profit delta 
        - Weekly limits:
            - BetWeeklyAmt - weekly bet amount
            - BetWeeklyCnt - weekly bet count
            - WinWeeklyAmt - weekly win amount
            - WinWeeklyCnt - weekly win count
            - ProfitWeeklyDelta - weekly player profit delta
        - Monthly limits:
            - BetMonthlyAmt - monthly bet amount
            - BetMonthlyCnt - monthly bet count
            - WinMonthlyAmt - monthly win amount
            - WinMonthlyCnt - monthly win count
            - ProfitMonthlyDelta - monthly player profit delta
    - Accounting for affected transactions: Deposits & Withdrawals
        - canceled transactions should decrease statistics
5. `Misc` - not fitting other domains
    - Limit types:
        - Daily limits:
            - MessageDailyCnt - daily message count
            - FailureDailyCnt - daily failure count
            - LimitHitDailyCnt - daily limit hit count
        - Weekly limits:
            - MessageWeeklyCnt - weekly message count
            - FailureWeeklyCnt - weekly failure count
            - LimitHitWeeklyCnt - weekly limit hit count
        - Monthly limits:
            - MessageMonthlyCnt - monthly message count
            - FailureMonthlyCnt - monthly failure count
            - LimitHitMonthlyCnt - monthly limit hit count
6. `Personnel` - limits of operations done by specific employee
    - Limit types:
        - Daily limits:
            - MessageDailyCnt - daily message count
            - ManualDailyAmt - daily manual transaction amount
            - ManualDailyCnt - daily manual transaction count
        - Weekly limits:
            - MessageWeeklyCnt - weekly message count
            - ManualWeeklyAmt - weekly manual transaction amount
            - ManualWeeklyCnt - weekly manual transaction count
        - Monthly limits:
            - MessageMonthlyCnt - monthly message count
            - ManualMonthlyAmt - monthly manual transaction amount
            - ManualMonthlyCnt - monthly manual transaction count

### 2.4.3. Limit types:

#### 2.4.3.1. Per account limits

Such limit is set per single account in currency of the account.

1. NBL - Negative Balance Limit (a.k.a. Overdraft) - set by system

#### 2.4.3.2. Account holder limits

These are personal user limits which user configures based on own will. Such limits are bound
by system limits and act as threshold value.

1. Extended verification - requires system to get implementation-defined additional confirmation
    of user activity. For example, input of Two-Factor Authentication code.
    * RetailDailyAmt
2. Soft limits - user configured restrictions
    * RetailDailyAmt
    * WithdrawalDailyAmt
    * BetDailyAmt
    * OutboundDailyAmt

#### 2.4.3.3. Group system limits

1. Hard limits
    * All fields of the same name as statitics field act as maximum limit
    * `Retail`
        - `RetailMinAmt` - minimal transaction amount
    * `Deposits`
        - `DepositMinAmt` - minimal deposit amount
        - `WithdrawalMinAmt` - minimal withdrawal amount
    * `Payments` 
        - `OutboundMinAmt` - minimal outbound payment amount
    * `Gaming`
        - `BetMinAmt` - minimal bet amount
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

### 2.4.4. Events

* `LIM_UPD` - update of limits
* `LIM_HLDR_UPD` - update of account holder limits

## 2.5. Account holder

There is strict Know Your Customer (KYC) and related limit requirements for financial
systems in scope of AML/CTF efforts. It's the primary reason to introduce such entity.

As account holder information varies across the Globe, it should be abstract enough
to hold arbitrary data provided by actual implementation.

However, if data type is already defined as part of spec - it must be used instead of
optional extensions.

### 2.5.1. Known data types

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

### 2.5.2. Events

* `AH_NEW` - new account holder
* `AH_UPD` - update of account holder
* `AH_BLOCK` - on account holder being blocked

## 2.6. Messages

Due to security and traceability considerations use of third-party communication channels
may be undesired. A basic plain text in-system messaging feature is required for
operator <-> user communication in scope of transaction processing.

All other types of communications must be handled externally.

## 2.7. Security considerations

User authentication & authorization is out of scope of this spec. It should be defined
in scope of FTN8: Security.

Some withdrawal, purchase and peer-to-peer transactions may require extra account holder
confirmation based on Soft limit. The way to verify user confirmation should be also
derived from FTN8.

In other cases, when additional confirmation does not make any sense (e.g. in-game bets)
Soft limit should cause transaction rejection.

# 3. Interface

## 3.1. Common types

Common types to use in other interfaces of this spec.

`Iface{`

        {
            "iface" : "futoin.xfer.types",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.currency.types:1.0"
            ],
            "types" : {
                "UUIDB64" : {
                    "type" : "string",
                    "regex" : "^[A-Za-z0-9+/]{22}$"
                },
                "AccountID" : "UUIDB64",
                "AccountHolderID" : "UUIDB64",
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
                    "maxlen" : 32
                },
                "XferExtInfo" : "map",
                "Reason" : {
                    "type" : "string",
                    "maxlen" : 128
                },
                "LimitGroup" : {
                    "type" : "string",
                    "regex" : "^[a-zA-Z ]+$"
                },
                "LimitDomain" : {
                    "type" : "enum",
                    "items" : [
                        "Purchases",
                        "Transfers",
                        "Gaming",
                        "Personnel"
                    ]
                },
                "Fee" : {
                    "type" : "map",
                    "fields" : {
                        "currency" : "Currency",
                        "amount" : "Amount",
                        "reason" : "Reason"
                    }
                },
               "XferTimestamp" : {
                    "type" : "string",
                    "regex": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"
                }
            }
        }

`}Iface`

## 3.2. Currency

Currency-related services are assumed to be a separate module. In some cases,
tehre can be a single centralized service from which other instances sync. Therefore
there is a strict separation between management and information retrieval.

### 3.2.1. Types

Common types in scope for currency processing.

`Iface{`

        {
            "iface" : "futoin.currency.types",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "types" : {
                "CurrencyCode" : {
                    "type" : "string",
                    "regex" : "^[ICKL]:[A-Z]{1,7}$",
                    "desc" : "T:Code, see the spec"
                },
                "DecimalPlaces": {
                    "type" : "integer",
                    "min" : 0,
                    "max" : 8
                },
                "CurrencyName" : {
                    "type" : "string",
                    "minlen" : 1,
                    "maxlen" : 64
                },
                "CurrencySymbol" : {
                    "type" : "string",
                    "minlen" : 1,
                    "maxlen" : 3
                },
                "Currency" : {
                    "type" : "map",
                    "fields" : {
                        "code" : "CurrencyCode",
                        "dec_places" : "DecimalPlaces",
                        "name" : "CurrencyName",
                        "symbol" : "CurrencySymbol",
                        "enabled" : "boolean"
                    }
                },
                "CurrencyList" : {
                    "type" : "array",
                    "elemtype" : "Currency"
                },
                "ExRate" : {
                    "type" : "string",
                    "regex" : "^[0-9]{1,12}(\\.[0-9]{1,12})?$"
                }
            }
        }

`}Iface`

### 3.2.2. Management

Currency management API.

`Iface{`

        {
            "iface" : "futoin.currency.manage",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.currency.types:1.0"
            ],
            "funcs" : {
                "setCurrency" : {
                    "params" : {
                        "code" : "CurrencyCode",
                        "dec_places" : "DecimalPlaces",
                        "name" : "CurrencyName",
                        "symbol" : "CurrencySymbol",
                        "enabled" : "boolean"
                    },
                    "result" : "boolean",
                    "desc" : "Register or update currency",
                    "throws" : [
                        "DecPlaceMismatch",
                        "DuplicateNameOrSymbol"
                    ]
                },
                "setExRate" : {
                    "params" : {
                        "base" : "CurrencyCode",
                        "foreign" : "CurrencyCode",
                        "rate" : "ExRate",
                        "margin" : "ExRate"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownCurrency"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

### 3.2.3. Information

Currency information API.

`Iface{`

        {
            "iface" : "futoin.currency.info",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.currency.types:1.0"
            ],
            "funcs" : {
                "listCurrencies" : {
                    "result" : "CurrencyList"
                },
                "getExRate" : {
                    "params" : {
                        "base" : "CurrencyCode",
                        "foreign" : "CurrencyCode"
                    },
                    "result" : {
                        "rate" : "ExRate",
                        "margin" : "ExRate"
                    },
                    "throws" : [
                        "UnknownPair"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`


## 3.3. Accounts

Account management API for internal use only.

Merge functionality should be rarely used to workaround multiple registrations per single person
which may happen in some scenarios.


`Iface{`

        {
            "iface" : "futoin.xfer.accounts",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:1.0"
            ],
            "types" : {
                "AccountType" : {
                    "type" : "enum",
                    "items": [
                        "System",
                        "Regular",
                        "Transit",
                        "External"
                    ]
                },
                "AccountExternalID" : {
                    "type" : "string",
                    "maxlen" : 64
                },
                "AccountAlias" : {
                    "type" : "string",
                    "maxlen" : 20
                },
                "AccountHolderData" : {
                    "type" : "map"
                },
                "AccountHolderInternalData" : {
                    "type" : "map"
                }
            },
            "funcs" : {
                "setAccount" : {
                    "params" : {
                        "id" : {
                            "type" : "AccountID",
                            "default" : null
                        },
                        "type" : "AccountType",
                        "holder" : "AccountHolderID",
                        "currency" : "CurrencyCode",
                        "ext_id" : "AccountExternalID",
                        "alias" : "AccountAlias"
                    },
                    "result" : "AccountHolderID",
                    "throws" : [
                        "UnknownHolderID",
                        "UnknownAccountID",
                        "ImmutableMismatch"
                    ]
                },
                "listAccounts": {
                    "params" : {
                        "holder" : "AccountHolderID"
                    },
                    "result" : {
                        "id" : "AccountID",
                        "type" : "AccountType",
                        "currency" : "CurrencyCode",
                        "ext_id" : "AccountExternalID",
                        "alias" : "AccountAlias",
                        "balance" : "Balance",
                        "reserved" : "Amount",
                        "created" : "XferTimestamp"
                    },
                    "throws" : [
                        "UnknownHolderID"
                    ]
                },
                "convAccount" : {
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
                "setAccountHolder" : {
                    "params" : {
                        "id" : {
                            "type" : "AccountHolderID",
                            "default" : null
                        },
                        "group" : "LimitGroup",
                        "kyc" : "boolean",
                        "data" : "AccountHolderData",
                        "internal" : "AccountHolderInternalData"
                    },
                    "result" : "AccountHolderID"
                },
                "getAccountHolder" : {
                    "params" : {
                        "id" : "AccountHolderID"
                    },
                    "result" : {
                        "group" : "LimitGroup",
                        "kyc" : "boolean",
                        "data" : "AccountHolderData",
                        "internal" : "AccountHolderInternalData",
                        "created" : "XferTimestamp"
                    },
                    "throws" : [
                        "UnknownAccountHolder"
                    ]
                },
                "mergeAccountHolders" : {
                    "params" : {
                        "id" : "AccountHolderID",
                        "other_id" : "AccountHolderID"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownAccountHolder"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

## 3.4. Transactions

Specific instances of transaction engine may support only subset of all
possible transaction processing features. Therefore, each part is split
into own interface/module.

General notes for canellation: even if transaction is not known, it must be marked
as canceled. So, if original transaction request comes after cancel request, it should
get "AlreadyCanceled" status.

A special system "External" account ID is assumed in "rel_account" field. It is used as
source of/sink for transaction credits. Primary reason is to manage limits per external
system. It may also aid integrity checks.

### 3.4.1. Deposits

Processing of deposit transactions. Actual external processing & integration
is out of scope. The interface is only responsible for "recording" fact of
transaction.

`Iface{`

        {
            "iface" : "futoin.xfer.deposit",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:1.0"
            ],
            "funcs" : {
                "preDepositCheck" : {
                    "params" : {
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "fee" : {
                            "type" : "Fee",
                            "default" : null
                        }
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownAccountID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject"
                    ],
                    "desc" : "Check if system allows deposit"
                },
                "onDeposit" : {
                    "params" : {
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "ext_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp",
                        "fee" : {
                            "type" : "Fee",
                            "default" : null
                        }
                    },
                    "result" : "XferID",
                    "throws" : [
                        "UnknownAccountID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject",
                        "OriginalTooOld"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

### 3.4.2. Withdrawals

Similar to deposits, this interface is only reponsible for in-system
processing of withdrawal transactions. External processing is out of scope.

`Iface{`

        {
            "iface" : "futoin.xfer.withdraw",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:1.0"
            ],
            "funcs" : {
                "startWithdrawal" : {
                    "params" : {
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "fee" : {
                            "type" : "Fee",
                            "default" : null
                        }
                    },
                    "result" : {
                        "xfer_id" : "XferID",
                        "wait_check" : "boolean"
                    },
                    "throws" : [
                        "UnknownAccountID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject",
                        "AlreadyCanceled",
                        "OriginalTooOld"
                    ]
                },
                "confirmWithdrawal" : {
                    "params" : {
                        "account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "xfer_id" : "XferID",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownXferID",
                        "AlreadyCanceled",
                        "OriginalTooOld"
                    ]
                },
                "completeWithdrawal" : {
                    "params" : {
                        "ref_id" : "XferID",
                        "ext_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownXferID",
                        "AlreadyCanceled",
                        "NotConfirmed",
                        "OriginalTooOld"
                    ]
                },
                "cancelWithdrawal" : {
                    "params" : {
                        "ref_id" : "XferID",
                        "reason" : "Reason",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownXferID",
                        "AlreadyCompleted",
                        "OriginalTooOld"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

### 3.4.3. Gaming

This module is focused on processing of gaming transactions. It should be supported
only for e-gaming and similar projects with real-time transactions.

Unlike other interfaces, there is no Account ID involved directly as it assumed that there is
is unique pair of AccountHolderID + CurrencyCode for Regular Account type. However, it's possible
to have more than one Bonus account types for proper bonus amount processing.

If there are associated bonus accounts of specified currency then their balance must be used in first place
in creation order. If more than one account is used for placing of bets then win amount must be distributed
proportionally. Creation, cancellation and release of bonus accounts is out of scope.

It must not happen that "cancelBet" is called after any related "win". "ext_info" should include information
about related game round in "round_id" field.

The interface is still internall and must not be exposed.

`Iface{`

        {
            "iface" : "futoin.xfer.gaming",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:1.0"
            ],
            "funcs" : {
                "bet" : {
                    "params" : {
                        "holder" : "AccountHolderID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "ext_id" : "XferExtId",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : {
                        "xfer_id" : "XferID",
                        "balance" : "Balance",
                        "bonus_part" : "Amount"
                    },
                    "throws" : [
                        "UnknownHolderID",
                        "CurrencyMismatch",
                        "OutOfBalance",
                        "LimitReject",
                        "DataMismatch",
                        "AlreadyCanceled",
                        "OriginalTooOld"
                    ]
                },
                "cancelBet" : {
                    "params" : {
                        "holder" : "AccountHolderID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "ext_id" : "XferExtId",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : {
                        "balance" : "Balance"
                    },
                    "throws" : [
                        "DataMismatch",
                        "OriginalTooOld"
                    ]
                },
                "win" : {
                    "params" : {
                        "holder" : "AccountHolderID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "ext_id" : "XferExtId",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : {
                        "xfer_id" : "XferID",
                        "balance" : "Balance",
                        "bonus_part" : "Amount"
                    },
                    "throws" : [
                        "UnknownHolderID",
                        "CurrencyMismatch",
                        "LimitReject",
                        "DataMismatch",
                        "OriginalTooOld"
                    ]
                },
                "gameBalance" : {
                    "params" : {
                        "holder" : "AccountHolderID",
                        "currency" : "CurrencyCode"
                    },
                    "result" : {
                        "balance" : "Balance",
                        "bonus_part" : "Amount"
                    },
                    "throws" : [
                        "UnknownHolderID",
                        "CurrencyMismatch"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

### 3.4.4. Sales

This interface is responsible for processing transactions in scope of goods and 
service purchase.

`Iface{`

        {
            "iface" : "futoin.xfer.sales",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:1.0"
            ],
            "funcs" : {
                "purchase" : {
                    "params" : {
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "ext_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp",
                        "fee" : {
                            "type" : "Fee",
                            "default" : null
                        },
                        "rel_auth_id" : {
                            "type" : "XferID",
                            "default" : null
                        }
                    },
                    "result" : {
                        "xfer_id" : "XferID",
                        "wait_check" : "boolean"
                    },
                    "throws" : [
                        "UnknownAccountID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject",
                        "AlreadyCanceled",
                        "OriginalTooOld"
                    ]
                },
                "cancelPurchase" : {
                    "params" : {
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "ext_id" : "XferExtID",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "DataMismatch"
                    ]
                },
                "refund" : {
                    "params" : {
                        "ref_id" : "XferID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "ext_id" : "XferExtID",
                        "purchase_ts" : "XferTimestamp",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "CurrencyMismatch",
                        "AmountTooLarge",
                        "PurchaseNotFound",
                        "AlreadyCanceled",
                        "OriginalTooOld"
                    ]
                },
                "preAuth" : {
                    "params" : {
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "ext_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : {
                        "xfer_id" : "XferID",
                        "wait_check" : "boolean"
                    },
                    "throws" : [
                        "UnknownAccountID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject",
                        "AlreadyCanceled",
                        "OriginalTooOld"
                    ]
                },
                "clearPreAuth" : {
                    "params" : {
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "ext_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp",
                        "rel_id" : {
                            "type" : "XferID",
                            "default" : null
                        }
                    },
                    "result" : "boolean",
                    "throws" : [
                        "DataMismatch",
                        "OriginalTooOld"
                    ]
                },
                "confirmAuth" : {
                    "params" : {
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "xfer_id" : "XferID",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownXferID",
                        "AlreadyCanceled",
                        "OriginalTooOld"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`


### 3.4.5. Bonus

`Iface{`

        {
            "iface" : "futoin.xfer.bonus",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:1.0"
            ],
            "funcs" : {
                "claimBonus" : {
                    "params" : {
                        "holder" : "AccountHolderID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "ext_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : "AccountID",
                    "throws" : [
                        "UnknownHolderID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject",
                        "OriginalTooOld"
                    ]
                },
                "clearBonus" : {
                    "params" : {
                        "holder" : "AccountHolderID",
                        "bonus" : "AccountID"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownHolderID",
                        "UnknownBonus"
                    ]
                },
                "releaseBonus" : {
                    "params" : {
                        "holder" : "AccountHolderID",
                        "bonus" : "AccountID"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownHolderID",
                        "UnknownBonus"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

### 3.4.6. Generic

`Iface{`

        {
            "iface" : "futoin.xfer.generic",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:1.0"
            ],
            "funcs" : {
                "fee" : {
                    "params" : {
                        "holder" : "AccountHolderID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "reason" : "Reason",
                        "ext_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp",
                        "force" : "boolean"
                    },
                    "result" : "XferID",
                    "throws" : [
                        "UnknownHolderID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject",
                        "OriginalTooOld"
                    ]
                },
                "genericXfer" : {
                    "params" : {
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "reason" : "Reason"
                    },
                    "result" : "XferID",
                    "throws" : [
                        "UnknownAccountID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject"
                    ]
                    
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

## 3.5. Limits

Internal API for limits configuration.

`Iface{`

        {
            "iface" : "futoin.xfer.limits",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:1.0"
            ],
            "types" : {
                "LimitXferCount" : {
                    "type" : "integer",
                    "min" : 0
                },
                "LimitValues" : {
                    "type" : "map"
                },
                "LimitGroups" : {
                    "type" : "array",
                    "elemtype" : "LimitGroup"
                }
            },
            "funcs" : {
                "setLimits" : {
                    "params" : {
                        "group" : "LimitGroup",
                        "domain" : "LimitDomain",
                        "hard" : "LimitValues",
                        "check" : "LimitValues",
                        "risk" : "LimitValues"
                    }
                },
                "getLimits" : {
                    "params" : {
                        "group" : "LimitGroup",
                        "domain" : "LimitDomain"
                    },
                    "result" : {
                        "hard" : "LimitValues",
                        "check" : "LimitValues",
                        "risk" : "LimitValues"
                    }
                },
                "getLimitGroups" : {
                    "result" : "LimitGroups"
                },
                "setHolderLimits" : {
                    "params" : {
                        "holder" : "AccountHolderID",
                        "domain" : "LimitDomain",
                        "soft" : "LimitValues",
                        "check" : "LimitValues"
                    }
                },
                "getHolderLimits" : {
                    "params" : {
                        "holder" : "AccountHolderID",
                        "domain" : "LimitDomain"
                    },
                    "result" : {
                        "check" : "LimitValues",
                        "soft" : "LimitValues"
                    }
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

## 3.7. Messages

TBD.

=END OF SPEC=
