<pre>
FTN5: FutoIn HTTP integration
Version: 1.2
Date: 2015-02-22
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.2 - 2015-02-22
    * Clarified query string parameter coding
* v1.1 - 2014-12-21
    * Simplified error response when raw result is expected
* v1.0 - 2014-10-11

# 1. Intro

Well, as mentioned in other specs, FutoIn project was born by influence
of Web technologies in scope of Enterprise solutions. So, HTTP is fundamental
communication channel (besides WebSockets).

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
4. A special case of large [binary/text] object download is when there
    are no result parameters. Instead, large object is sent as body
    of HTTP response. Can be combined with any other use case.

Note: By definition of HTTP, only uni-directional message exchange is supported
with no multiplexing on communication channel level.


# 2. Use case auto-detection

* If request URI exactly matches Executor's end-point URI:rawresult
    * case if POST
        * *Use Case #1*
        * read request body as JSON FutoIn request
        * process (see below)
    * else fail
* else if sub-path after Executor's end-point URI, matches "interfaces/version/function[/sec]" format:
    * deduce interface, its version and function name from sub-path
    * if exists, extract 'sec' as fourth component of the sub-path
    * if provided, extract 'sec' from HTTP 'Basic Auth'
    * if query string is present
        * read parameters from query string
        * case if GET
            * *Use Case #2*
            * process (see below)
        * case if POST
            * *Use Case #3*
            * process (see below)
            * allow rawInput()
                * Note: multi-part must not be parsed by Executor implementation
        * else fail
    * else fail
* else fail

*Note: Executor must accept URI with or without trailing slash in path*

# 2.1. Request processing steps

* process request in Executor
* on success, write response body as (one of):
    * if raw data response expected (by spec)
        * arbitrary large object (*Use Case #4*)
        * Note: there is no point in re-defining HTTP conditional requests (If-*/Etag/etc).
            in scope of this spec.
    * else
        * JSON FutoIn response (even with empty result variables)
* on error,
    * JSON FutoIn response (even with raw result is expected)

# 2.2. MIME-type

FutoIn request and response messages must have *application/futoin+json* MIME-type. This type must be used
ONLY for actual messages in Invoker-Executor dialog. In any other case, *application/json* should be used
for messages.

Implementation must refuse to parse JSON as request or response message, if corresponding HTTP
headers do not have correct MIME-type.

Invoker should assume *Use Case #4*, if response MIME-Type is not *application/futoin+json*.


# 3. Misc. technical details

URI is assumed as defined in its [RFC3986][] or any later version.

*Note: Executor must behave equally with or without trailing slash in URI path part.*

## 3.1. Executor's end-point sub-path format

Generic format: "{end-point-URI}/{interface}/{version}/{function_name}[/sec_field]"

*Example:*
    "https://api.example.com/futoin/**some.interface.name/1.0/someFunc**"
    "https://api.example.com/futoin/**some.interface.name/1.0/someFunc/sec_field**"


## 3.2. URI Query string format

Query string starts with question mark "?". Parameters are separated with ampersand sign "&".

*Example: "https://api.example.com/futoin/some.interface.name/1.0/someFunc?**param1=val1&param2=val2**"*

## 3.3. Objects and arrays in query string and multi-part form data

There are the following rules for query string coding:

1. String values are added as is
2. All others value types are respresented as raw JSON

## 3.4. {empty}

Reserved.

## 3.5. File upload

By fundamental principles of FutoIn, there should be a special File Upload service
implemented once (for both long storage and temporary files). In general, no 
other service should accept file uploads. Instead, special file operation API
should exist. 

File uploads have a serious risk of security exploits and denial of service. It
should not be implemented in any arbitrary service.

Client code should first request file upload token and only then start upload
identifying each related request with this token, besides general security framework.

### 3.5.1 Raw HTML form file upload

HTTP multipart/form-data upload must not be handled by Executor. Instead, FileUpload
service should handle one.
Still, it is not recommended to upload more than one file at a time to save bandwidth
or error situations.

### 3.5.2. Advanced file upload

To minimize effect of temporary upload errors, FileUpload service should support
incremental file upload using combination of Use Case #2 and #3.

* Maximal chunk size should not be limited by Service side
* Chunk size must be dynamically adjusted by client to be uploaded within 3 seconds
    based on results of previously uploaded chunk(s).

Modern web browser JavaScript should support file reading API. Client side should
limit buffer size to a reasonable size until direct streaming from file is not supported
by XHR.


## 3.6. INFO_CHANNEL_CONTEXT field of Executor.RequestInfo.info()

It should be an object for on-demand access of HTTP request/response details.

HTTPChannelContext inherits from ChannelContext

* map getRequestHeaders()
* void setResponseHeader( name, value, override=true )
* void setStatusCode( http_code )
* string getCookie( name )
* void setCookie( name, value, options )
    * options.http_only = true 
    * options.secure = INFO_SECURE_CHANNEL
    * options.domain = null
    * options.path = null
    * options.expires = null (date object or string)
    * options.max_age = null (interval object or string)




[RFC3986]: http://www.ietf.org/rfc/rfc3986.txt "Uniform Resource Identifier (URI): Generic Syntax"

=END OF SPEC=
