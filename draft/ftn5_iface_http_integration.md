<pre>
FTN3: FutoIn HTTP integration
Version: 0.1
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# 1. Intro

Well, as mentioned in other specs, FutoIn project was born by influence
of Web technologies in scope of Enterprise solutions.

Use cases:

1. The default integration is based on single end-point URI, which
    accepts HTTP POST requests in plain JSON format and responses in plain
    JSON format.
2. Another integration type is when FutoIn interface, its version and
    function name are placed into URI's path and all parameters are placed
    in HTTP GET query
3. A special case of large [binary/text] object upload is combination of
    #2 made with HTTP POST. Call information is coded in URI, but large
    data is passed through POST as is.
4. Multiple large objects can be uploaded in multi-part format, when
    FutoIn interfaces, its version and function name are coded in URI's
    path, but all parameters are sent as HTML form fields in HTTP POST.
5. A special case of large [binary/text] object download is when there
    are no result parameters. Instead, large object is sent as body
    of HTTP response. Can be combined with any other use case.



# 2. Use case auto-detection

* If request URI exactly matches Executor's end-point URI:
    * case if GET
        * *Use Case #1*
        * read request body as JSON FutoIn request
        * process (see below)
    * othewise, fail
* else if sub-path after Executor's end-point URI, matches "interfaces/version/function" format:
    * deduce interface, its version and function name from sub-path
    * if query string is present and 
        * read parameters from query string
        * case if GET
            * *Use Case #2*
            * process (see below)
        * case if POST
            * *Use Case #3*
            * store request body as temporary uploaded file
            * process (see below)
        * otherwise, fail
    * else
        * if multi-part data
            * *Use Case #4*
            * read parameters from form fields
            * store files as temporary uploaded files
            * process (see below)
        * else fail
* else:
    * fail

# 2.1. Request processing steps

* process request in Executor
* write response body as (one of):
    * JSON FutoIn response, if function has parameters
    * arbitrary large object (*Use Case #5*)
    * empty string (even though, there is no result, HTTP requires response)


# 3. Misc. technical details

URI is assumed as defined in its [RFC3986][] or any later version.

*Note: Executor must behave equally with or without trailing slash in URI path part.*

## 3.1. Executor's end-point sub-path format

Generic format: "{end-point-URI}/{interface}/{version}/{function_name}"

*Example: "https://api.example.com/futoin/**some.interface.name/1.0/someFunc**"*


## 3.2. URI Query string format

Query string starts with question mark "?". Parameters are separated with ampersand sign "&".

*Example: "https://api.example.com/futoin/some.interface.name/1.0/someFunc?**param1=val1&param2=val2**"*

## 3.3. Rules for representing objects and arrays in query string and multi-part form data

Note: the specifications uses unreserved by URI [RFC3986][] character classes to avoid extra coding needed.

JSON object is a tree-like structure. Each parent node is marked as object by added 
dot "." as separator right after parent node name.

JSON array is marked by adding plus sign "+" right after parent node name.

The function parameters object type is implicitly assumed and leading "." is forbidden.

Example:

        {
            "tree" : {
                "subtree" : {
                    "node1" : "val1"
                },
                "node2" : "val2",
                "array" : [
                    "item1",
                    {
                        "node3" : "val3"
                    }
                ]
            }
        }

would be coded as:

        tree.subtree.node1=val1
        tree.node2=val2
        tree.array+=item1
        tree.array+.node3=val3


## 3.4. Conflicts in passed parameters

In case if the same request parameter tree node is used in different contexts
(as leaf, as object or as array). Executor must rise InvalidRequest.



[RFC3986]: http://www.ietf.org/rfc/rfc3986.txt "Uniform Resource Identifier (URI): Generic Syntax"
