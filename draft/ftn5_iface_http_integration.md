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

1. The default integration is based on single end-point URL, which
    accepts HTTP POST requests in plain JSON format and responses in plain
    JSON format.
2. Another integration type is when FutoIn interface, its version and
    function name are placed into URL's path and all parameters are placed
    in GET query
3. A special case of large [binary/text] object upload is combination of
    #2 made with HTTP POST. Call information is coded in URL, but large
    data is passed through POST as is.
4. A special case of large [binary/text] object download is when there
    are no result parameters. Instead, large object is sent as body
    of HTTP response
5. Multiple large objects can be uploaded in multipart format, when
    FutoIn interfaces, its version and function name are coded in URL's
    path, but all parameters are sent as HTML form fields.

