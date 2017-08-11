<pre>
FTN17: FutoIn Interface - Database
Version: 1.0DV
Date: 2017-08-12
Copyright: 2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.0 - 2017-08-12 - Andrey Galkin
    - Initial spec
* DV - 2017-08-12 - Andrey Galkin
    - Added L1.getFlavour()
    - Added QueryBuilder.join() and sub-query support
    - Removed explicit escape control
    - Added notes about client design
* DV - 2017-08-03 - Andrey Galkin
    - Initial draft

# 1. Intro

Database interface is fundamental part of almost any technology stack.
The primary focus is interface for classical Relational Database Systems.

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

Database metadata and ORM-like abstraction. TBD.

## 2.4. Client-service design

For cross-operation support, client side should be as much neutral as possible and try
to use QueryBuilder interface which should auto-detect actual database type. QueryBuilder
is responsible to consistent behavior across databases. The same applies for XferBUilder
in Level 2.

Client application should be able to run raw queries depending on L1.getType() result.

## 2.5. QueryBuilder security & escapes

QueryBuilder must enforce auto-escape of all values. Identifiers must be checked for valid
[fully qualified] format to prevent possible injection attacks.

## 2.6. QueryBuilder conditions

Conditions can be set as:
1. string - must a be a plain expression used as-is:
2. map:
    - "field.name" => "value" or "field.name OP" pairs
    - value is auto-escaped
3. array - special cases for building complex conditions as tree
    - Optional "AND" (default) or "OR" string in first element indicate join type
    - any following element is recursive of these rules: string, map or another array
    
Multiple conditions and/or repeated calls assune "AND" join.


Simple Example:
```pseudo
    select('TableName')
        .where('SomeField IS NULL')
        .where({
            'OtherField' => $val,
            'AnotherField <' => $threshold,
        })
```

Complex Example:
```pseudo
    select('TableName')
        .where([
            "FieldOne IS NULL",
            [
                "OR",
                "FieldTwo <" => 2,
                "FieldThee IN" => [1, 2, 3], 
            ],
            {
                "FieldFour" => $val,
            }
        ])
```

## 2.7. QueryBuilder condition operators

For map conditions optional match operators are supported.
The following standard ops are assumed:

* `=` - equal
* `<>` - not equal
* `>` - greater
* `>=` - greater or equal
* `<` - less
* `<=` - less or equal
* `IN` - in array or subquery (assumed)
* `NOT IN` - not in array or subquery (assumed)
* `BETWEEN` - two value tuple is assumed for inclusive range match
* `NOT BETWEEN` - two value tuple is assumed for inverted inclusive range match
* `LIKE` - LIKE match
* `NOT LIKE` - NOT LIKE match
* other ops may be implicitely supported

*Note: `EXISTS`, `ANY` and `SOME` are not supported by design due to known performance issues in many database implementations.*

# 3. Interfaces

## 3.1. Level 1 - query interface


`Iface{`

        {
            "iface" : "futoin.db.l1",
            "version" : "1.0",
            "ftn3rev" : "1.7",
            "imports" : [
                "futoin.ping:1.0"
            ],
            "types" : {
                "Query" : {
                    "type" : "string",
                    "minlen" : 1,
                    "maxlen" : 10000
                },
                "Identifier" : {
                    "type" : "string",
                    "maxlen" : 256
                },
                "Row" : "array",
                "Rows" : {
                    "type" : "array",
                    "elemtype" : "Row",
                    "maxlen" : 1000
                },
                "Field" : {
                    "type" : "string",
                    "maxlen" : 256
                },
                "Fields" : {
                    "type" : "array",
                    "elemtype" : "Field",
                    "desc" : "List of field named in order of related Row"
                },
                "Flavour" : {
                    "type" : "Identifier",
                    "desc" : "Actual actual database driver type"
                },
                "QueryResult" : {
                    "type" : "map",
                    "fields" : {
                        "rows" : "Rows",
                        "fields" : "Fields",
                        "affected" : "integer"
                    }
                }
            },
            "funcs" : {
                "query" : {
                    "params" : {
                        "q" : "Query"
                    },
                    "result" : "QueryResult",
                    "throws" : [
                        "InvalidQuery",
                        "Duplicate",
                        "OtherExecError",
                        "LimitTooHigh"
                    ]
                },
                "callStored" : {
                    "params" : {
                        "name" : "Identifier",
                        "args" : "Row"
                    },
                    "result" : "QueryResult",
                    "throws" : [
                        "InvalidQuery",
                        "Duplicate",
                        "OtherExecError",
                        "LimitTooHigh"
                    ]
                },
                "getFlavour" : {
                    "result" : "Flavour"
                }
            }
        }

`}Iface`

### 3.1.1. Native interface extension

