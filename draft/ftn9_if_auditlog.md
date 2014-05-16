<pre>
FTN9: FutoIn Interface - AuditLog
Version: 0.1
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# 1. Intro

It is assumed that there is a central sink for all audit log
messages in the system. There should be no individual logging
mechanism per component.

There should be universal Invoker and Executor API wrapper interface
with handy shortcuts and formatting.

# 2. Interface schema

`Iface{`

        {
            "iface" : "futoin.log",
            "version" : "0.1",
            "funcs" : {
                "msg" : {
                    "params" : {
                        "lvl" : {
                            "type" : "string",
                            "desc" : "Severity level: debug|info|warn|error|security"
                        },
                        "txt" : {
                            "type" : "string",
                            "desc" : "Text message, may include new lines"
                        }
                    },
                    "desc" : "Trivial log message"
                },
                "hexdump" : {
                    "params" : {
                        "lvl" : {
                            "type" : "string",
                            "desc" : "Severity level: debug|info|warn|error|security"
                        },
                        "txt" : {
                            "type" : "string",
                            "desc" : "Text message, may include new lines"
                        },
                        "data" : {
                            "type" : "string",
                            "desc" : "Base64 encoded binary data"
                        }
                    },
                    "desc" : "Trivial log message"
                }
            },
            "requires" : [
                "SecureChannel"
            ],
            "desc" : "Audit Log interface"
        }

`}Iface`

# 3. Extended API interface

The raw FutoIn interface is not very handy for writing code and additional
feateres are desired.

* Extend "futoin.log"
* Two type of functions
    * func*f*( tpl, args ) - printf() or similar style
    * func*s*() - language/platform-specific stream object
* Functions:
    * msgf( lvl, tpl, args ) / msgs( lvl ) - formatting enabled msg functions
    * debugf( tpl, args ) / debugs() - equal to msgf/msgs with "debug" lvl
    * infof( tpl, args ) / infos() - equal to msgf/msgs with "info" lvl
    * warnf( tpl, args ) / warns() - equal to msgf/msgs with "warn" lvl
    * errorf( tpl, args ) / errors() - equal to msgf/msgs with "warn" lvl
* Enumeration:
    * LVL_DEBUG
    * LVL_INFO
    * LVL_WARN
    * LVL_ERROR
    * LVL_SECURITY

## 3.1. Example of use


        Without [RAII][] principle (e.g. Java, Python, PHP):
        ...log().infof( "Message %s", str )
        with ...log().infos() as l:
            l.write( "Message " )
            l.write( str )

        With [RAII][] principle (e.g. C++):
        ...log().infof( "Message %s", str );
        ...log().infos() << "Message " << str;

[RAII]: http://en.wikipedia.org/wiki/Resource_Acquisition_Is_Initialization "Resource Acquisition Is Initialization"

