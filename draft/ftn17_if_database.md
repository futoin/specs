<pre>
FTN17: FutoIn Interface - Database
Version: 1.0DV
Date: 2017-08-03
Copyright: 2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.0 - 2017-08-03
    - Initial spec

# 1. Intro

Database interface is fundamental part of almost any technology stack.

# 2. Concept

Interface is split into several levels which are combined in inheritance chain.

Fundamental difference from traditional interfaces is lack of large
result set support, cursors and explicit transaction control. This is
done by intention to forbid undesired database operation patterns.

## 2.1. Level 1

The very basic level for query execution with minimal safety requirements.

## 2.2. Level 2

Transaction execution abstraction with "single call" pattern.

The overall idea is to execute a list of statements on DB side in single transaction
one-by-one. After each xfer, trivial validation is done like amount of affected rows
or count of rows in result. This allows creating complex intermediate checks in
native DB query. Such pattern avoids blocking on usually expensive DB connection
and forces to execute transaction with no client-side delays. Also, proper release
of connection to DB connection pool is ensured.

If at any step an error occurs then whole transaction is rolled back.

*Note: internally, it's assumed that there is a limited number of simultaneous
DB connection allowed which are managed in connection pool for performance reasons,
but such details are absolutely hidden from clients.*

## 2.3. Level 3

Database metadata and ORM-like abstraction.

# 3. Interfaces

## 3.1. Level 1 - query interface


`Iface{`

        {
            "iface" : "futoin.db.l1",
            "version" : "1.0",
            "ftn3rev" : "1.6",
            "imports" : [
                "futoin.ping:1.0"
            ],
            "types" : {
                "Query" : {
                    "type" : "string",
                    "minlen" : 1,
                    "maxlen" : 10000
                },
                "Row" : "array",
                "Rows" : {
                    "type" : "array",
                    "elemtype" : "Row",
                    "maxlen" : 1000
                },
                "Fields" : {
                    "type" : "array",
                    "elemtype" : "string",
                    "desc" : "List of field named in order of related Row"
                }
            },
            "funcs" : {
                "query" : {
                    "params" : {
                        "q" : "Query"
                    },
                    "result" : {
                        "rows" : "Rows",
                        "fields" : "Fields",
                        "affected" : "integer"
                    },
                    "throws" : [
                        "InvalidQuery",
                        "Duplicate",
                        "OtherExecError",
                        "LimitTooHigh"
                    ]
                }
            }
        }

`}Iface`

### 3.1.1. Native interface extension

* Extends "futoin.db.l1"
* Functions:
    * QueryBuilder queryBuilder(type, entity)
        * *type* - DELETE, INSERT, SELECT, UPDATE
        * *entity* - table or view to use
    * QueryBuilder delete(entity)
        * calls queryBuilder()
    * QueryBuilder insert(entity)
        * calls queryBuilder()
    * QueryBuilder select(entity)
        * calls queryBuilder()
    * QueryBuilder update(entity)
        * calls queryBuilder()
    * void call(as, name, Array arguments=[])
        * *name* - stored procedure name
        * *arguments* - list of positional arguments to pass
    * void raw(as, String q, Map params={})
* Class QueryBuilder
    * QueryBuilder clone()
        * create copy of builder
    * QueryBuilder get(fields, escape_field=true)
        * *fields* - field name, array of fields names or map of field-expresion pairs
        * *escape_field* - escape filed names, if true
    * QueryBuilder set(field, value, escape_value=true, escape_field=true)
        * *field* - string
        * *value* - arbitrary value
        * *escape_field* - escape filed names, if true
        * *escape_value* - escape value, if true
    * QueryBuilder setMany(Map fieldValueMap, escape_value=true, escape_field=true)
        * calls set() for each pair of *fieldValueMap*
    * QueryBuilder where(Map conditions, escape_value=true, escape_field=true)
        * *conditions* - pairs of field-value conditions
            * field name may include operator in the end
        * *escape_field* - escape filed names, if true
        * *escape_value* - escape value, if true
    * QueryBuilder having(Map conditions, escape_value=true, escape_field=true)
        * *conditions* - pairs of field-value conditions
            * field name may include operator in the end
        * *escape_field* - escape filed names, if true
        * *escape_value* - escape value, if true    * QueryBuilder group(fields, escape_field=true)
    * QueryBuilder order(Map fields, Boolean escape_field=true)
        * *conditions* - pairs of field-direction, direction in ASC, DESC
        * *escape_field* - escape filed names, if true
    * QueryBuilder limit([Integer start,] Integer count)
    * void execute(AsyncSteps as, Boolean unsafe=false)
        * creates query string and calls query()
        * *unsafe* - fail on DML query without conditions, if true
    * void executeAssoc(AsyncSteps as, Boolean unsafe=false)
        * Same as execute(), but process response and passes
            array of maps and amount of affected rows instead.
            