* Extends "futoin.db.l1"
* Functions:
    * QueryBuilder queryBuilder(type, entity)
        * *type* - DELETE, INSERT, SELECT, UPDATE
        * *entity* -
            - table or view name
            - QueryBuilder object to use as sub-query
            - tuple of [entity, alias]
            - null - special case without SQL "FROM"
        * *alias* - alias to use for referencing
    * QueryBuilder delete(entity)
        * calls queryBuilder()
    * QueryBuilder insert(entity)
        * calls queryBuilder()
    * QueryBuilder select(entity)
        * calls queryBuilder()
    * QueryBuilder update(entity)
        * calls queryBuilder()
    * void paramQuery(as, String q, Map params={})
        * substiatue ":name" placeholders in q with
            values from params
        * do normal raw query()
    * void associateResult(as_result)
        * process efficiently packed result to get array
            of associative Map
* Class QueryBuilder:
    * static void addDriver(type, module)
        * *type* - driver name to match L1.getType()
        * *module* - module name or actual instance
        * add/override driver support
    * QueryBuilder clone()
        * create copy of builder
    * String escape(value)
        * *value* any value, including QueryBuilder instance
    * String identifier(name)
        * *name* - string to escape as identifier
    * Expression expr(expr)
        * *expr* - raw expression
        * wrap raw expression to avoid escaping as value
    * Expression param(name)
        * *name* - parameter name
        * wrapped placeholder for prepared statement
    * QueryBuilder get(field[, value])
        * *fields* - field name, array of fields names or map of field-expresion pairs
        * *value* - arbitrary value, expression or QueryBuilder sub-query
    * QueryBuilder get(List field)
        * list of field names to select
    * QueryBuilder get(Map field)
        * field name => expression pairs to select
    * QueryBuilder set(field[, value])
        * *field* - string
        * *value* - arbitrary value, expression or QueryBuilder sub-query
    * QueryBuilder set(Map fieldValueMap)
        * calls set() for each pair of *fieldValueMap*
    * QueryBuilder set(QueryBuilder select_query)
        * special for "INSERT-SELECT" cases
        * *select_query* field names are used for target field names
    * QueryBuilder where(conditions)
        * *conditions* - see concept
    * QueryBuilder where(field, value)
        * handy shorcut for where({ field: value })
    * QueryBuilder having(conditions)
        * *conditions* - see concept
    * QueryBuilder having(field, value)
        * handy shorcut for having({ field: value })
    * QueryBuilder group(field_expr)
    * QueryBuilder order(field_expr, Boolean ascending=true)
        * *fields* - pairs of field-direction, direction in ASC, DESC
    * QueryBuilder limit(Integer count, Integer offset)
    * QueryBuilder join(join_type, entity, conditions)
        * *join_type* - INNER, LEFT
        * *entity* - see L1.queryBuilder()
        * *conditions* - see concept
    * QueryBuilder innerJoin(entity, conditions)
    * QueryBuilder leftJoin(entity, conditions)
    * void execute(AsyncSteps as, Boolean unsafe_dml=false)
        * creates query string and calls query()
        * *unsafe_dml* - fail on DML query without conditions, if true
    * void executeAssoc(AsyncSteps as, Boolean unsafe_dml=false)
        * Same as execute(), but process response and passes
            array of maps and amount of affected rows instead.
    * Prepared prepare(Boolean unsafe_dml=false)
        * Return an interface for efficient execution of built query
            multiple times
* class Prepared:
    * void execute(AsyncSteps as, L1Face iface, params=null)
        * *params* - name => value pairs for substitution
        * *iface* - iface to run against
        * executes already built query with optional parameters
    * void executeAssoc(AsyncSteps as, L1Face iface, params=null)
        * the same as execute(), but return associative result
            

### 3.1.2. Native service extension

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
            "ftn3rev" : "1.7",
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
                        "seq" : "integer",
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
                        "ql" : "XferQueryList",
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
    * XferBuilder newXfer(IsolationLevel isol="RC")
* Map QueryOptions:
    * *Integer|Boolean affected* - exact number or true for >0
    * *Integer|Boolean selected* - exact number or true for >0
    * *Boolean return* - mark query which result must be returned (default true for last)
* Class XferBuilder:
    * XferBuilder clone()
    * XferQueryBuilder delete(String entity, QueryOptions query_options)
    * XferQueryBuilder insert(String entity, QueryOptions query_options)
    * XferQueryBuilder update(String entity, QueryOptions query_options)
    * XferQueryBuilder select(String entity, QueryOptions query_options)
    * void call(String name, Array arguments=[], QueryOptions query_options={})
    * void raw(String q, Map params={}, QueryOptions query_options={})
    * void execute(AsyncSteps as, Boolean unsafe_dml=false)
        * build all queries and execute in single transaction
        * *unsafe_dml* - fail on DML query without conditions, if true
    * void executeAssoc(AsyncSteps as, Boolean unsafe_dml=false)
        * Same as execute(), but process response and passes
            array of maps and amount of affected rows instead.
    * Prepared prepare(Boolean unsafe_dml=false)
        * Return an interface for efficient execution of built transaction
            multiple times
* Class XferQueryBuilder extends QueryBuilder
    * void execute(AsyncSteps as, Boolean unsafe_dml=false)
        - must unconditionally throw InternalError
    * QueryBuilder clone()
        - must unconditionally throw InternalError
    


## 3.3. Level 3 - TBD

To be defined in later versions.

=END OF SPEC=

