<pre>
FTN20: FutoIn Interface - Payment Service Provider
Version: 0.1DV
Date: 2017-12-16
Copyright: 2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* DV - 2017-12-16 - Andrey Galkin
    - Initial draft

# 1. Intro

There is a demand for common Payment Service Provider (PSP)
interface to unify uncountable numbers of protocols in the market.

The priorities are payment industry grade transaction consistency control
and reliable automatic error recovery.

The specifications covers interface between merchant and PSP. Therefore,
it also coveres PSP-to-PSP cases when one of PSP acts on behalf of merchant.

# 2. Concept

This PSP interface is heavily based on assumptions and types of
[FTN19: FutoIn Interface - Transaction Engine](./ftn19\_if\_xfer\_engine.md).

There are several areas related to PSP, but those can separated into inbound
and outbound transactions.

## 2.1. Basic interaction

Unlike many protocols in the market, there are no callbacks from PSP allowed
as merchant's system code quality is quite low in many cases by fact. So, there
is a large security problem due to incorrect request handling.

However, in many cases users are required to be redirected to PSP or owm bank
page for secure authorization of payments. As it's unavoidable that
user gets redirected to another page or application, it the information passed
through user (app/browser) should be minimized to related transaction ID and
other not essential data. It must be impossible for user to alter even encrypted/signed data the way it would affect transaction processing.

## 2.2. Region-based restrictions

Very often old world order imposes different restrictions and sanctions
for doing business and processing of financial transfers. Therefore, PSP
protocol has to reflect them as well.

Protocols refers to regions with the following prefixes:
* "I:" - ISO 3166-1 alpha-3 namespace.
* "K:" - for countries of Confederation of Reasonable Legal Freedom
* "L:" - for closed loop custom operator-defined namespaces

The namespace can be sub-namespaces with ":" separator.

There are two approaches for restrictions:
* "only_in" - functionality accessible only in specific regions
* "except_for" - functionality not accessible in specific regions

## 2.3. General error control

Unless otherwise noted, each transaction call must be repeated until it succeeds or
expected errors occurs.

## 2.4. Parties

1. *PSP* - Payment Service Provider as the main party
2. *Merchant* - user of PSP services
    - API integration assumed
3. *Client* - user of Merchant system
    - may be user of PSP as well
    - human interaction assumed, but API integration is optional

# 3. Interface

## 3.1. Common types

Common types to use in PSP interfaces.

`Iface{`

    {
        "iface" : "futoin.psp.types",
        "version" : "{ver}",
        "ftn3rev" : "1.8",
        "imports" : [
            "futoin.types:1.0",
            "futoin.currency.types:1.0",
            "futoin.xfer.types:1.0"
        ],
        "types" : {
            "AVSCode" : {
                "type" : "string",
                "regex" : "^[A-z0-9]{1}$"
            },
            "ComisionRate" : {
                "type" : "string",
                "regex" : "^0(\\.[0-9]{1,12})?$"
            },
            "CVVCode" : {
                "type" : "string",
                "regex" : "^[A-z0-9]{1}$"
            },
            "InvoiceID" : "XferExtID",
            "MethodAlias" : {
                "type" : "string",
                "regex" : "^[a-b][a-b0-9_]{1,30}[a-b0-9]$"
            },
            "MethodInfo" : {
                "type" : "map",
                "fields" : {
                    "alias" : "MethodAlias",
                    "min" : "Amount",
                    "max" : "Amount",
                    "fee" : {
                        "type" : "Amount",
                        "optional" : true
                    },
                    "commision" : {
                        "type" : "ComisionRate",
                        "optional" : true
                    },
                    "only_in" : {
                        "type" : "RegionList",
                        "optional" : true
                    },
                    "except_for" : {
                        "type" : "RegionList",
                        "optional" : true
                    }
                }
            },
            "MethodInfoList" : {
                "type" : "array",
                "elemtype" : "MethodInfo",
                "maxlen" : 100
            },
            "RedirectURL" : {
                "type" : "string",
                "regex" : "^(https://[a-z0-9-]+(\\.[a-z0-9-]+)+/[A-Za-z0-9\\-._~%:/?#[\\]@!$&'()*+,;=])?$"
            },
            "Region" : {
                "type" : "string",
                "regex" : "^[IKL]:[A-Z]{1,16}(:[A-Z0-9]{1,16})?$",
                "desc" : "T:Code, see the spec"
            },
            "RegionList" : {
                "type" : "array",
                "elemtype" : "Region",
                "minlen" : 1,
                "maxlen" : 1000
            },
            "SaleResult" : {
                "type" : "map",
                "fields" : {
                    "reason" : {
                        "type" : "string",
                        "optional" : true
                    },
                    "auth_code" : {
                        "type" : "string",
                        "optional" : true
                    },
                    "avs_code" : {
                        "type" : "AVSCode",
                        "optional" : true
                    },
                    "cvv_code" : {
                        "type" : "CVVCode",
                        "optional" : true
                    },
                    "passed_3ds" : {
                        "type" : "boolean",
                        "optional" : true
                    },
                    "other" : {
                        "type" : "any",
                        "optional" : true
                    }
                }
            },
            "PaymentToken" : "UUIDB64"
        }
    }

`}Iface`

## 3.2. Merchant facing interfaces

### 3.2.1. Sales interface

This interface is focused on goods and services sale with optional
partial or full refund of transactions.

