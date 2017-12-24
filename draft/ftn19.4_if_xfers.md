<pre>
FTN19.4: FutoIn Interface - Transaction Engine - Transactions
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

# 2. Concept (Transactions)

## 2.1. Types

The following list is recommendation. Particular implementation may
omit some or add additional types. However, if type is already listed in the spec
then it must be used.

* Large amounts with extra checks:
    * Deposit - funds deposit from external source
    * Withdrawal - funds withdrawal to external destination
    * CancelWithdrawal - cancel not completed withdrawal
* Relatively small amounts with real-time transactions:
    * Bet - gaming bet
    * Win - gaming win
    * CancelBet - cancel gaming bet due to canceled game or late bet
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
    * Settle - settlement related to External accounts
    * Generic - generic transaction not related to others, e.g. peer-to-peer

## 2.2. Fees

As many transaction processing types involve expenses for operator they may be accompanied
by Fee transaction which should be atomically processed with relates transaction.

Fees due to operation initiatied by account holder action should not allow account
balance to become negative. Other type of fees may result in negative account balance,
if the cause is unavoidable.

## 2.3. Transaction processing & error recovery

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
    * `orig_ts` is approximate value with 24h precision - it's minor mismatch must not cause failure

## 2.4. Transaction use case

In all cases, if not noted otherwise, Withdrawals, Refunds, Wins, ClearBonus go in opposite direction
of Deposits, Purchases, Bets and Bonus respectively. 

Pre-authorizations must be reserved only on Regular accounts.

### 2.4.1. Online bank

1. Natural persons & companies have Regular accounts
2. Funds deposit in bank branch goes from System(Bank) to Regular(User) account
3. Transfers to another bank go from Regular(User) to External(OtherBank) correspondent account
4. Inter-bank settlement goes as transaction between External(OtherBank) and System(Bank) accounts
5. Purchases from Regular(Person) to Regular(Company) accounts
6. Fees go from Regular(User) to System(Bank) accounts
7. In-bank transfers go from Regular(User) to Regular(User)

### 2.4.2. General integration of third-party service (Payments, Gaming, Retail, etc.)

Third-party service may be integrated through External(Service) accounts:

* Purchases go from Regular(User) to External(Service) accounts
* Deposits go from External(Service) to Regular(User) accounts
* Settlement is done from/to System(Bank) to External(Service)
* External(Service) account should be constrained by negative balance limit

### 2.4.3. Closed loop online gaming system

1. Players get single per currency Regular accounts and unlimited number of Bonus accounts
2. Deposits go from System(Service) to Regular(Player)
3. Bets go from Regular(Player) to System(Service)
    * Associated Bonus(Player) accounts are used in first place by time of claim
    * Bets go from Bonus(Player) to System(Service) account
    * It's possible to have more than one transaction per single bet
4. Purchases go from Regular(Player) to System(Service)
5. Bonus goes from System(Service) to Bonus(Player) accounts

### 2.4.4. Online gaming service provider

1. Players get Transit account, single per currency
2. No deposits or withdrawals are assumed
3. Bets go from External(Operator) to Transit(Player) to System(Service)
4. Purchases go from External(Operator) to Transit(Player) to System(Service)
5. Bonus amount is not processed separately in transaction, but should be availabe in extended
    info for fine reporting (out of scope)
6. Settlement is done between Externa(Operator) and System(Service) accounts
7. External(Operator) account should be constrained by negative balance limit

### 2.4.5. Online gaming operator

1. Players get single per currency Regular accounts and unlimited number of Bonus accounts
2. In-house Deposits go from System(Operator) to Regular(Player)
3. Payments Deposits go from External(Payments) to Regular(Player) accounts
4. Bets go from Regular(Player) to External(Service) accounts
5. Purchases go from Regular(Player) to External(Service) accounts
6. Purchases in Operator go from Regular(Player) to System(Operator) accounts
7. External(Payments) and External(Service) accounts should be constrained by negative balance limit
8. Settlement is done between System(Operator) and External accounts

### 2.4.6. Online gaming pass-through aggregator

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