### 3.1.2. Native executor extension

* Functions:
    * void setup(host, port, user, password, database, conn_limit[, options])
        * *host* - native DB interface host address
        * *port* - native DB interface port
        * *user* - database user
        * *password* - database password
        * *conn_limit* - maximum limit of simultaneous connections
        * *options* - database-specific options

## 3.2. Level 2 - transaction interface

`Iface{`

        {
            "iface" : "futoin.db.l2",
            "version" : "1.0",
            "ftn3rev" : "1.6",
            "inherit" : "futoin.db.l1:1.0",
            "types" : {
                "IntOrBool" : ["integer", "boolean"],
                "XferQuery" : {
                    "type" : "map",
                    "fields" : {
                        "q" : "Query",
                        "affected" : {
                            "type" : "IntOrBool",
                            "optional" : true,
                            "desc" : "Require changed row count: specific or > 0, if true"
                        },
                        "selected" : {
                            "type" : "IntOrBool",
                            "optional" : true,
                            "desc" : "Require selected row count: specific or > 0, if true"
                        },
                        "return" : {
                            "type" : "boolean",
                            "optional" : true,
                            "desc" : "Return result of the statement"
                        }
                    }                    
                },
                "XferQueryList" : {
                    "type" : "array",
                    "elemtype" : "XferQuery",
                    "minlen" : 1,
                    "maxlen" : 100
                },
                "XferResult" : {
                    "type" : "map",
                    "fields" : {
                        "rows" : "Rows",
                        "fields" : "Fields",
                        "affected" : "integer"
                    }
                },
                "XferResultList" : {
                    "type" : "array",
                    "elemtype" : "XferResult",
                    "minlen" : 0,
                    "maxlen" : 100
                },
                "IsolationLevel" : {
                    "type" : "enum",
                    "items" : ["RU", "RC", "RR", "SRL"],
                    "desc" : "Refers to standard ISO isolation levels"
                }
            },
            "funcs" : {
                "xfer" : {
                    "params" : {
                        "ql" : "XferQuery",
                        "isol" : "IsolationLevel"
                    },
                    "result" : {
                        "results" : "XferResultList"
                    },
                    "throws" : [
                        "InvalidQuery",
                        "Duplicate",
                        "OtherExecError",
                        "LimitTooHigh"
                    ]

                }            
            }
        }

`}Iface`

### 3.2.1. Native interface extension

* Extends "futoin.db.l2"
* Functions:
    * XferBuilder xferBuilder(IsolationLevel isol="RC")
* Map QueryOptions:
    * *Integer|Boolean affected* - exact number or true for >0
    * *Integer|Boolean selected* - exact number or true for >0
    * *Boolean return* - mark query which result must be returned
* Class XferBuilder:
    * XferBuilder clone()
    * XferQueryBuilder delete(String entity, QueryOptions query_options)
    * XferQueryBuilder insert(String entity, QueryOptions query_options)
    * XferQueryBuilder update(String entity, QueryOptions query_options)
    * XferQueryBuilder select(String entity, QueryOptions query_options)
    * void call(String name, Array arguments=[], QueryOptions query_options)
    * void raw(String q, Map params={}, query_options)
    * void execute(AsyncSteps as, Boolean unsafe=false)
* Class XferQueryBuilder extends QueryBuilder
    * void execute(AsyncSteps as, Boolean unsafe=false) - must unconditionally throw InternalError
    


## 3.3. Level 3 - TBD

To be defined in later versions.

=END OF SPEC=

