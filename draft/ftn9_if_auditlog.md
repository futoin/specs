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
                        },
                        "ts" : {
                            "type" : "string",
                            "desc" : "Original timestamp in YYYYMMDDhhmmss.frac format"
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
                        "ts" : {
                            "type" : "string",
                            "desc" : "Original timestamp in YYYYMMDDhhmmss.frac format"
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
* Three type of functions
    * lvl( msg ) - shortcut for msg( lvl, msg ) - preffered way for languages with easy string formatting
    * lvl*f*( tpl, args ) - printf() or similar style
    * lvl*s*() - language/platform-specific stream object
* Functions:
    * msgf( lvl, tpl, args ) / msgs( lvl ) - formatting enabled msg functions
    * debug( msg ) / debugf( tpl, args ) / debugs() - equal to msg/msgf/msgs with "debug" lvl
    * info( msg ) / infof( tpl, args ) / infos() - equal to msg/msgf/msgs with "info" lvl
    * warn( msg ) / warnf( tpl, args ) / warns() - equal to msg/msgf/msgs with "warn" lvl
    * error( msg ) / errorf( tpl, args ) / errors() - equal to msg/msgf/msgs with "warn" lvl
    * security( msg ) / securityf( tpl, args ) / securitys() - equal to msg/msgf/msgs with "security" lvl
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