### 2.4.7. Payments provider

1. For each User a Transit account is created, Operators have External account
2. No gaming or sales transactions are assumed
3. Deposits go from System(Payments) to Transit(User) to External(Operator) accounts
4. Settlement is done between System(Payments) and External(Operator) accounts
5. External(Operator) accounts should be constrained by negative balance limit

### 2.4.8. Payments aggregator

1. For each User a Transit account is created, Operators and Payment providers have External accounts
2. No gaming or sales transactions are assumed
3. Deposits go from External(Payments) to Transit(User) to External(Operator) accounts
4. Settlement is done between System(Aggregator) and External accounts
5. External accounts should be constrained by negative balance limit

## 2.5. Unattended external processing

There are cases when user wallet is managed outside of the system while transaction engine
has control only over Transit account. All operations on Transit account must require online
communication with external peer systems.

Similar to that synchronous risk assessment can be done in scope of single transaction processing.

Transaction engine should automatically workaround interruptions and repeated calls for error recovery.

There should be unified interface for transaction operation with only difference - time required
for operation.

## 2.6. Human-involved external processing

Some operations like withdrawals, purchases or manual risk analysis require
relatively long interruption for human confirmation/rejection. Interface for such operations
assumes such interruption by splitting processing into different API calls.

## 2.7. Events

* 'XFER_NEW' - new xfer added
* 'XFER_UPD' - on xfer status update
* 'XFER_ERR' - on internal xfer failure
* 'XFER_EXTERR' - on external xfer failure

# 3. Interface (Transaction)

*The interfaces defined here as well as in other parts of FTN19 are designed for INTERNAL USE.*

Specific instances of transaction engine may support only subset of all
possible transaction processing features. Therefore, each part is split
into own interface/module.

General notes for cancellation: even if transaction is not known, it must be marked
as canceled. So, if original transaction request comes after cancel request, it should
get "AlreadyCanceled" status.

A special system "External" account ID is assumed in "rel_account" field. It is used as
source of/sink for transaction credits. Primary reason is to manage limits per external
system. It may also aid integrity checks.

## 3.1. Deposits

Processing of deposit transactions. Actual external processing & integration
is out of scope. The interface is only responsible for "recording" fact of
transaction.

Fee is deducted from deposit amount.