1. Payment is initiated with "sale" call from Merchant's system.
    - Note: optional invoice with details can be set in advance.
2. If result "url" is not empty string then client must be redirected to the specified URL.
3. Out-of-scope client authentication and payment authorization is done.
4. PSP redirects user back to pre-configured URL in Merchant's with "id" GET parameter equal to "ext_id" in sale call.
    - Note: pre-configured URL is intentional to minimize security risk of incorrect Merchant's implementation.
5. Merchant's system does "status" call to find out if payment's status.


`Iface{`

    {
        "iface" : "futoin.psp.sale",
        "version" : "{ver}",
        "ftn3rev" : "1.8",
        "imports" : [
            "futoin.psp.types:{ver}"
        ],
        "funcs" : {
            "methods" : {
                "params" : {
                    "currency" : "CurrencyCode"
                },
                "result" : "MethodInfoList",
                "throws" : [
                    "UnknownCurrency"
                ]
            },
            "sale" : {
                "params" : {
                    "method" : "MethodAlias",
                    "ext_id" : "XferExtID",
                    "currency" : "CurrencyCode",
                    "amount" : "Amount",
                    "invoice" : {
                        "type" : "InvoiceID",
                        "default" : null
                    }
                },
                "result" : {
                    "id" : "XferID",
                    "url" : "RedirectURL"
                },
                "throws" : [
                    "UnknownCurrency",
                    "UnknownMethod",
                    "UnknownInvoice",
                    "LimitRejected"
                ]
            },
            "status" : {
                "params" : {
                    "id" : "XferID"
                },
                "result" : {
                    "method" : "MethodAlias",
                    "ext_id" : "XferExtID",
                    "currency" : "CurrencyCode",
                    "amount" : "Amount",
                    "info" : "SaleResult"
                },
                "throws" : [
                    "UnknownXferID",
                    "OriginalTooOld",
                    "OriginalMismatch"
                ]
            }
        }
    }

`}Iface`

### 3.2.2. Payout interface

This interface is not related to sales. Funds are transfered from merchant
to client as salary, compenstation, win or any other sort of income.

`Iface{`

    {
        "iface" : "futoin.psp.payout",
        "version" : "{ver}",
        "ftn3rev" : "1.8",
        "imports" : [
            "futoin.psp.types:{ver}"
        ],
        "funcs" : {
        }
    }

`}Iface`

### 3.2.3. Reconciliation interface

The interface is optional and used only for error checking purposes.

`Iface{`

    {
        "iface" : "futoin.psp.reconciliation",
        "version" : "{ver}",
        "ftn3rev" : "1.8",
        "imports" : [
            "futoin.psp.types:{ver}"
        ],
        "funcs" : {
        }
    }

`}Iface`

### 3.2.4. Invoicing interface

Interface to set electronic invoices. It may operate without related
sales interface.

`Iface{`

    {
        "iface" : "futoin.psp.invoice",
        "version" : "{ver}",
        "ftn3rev" : "1.8",
        "imports" : [
            "futoin.psp.types:{ver}"
        ],
        "funcs" : {
        }
    }

`}Iface`

### 3.2.5. Billing interface

Setup recurring payment plan in scope of initial sale and re-use token for later sales.
Important part are terms & conditions to be provided and saved in PSP for dispute resolution
as recurring payments must be processed without client's confirmation.

`Iface{`

    {
        "iface" : "futoin.psp.billing",
        "version" : "{ver}",
        "ftn3rev" : "1.8",
        "imports" : [
            "futoin.psp.types:{ver}"
        ],
        "types" : {
            "TermsAndConditions" : {
                "type" : "array",
                "elemtype" : "string"
            }
        },
        "funcs" : {
            "methods" : {
                "params" : {
                    "currency" : "CurrencyCode"
                },
                "result" : "MethodInfoList",
                "throws" : [
                    "UnknownCurrency"
                ]
            },
            "sale" : {
                "params" : {
                    "method" : "MethodAlias",
                    "ext_id" : "XferExtID",
                    "currency" : "CurrencyCode",
                    "amount" : "Amount",
                    "tc" : "TermsAndConditions",
                    "invoice" : {
                        "type" : "InvoiceID",
                        "default" : null
                    }
                },
                "result" : {
                    "id" : "XferID",
                    "url" : "RedirectURL"
                },
                "throws" : [
                    "UnknownCurrency",
                    "UnknownMethod",
                    "UnknownInvoice",
                    "LimitRejected",
                    "UnacceptableTC"
                ]
            },
            "status" : {
                "params" : {
                    "id" : "XferID"
                },
                "result" : {
                    "method" : "MethodAlias",
                    "ext_id" : "XferExtID",
                    "currency" : "CurrencyCode",
                    "amount" : "Amount",
                    "info" : "SaleResult",
                    "token" : "PaymentToken"
                },
                "throws" : [
                    "UnknownXferID",
                    "OriginalTooOld",
                    "OriginalMismatch"
                ]
            },
            "tokenSale" : {
                "params" : {
                    "token" : "PaymentToken",
                    "currency" : "CurrencyCode",
                    "amount" : "Amount",
                    "invoice" : {
                        "type" : "InvoiceID",
                        "default" : null
                    }
                },
                "result" : {
                    "id" : "XferID",
                    "info" : "SaleResult"
                },
                "throws" : [
                    "LimitRejected",
                    "UnknownToken"
                ]
            }
        }
    }

`}Iface`

## 3.4. Management interface

TBD.


=END OF SPEC=
