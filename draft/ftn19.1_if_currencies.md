<pre>
FTN19.1: FutoIn Interface - Transaction Engine - Currencies
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

# 2. Concept (Currencies)

## 2.1. Codes

There are known internationally accepted currencies with standardized codes, but that
does not cover widely known, but "unofficial" currencies. It's possible to have various
other virtual or closed loop currencies. Therefore, there must be a clear distinction
of currency code "sets". In current implementation, currency code is prefixed with the
following:

* "I:" - for ISO 4217 fiat currency codes of International Organization for Standardization
* "C:" - for so-called cryptocurrencies with de-facto code conventions
* "K:" - for currencies of Confederation of Reasonable Legal Freedom
* "L:" - for closed loop internal currencies or other type of credits (e.g. game minutes)

It should be possible to disable unused or undesired currencies even if those were previously
registered and/or used for accounts and transactions.

## 2.2. Units

Each currency must have a minimal unit in decimal notation. All currency operations must
always have exact number of decimal places after dot in amounts used in interface. However,
internal database representation may use types without decimal places after dot based on
minimal unit per currency.

## 2.3. Exchange rates

Currency exchange rates are dynamic. Therefore, transaction engine must manage current
exchange rate and full history of changes, if applicable. However, each transaction must
contain used rate regardless of data available elsewhere.

It's assumed that exchange rates are constantly updated from authoritative source.

Exchange rate must be set with up to four extra decimal places after dot.

## 2.4. Base currency

Each currency may have own authoritative source of exchange rates. It may happen that
the same currency pair may have different rates based on authoritative source.

Due to legislation and other means, all conversion operations should specify the base
currency. Only associated authoritative source exchange rate must be used in such operation.

## 2.5. Buy/Sell margin & rounding

Due to imposed risks and rounding errors, the transaction engine operator may need to specify
different rates for conversion to and from base currency. The system should hold a spot rate
and a margin rate to be added to/subtracted from the spot rate.

Relative spread calculations to be done externally before spot & margin rate is set.

Rounding must be done in favour of transaction engine operator.

## 2.6. Events

* `CURRENCY` - update of existing currency
* `CURRENCY_NEW` - new currency
* `EXRATE` - change of existing exchange rate
* `EXRATE_NEW` - new pair of exchange rate

# 3. Interface (Currencies)

Currency-related services are assumed to be a separate module. In some cases,
there can be a single centralized service from which other instances sync. Therefore
there is a strict separation between management and information retrieval.

## 3.1. Types

Common types in scope for currency processing.

`Iface{`

        {
            "iface" : "futoin.currency.types",
            "version" : "{ver}",
            "ftn3rev" : "1.7",
            "types" : {
                "CurrencyCode" : {
                    "type" : "string",
                    "regex" : "^((I:[A-Z]{3})|([CKL]:[A-Za-z0-9*.-_]{1,16}))$",
                    "desc" : "T:Code, see the spec"
                },
                "DecimalPlaces": {
                    "type" : "integer",
                    "min" : 0,
                    "max" : 39
                },
                "CurrencyName" : {
                    "type" : "string",
                    "minlen" : 1,
                    "maxlen" : 64
                },
                "CurrencySymbol" : {
                    "type" : "string",
                    "minlen" : 1,
                    "maxlen" : 18
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
                    "elemtype" : "Currency",
                    "maxlen" : 1000
                },
                "ExRate" : {
                    "type" : "string",
                    "regex" : "^[0-9]{1,12}(\\.[0-9]{1,12})?$"
                }
            }
        }

`}Iface`

## 3.2. Management

Currency management API.

`Iface{`

        {
            "iface" : "futoin.currency.manage",
            "version" : "{ver}",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.currency.types:{ver}"
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

## 3.3. Information

Currency information API.

`Iface{`

        {
            "iface" : "futoin.currency.info",
            "version" : "{ver}",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0",
                "futoin.currency.types:{ver}"
            ],
            "types" : {
                "ListOffset" : {
                    "type" : "integer",
                    "min" : 0
                }
            },
            "funcs" : {
                "listCurrencies" : {
                    "params" : {
                        "from" : {
                            "type" : "ListOffset",
                            "default" : 0
                        },
                        "only_enabled" : {
                            "type" : "boolean",
                            "default" : false
                        }
                    },
                    "result" : "CurrencyList"
                },
                "getCurrency" : {
                    "params" : {
                        "code" : "CurrencyCode"
                    },
                    "result" : "Currency",
                    "throws" : [
                        "UnknownCurrency"
                    ]
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

=END OF SPEC=