`Iface{`

        {
            "iface" : "futoin.xfer.deposit",
            "version" : "{ver}",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:{ver}"
            ],
            "funcs" : {
                "preDepositCheck" : {
                    "params" : {
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount"
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
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

## 3.2. Withdrawals

Similar to deposits, this interface is only reponsible for in-system
processing of withdrawal transactions. External processing is out of scope.

Fee is processed as extra on top of transaction amount.

`Iface{`

        {
            "iface" : "futoin.xfer.withdraw",
            "version" : "{ver}",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:{ver}"
            ],
            "funcs" : {
                "startWithdrawal" : {
                    "params" : {
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "ext_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp",
                        "extra_fee" : {
                            "type" : "Fee",
                            "default" : null
                        }
                    },
                    "result" : {
                        "xfer_id" : "XferID",
                        "wait_user" : "boolean"
                    },
                    "throws" : [
                        "UnknownAccountID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject",
                        "NotEnoughFunds",
                        "AlreadyCanceled"
                    ]
                },
                "confirmWithdrawal" : {
                    "params" : {
                        "xfer_id" : "XferID",
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "orig_ts" : "XferTimestamp",
                        "extra_fee" : {
                            "type" : "Fee",
                            "default" : null
                        }
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownXferID",
                        "AlreadyCanceled",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                },
                "rejectWithdrawal" : {
                    "params" : {
                        "xfer_id" : "XferID",
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "orig_ts" : "XferTimestamp",
                        "extra_fee" : {
                            "type" : "Fee",
                            "default" : null
                        }
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownXferID",
                        "AlreadyCompleted",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

## 3.3. Gaming

This module is focused on processing of gaming transactions. It should be supported
only for e-gaming and similar projects with real-time transactions.

Unlike other interfaces, there is no Account ID involved directly as it assumed that there is
is unique pair of AccountHolderID + CurrencyCode for Regular Account type. However, it's possible
to have more than one Bonus account types for proper bonus amount processing.

If there are associated bonus accounts of specified currency then their balance must be
used in creation order (date), but only after main account is depleted.

For simplicity reasons, if main account is transit then "NotEnoughFunds" error is seen as
"depleted" account even though some funds remain available for betting. Such situation may
happen only if Bonus and Wallet systems are located on different nodes.

If more than one account is used for placing of bets then win amount must be distributed
proportionally excluding non-Bonus accounts for fraud mitigation reasons.

Creation, cancellation and release of bonus accounts is out of scope.

It must not happen that "cancelBet" is called after any related "win". "round_id" is used to tie
bets to wins for proper bonus win calculations and general security.

The "gameBalance" call may return different amounts based external info details (out of scope).

The interface is still internal and must not be exposed.

`Iface{`

        {
            "iface" : "futoin.xfer.gaming",
            "version" : "{ver}",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:{ver}"
            ],
            "types" : {
                "RelatedBetPH" : {
                    "type" : "enum",
                    "items" : [
                        "%FreeSpin%",
                        "%Prize%",
                        "%Award%"
                    ]
                },
                "RelatedBet" : [ "XferExtID", "RelatedBetPH" ]
            },
            "funcs" : {
                "bet" : {
                    "params" : {
                        "user" : "AccountHolderExternalID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "round_id" : "XferExtID",
                        "ext_id" : "XferExtID",
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
                        "AlreadyCanceled",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                },
                "cancelBet" : {
                    "params" : {
                        "user" : "AccountHolderExternalID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "round_id" : "XferExtID",
                        "ext_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp",
                        "reason" : "Reason"
                    },
                    "result" : {
                        "balance" : "Balance"
                    },
                    "throws" : [
                        "UnknownHolderID",
                        "CurrencyMismatch",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                },
                "win" : {
                    "params" : {
                        "user" : "AccountHolderExternalID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "round_id" : "XferExtID",
                        "ext_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : {
                        "xfer_id" : "XferID",
                        "balance" : "Balance"
                    },
                    "throws" : [
                        "UnknownHolderID",
                        "CurrencyMismatch",
                        "LimitReject",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                },
                "gameBalance" : {
                    "params" : {
                        "user" : "AccountHolderExternalID",
                        "currency" : "CurrencyCode",
                        "ext_info" : {
                            "type": "XferExtInfo",
                            "default": null
                        }
                    },
                    "result" : {
                        "balance" : "Balance"
                    },
                    "throws" : [
                        "UnknownHolderID",
                        "UnknownCurrency",
                        "CurrencyMismatch"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

## 3.4. Retail

This interface is responsible for processing transactions in scope of goods and 
service purchase.

Refunds is assumed to be partial. Otherwise, cancelPurchase must be used.

Refund is a separate transaction type. Therefore, it does not return xfer fee.

`Iface{`

        {
            "iface" : "futoin.xfer.retail",
            "version" : "{ver}",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:{ver}"
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
                        "rel_preauth" : {
                            "type" : "XferID",
                            "default" : null
                        }
                    },
                    "result" : {
                        "xfer_id" : "XferID",
                        "wait_user" : "boolean"
                    },
                    "throws" : [
                        "UnknownAccountID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject",
                        "AlreadyCanceled",
                        "OriginalTooOld",
                        "OriginalMismatch",
                        "UnavailablePreAuth"
                    ]
                },
                "cancelPurchase" : {
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
                        "reason" : "Reason"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownAccountID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject",
                        "OriginalTooOld",
                        "OriginalMismatch",
                        "AlreadyRefunded"
                    ]
                },
                "confirmPurchase" : {
                    "params" : {
                        "xfer_id" : "XferID",
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "orig_ts" : "XferTimestamp",
                        "fee" : {
                            "type" : "Fee",
                            "default" : null
                        }
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownXferID",
                        "AlreadyCanceled",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                },
                "rejectPurchase" : {
                    "params" : {
                        "xfer_id" : "XferID",
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "orig_ts" : "XferTimestamp",
                        "fee" : {
                            "type" : "Fee",
                            "default" : null
                        }
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownXferID",
                        "AlreadyCompleted",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                },
                "refund" : {
                    "params" : {
                        "purchase_id" : "XferID",
                        "purchase_ts" : "XferTimestamp",
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "ext_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "CurrencyMismatch",
                        "NotEnoughFunds",
                        "AmountTooLarge",
                        "PurchaseNotFound",
                        "AlreadyCanceled",
                        "OriginalTooOld",
                        "OriginalMismatch"
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
                        "wait_user" : "boolean"
                    },
                    "throws" : [
                        "UnknownAccountID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject",
                        "AlreadyCanceled",
                        "OriginalTooOld",
                        "OriginalMismatch"
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
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                },
                "confirmPreAuth" : {
                    "params" : {
                        "xfer_id" : "XferID",
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownXferID",
                        "AlreadyCanceled",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                },
                "rejectPreAuth" : {
                    "params" : {
                        "xfer_id" : "XferID",
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownXferID",
                        "AlreadyCompleted",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`


## 3.5. Bonus

Manage claiming, canceling and releasing bonus. To avoid confusion
with regular transaction cancel, cancel operation is called "clear".

`ext_id` on claim is used as external account ID and as transaction ID.

`Iface{`

        {
            "iface" : "futoin.xfer.bonus",
            "version" : "{ver}",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:{ver}"
            ],
            "funcs" : {
                "claimBonus" : {
                    "params" : {
                        "user" : "AccountHolderExternalID",
                        "rel_account" : "AccountID",
                        "alias" : "AccountAlias",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "bonus_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownHolderID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                },
                "clearBonus" : {
                    "params" : {
                        "user" : "AccountHolderExternalID",
                        "rel_account" : "AccountID",
                        "bonus_id" : "XferExtID"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownHolderID",
                        "UnknownAccountID",
                        "AlreadyReleased"
                    ]
                },
                "releaseBonus" : {
                    "params" : {
                        "user" : "AccountHolderExternalID",
                        "rel_account" : "AccountID",
                        "bonus_id" : "XferExtID"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownHolderID",
                        "UnknownAccountID",
                        "AlreadyCanceled"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

## 3.6. Direct Payments

Direct payments interface for incoming and outgoing payment processing.

`Iface{`

        {
            "iface" : "futoin.xfer.direct",
            "version" : "{ver}",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:{ver}"
            ],
            "funcs" : {
                "startOutbound" : {
                    "params" : {
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "ext_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp",
                        "extra_fee" : {
                            "type" : "Fee",
                            "default" : null
                        }
                    },
                    "result" : {
                        "xfer_id" : "XferID",
                        "wait_user" : "boolean"
                    },
                    "throws" : [
                        "UnknownHolderID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject",
                        "OriginalTooOld",
                        "OriginalMismatch",
                        "NotEnoughFunds",
                        "AlreadyCanceled"
                    ]
                },
                "confirmOutbound" : {
                    "params" : {
                        "xfer_id" : "XferID",
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "orig_ts" : "XferTimestamp",
                        "extra_fee" : {
                            "type" : "Fee",
                            "default" : null
                        }
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownXferID",
                        "AlreadyCanceled",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                },
                "rejectOutbound" : {
                    "params" : {
                        "xfer_id" : "XferID",
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "orig_ts" : "XferTimestamp",
                        "extra_fee" : {
                            "type" : "Fee",
                            "default" : null
                        }
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownXferID",
                        "AlreadyCompleted",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                },
                "onInbound" : {
                    "params" : {
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "ext_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp",
                        "xfer_fee" : {
                            "type" : "Fee",
                            "default" : null
                        }
                    },
                    "result" : "XferID",
                    "throws" : [
                        "UnknownHolderID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

## 3.7. Generic

This interface is assumed to be used for operator activities and automatic scheduled tasks.

Settlement is used to adjust balance to reflect external operations like payment or some
valuables transfer done outside.

All transactions are processed as force and may result in negative balance.

`Iface{`

        {
            "iface" : "futoin.xfer.generic",
            "version" : "{ver}",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:{ver}"
            ],
            "types" : {
                "CancelableXferType" : {
                    "type" : "enum",
                    "items" : [
                        "Deposit",
                        "Withdrawal",
                        "Purchase",
                        "Refund",
                        "PreAuth",
                        "Win",
                        "Fee",
                        "Settle",
                        "Generic"
                    ]
                }
            },
            "funcs" : {
                "fee" : {
                    "params" : {
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
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
                        "NotEnoughFunds",
                        "LimitReject",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                },
                "settle" : {
                    "params" : {
                        "account" : "AccountID",
                        "rel_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "reason" : "Reason",
                        "ext_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : "XferID",
                    "throws" : [
                        "UnknownAccountID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "NotEnoughFunds",
                        "LimitReject",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                },
                "cancel" : {
                    "params" : {
                        "xfer_id" : "XferID",
                        "type" : "CancelableXferType",
                        "src_account" : "AccountID",
                        "dst_account" : "AccountID",
                        "currency" : "CurrencyCode",
                        "amount" : "Amount",
                        "orig_ts" : "XferTimestamp",
                        "xfer_fee" : {
                            "type" : "Fee",
                            "default" : null
                        },
                        "extra_fee" : {
                            "type" : "Fee",
                            "default" : null
                        },
                        "reason" : "Reason"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownAccountID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "NotEnoughFunds",
                        "LimitReject",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

## 3.8. Cluster peer interface

It is assumed that all external systems operate on the same transaction interfaces
as already defined above.

External IDs in "current" systems refer to internal IDs in "other" system and vice-versa.

This interface is left as placeholder for system-to-system interface not defined in
other specs.

`Iface{`

        {
            "iface" : "futoin.xfer.peer",
            "version" : "{ver}",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.xfer.types:{ver}"
            ],
            "funcs" : {
                "pair" : {
                    "params" : {
                        "ext_id" : "AccountExternalID",
                        "currency" : "CurrencyCode",
                        "alias" : "AccountAlias"
                    },
                    "result" : "AccountID",
                    "throws" : [
                        "CurrencyMismatch"
                    ]
                },
                "rawXfer" : {
                    "params" : {
                        "to_external" : "boolean",
                        "xfer_type" : "XferType",
                        "orig_currency" : "CurrencyCode",
                        "orig_amount" : "Amount",
                        "src_account" : "AccountID",
                        "src_currency" : "CurrencyCode",
                        "src_amount" : "Amount",
                        "dst_account" : "AccountID",
                        "dst_currency" : "CurrencyCode",
                        "dst_amount" : "Amount",
                        "ext_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp"
                    },
                    "result" : "XferID",
                    "throws" : [
                        "UnknownAccountID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject",
                        "OriginalTooOld",
                        "OriginalMismatch",
                        "NotEnoughFunds",
                        "AlreadyCanceled"
                    ]
                },
                "cancelXfer" : {
                    "params" : {
                        "to_external" : "boolean",
                        "xfer_type" : "XferType",
                        "orig_currency" : "CurrencyCode",
                        "orig_amount" : "Amount",
                        "src_account" : "AccountID",
                        "src_currency" : "CurrencyCode",
                        "src_amount" : "Amount",
                        "dst_account" : "AccountID",
                        "dst_currency" : "CurrencyCode",
                        "dst_amount" : "Amount",
                        "ext_id" : "XferExtID",
                        "ext_info" : "XferExtInfo",
                        "orig_ts" : "XferTimestamp",
                        "reason" : "Reason"
                    },
                    "result" : "boolean",
                    "throws" : [
                        "UnknownAccountID",
                        "CurrencyMismatch",
                        "InvalidAmount",
                        "LimitReject",
                        "OriginalTooOld",
                        "OriginalMismatch"
                    ]
                }
            },
            "requires" : [ "SecureChannel" ]
        }

`}Iface`

=END OF SPEC=
