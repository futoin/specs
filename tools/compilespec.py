#!/usr/bin/python3
#
#
# !!! NOTE: THIS IS ONLY A QUICK DIRTY TOOL - MUST BE REWRITTEN !!!
#
#
#

import json
import markdown
import sys
import os
import codecs
import re
import collections
from jsonschema import validate as schema_validate, Draft4Validator

def die( msg ) :
    sys.stderr.write( msg )
    sys.exit( -1 )

def compilespec( spec_file ) :
    #---
    spec_dir = os.path.dirname( spec_file )
    meta_dir = os.path.join( spec_dir, 'meta' )
    preview_dir = os.path.join( spec_dir, 'preview' )
    html_file = os.path.join( preview_dir, os.path.basename( spec_file ).replace( '.md', '.html' ) )

    #---
    spec_time = os.path.getmtime(spec_file)
    try :
        html_time = os.path.getmtime(html_file)
    except OSError:
        spec_time = 1
        html_time = 0

    if spec_time < html_time :
        print( "- Skipping " + spec_file + "\n" )
        return

    #---
    input_file = codecs.open( spec_file, mode="r", encoding="utf-8" )


    #---
    text = []
    json_text = []
    parsing_iface = False
    parsing_schema = False
    schema_re = re.compile( '^`Schema\\(([a-z0-9\\-_]+)\\){`$' )
    curr_line = 1
    in_header = True
    spec_ver = ''
    end_of_spec_seen = False

    for l in input_file:
        try:
            if in_header :
                pair = l.split( ':', 2 )

                if len( pair ) == 2 :
                    tag, value = pair
                    value = value.strip()

                    if tag == 'Version' :
                        spec_ver = value.replace('DV','')
                    elif tag in ('Copyright','Authors','Date') :
                        pass
                    elif re.match( 'FTN[0-9]+', l ) :
                        pass
                    else :
                        die(str(curr_line) + " Unknown header field")

                if l == '\n' :
                    in_header = False

                    if not spec_ver :
                        die( str(curr_line) + " Missing spec Version" )
                        
            #---
            if end_of_spec_seen and l != '\n':
                die( str(curr_line) + " Text after end of spec" )
                        
            #---
            m = schema_re.match( l )

            if m is not None:
                if parsing_iface or parsing_schema :
                    print( "Current Schema: " + str( parsing_schema ) + "\n" )
                    die( str(curr_line) + ': Unable to parse Schema in scope of another Schema or Iface\n' )

                parsing_schema = m.group(1)
                text.append('<p class="futoin-schema">Schema: ' + parsing_schema + '</p>\n')

            elif l == '`}Schema`\n' :
                schema_obj = json.loads(
                        ''.join( json_text ),
                        object_pairs_hook = lambda pairs: collections.OrderedDict( pairs )
                )
                Draft4Validator.check_schema(schema_obj)
                schema = json.dumps(schema_obj, indent=2, separators=(',', ': ') )

                schema_file = os.path.join( meta_dir, parsing_schema + '-' + spec_ver + '-schema.json' )

                with codecs.open( schema_file,
                                "w",
                                encoding="utf-8",
                                errors="xmlcharrefreplace"
                ) as f:
                    f.write( schema )
                    
                    
                # mjr ver
                spec_major_ver = spec_ver.split('.')
                spec_major_ver = spec_major_ver[0]

                schema_mjr_file = os.path.join( meta_dir, parsing_schema + '-' + spec_major_ver + '-schema.json' )
                try:
                    os.unlink( schema_mjr_file )
                except OSError:
                    pass
                
                os.symlink( os.path.basename( schema_file ), schema_mjr_file )
                    
                # no ver
                schema_file_nover = os.path.join( meta_dir, parsing_schema + '-schema.json' )
                try:
                    os.unlink( schema_file_nover )
                except OSError:
                    pass
                os.symlink( os.path.basename( schema_mjr_file ), schema_file_nover )

                parsing_schema = False
                json_text = []

            elif l == '`Iface{`\n' :
                if parsing_iface or parsing_schema :
                    die( str(curr_line) + ': Unable to parse Iface in scope of Schema or another Iface\n' )

                parsing_iface = True

            elif l == '`}Iface`\n' :
                if not parsing_iface:
                    die( str(curr_line) + ': Unexpected end of Iface' )

                iface = json.loads(
                        ''.join( json_text ),
                        object_pairs_hook = lambda pairs: collections.OrderedDict( pairs )
                )
                iface_name = iface['iface']
                iface["version"] = spec_ver
                
                if 'imports' in iface:
                    iface['imports'] = [ v.replace('{ver}', spec_ver) for v in iface['imports'] ]
                if 'inherit' in iface:
                    iface['inherit'] = iface['inherit'].replace('{ver}', spec_ver)
                
                # validate schema
                schema_file = os.path.join(meta_dir, 'futoin-interface-' + iface['ftn3rev'] + '-schema.json')
                with open(schema_file, 'r') as sf:
                    schema = json.load(sf)
                schema_validate(iface, schema)
                
                # version file
                iface_ver_file = os.path.join( meta_dir, iface_name + '-' + iface['version'] + '-iface.json' )

                with codecs.open( iface_ver_file,
                                "w",
                                encoding="utf-8",
                                errors="xmlcharrefreplace"
                ) as f:
                    f.write( json.dumps( iface, indent=2, separators=(',', ': ') ) )

                # mjr symlink
                iface_major_ver = iface['version'].split('.')
                iface_major_ver = iface_major_ver[0]
                iface_mjr_file = os.path.join( meta_dir, iface_name + '-' + iface_major_ver + '-iface.json' )
                
                try:
                    os.unlink( iface_mjr_file )
                except OSError:
                    pass
                os.symlink( os.path.basename( iface_ver_file ), iface_mjr_file )

                
                # no ver symlink
                iface_file_nover = os.path.join( meta_dir, iface_name + '-iface.json' )
                try:
                    os.unlink( iface_file_nover )
                except OSError:
                    pass
                os.symlink( os.path.basename( iface_mjr_file ), iface_file_nover )

                parsing_iface = False
                json_text = []

            else :
                if l == '=END OF SPEC=\n' :
                    end_of_spec_seen = True
                    
                if parsing_iface or parsing_schema :
                    json_text.append( l )

                l = l.replace( '.md', '.html' )
                text.append( l )

            curr_line += 1
        except Exception as e :
            if len( json_text ) :
                i = 1
                for jl in json_text :
                    sys.stderr.write( "%s: %s"  % ( i, jl ) )
                    i += 1
            die( "At line %s: Exception: %s\n" % ( curr_line, e )  )
            
    #---
    if not end_of_spec_seen:
        die( "Missing '=END OF SPEC=' in %s" % ( spec_file )  )

    #---
    html_ver_file = html_file.replace( '.html', '-' + spec_ver + '.html' )
    
    spec_major_ver = spec_ver.split('.')
    spec_major_ver = spec_major_ver[0]
    html_mjrver_file = html_file.replace( '.html', '-' + spec_major_ver + '.html' )
    
    if False :
        raw_file = codecs.open( html_file + '.raw', "w",
                                encoding="utf-8",
                                errors="xmlcharrefreplace"
        )

        raw_file.write( ''.join( text ) )
        raw_file.close()

    output_file = codecs.open( html_ver_file, "w",
                            encoding="utf-8",
                            errors="xmlcharrefreplace"
    )

    # mjr.mnr symlink
    try :
        os.unlink( html_mjrver_file )
    except OSError:
        pass
    os.symlink( os.path.basename( html_ver_file ), html_mjrver_file )

    # mjr symlink
    try :
        os.unlink( html_file )
    except OSError:
        pass
    os.symlink( os.path.basename( html_mjrver_file ), html_file )

    # update html
    output_file.write( '<!DOCTYPE html>\n' )
    output_file.write( '<html>\n<head>\n' )
    output_file.write( '<title>' + os.path.basename( spec_file ) + '</title>\n' )
    output_file.write( '<link rel="stylesheet" type="text/css" href="../../css/specs.css">\n' )
    output_file.write( '</head><body>\n' )
    output_file.write( '<nav>\n' )
    output_file.write( '<a href="/">' )
    output_file.write( ' <img src="data:image/svg+xml;base64,PHN2ZyBpZD0iTGF5ZXJfMSIgZGF0YS1uYW1lPSJMYXllciAxIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNTAwIDE1MDAiPjxkZWZzPjxzdHlsZT4uY2xzLTF7ZmlsbDojMzExYjkyO30uY2xzLTJ7ZmlsbDojZmZmO308L3N0eWxlPjwvZGVmcz48dGl0bGU+RnV0b0luX2xvZ288L3RpdGxlPjxyZWN0IGNsYXNzPSJjbHMtMSIgd2lkdGg9IjE1MDAiIGhlaWdodD0iMTUwMCIvPjxjaXJjbGUgY2xhc3M9ImNscy0yIiBjeD0iNzUwIiBjeT0iNzUwIiByPSIyMzcuODgiLz48cmVjdCBjbGFzcz0iY2xzLTIiIHg9IjcyNC4yMyIgeT0iMTQ2LjczIiB3aWR0aD0iNTEuNDQiIGhlaWdodD0iMTIwNi40NiIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMTQ5OS45NiAwLjA1KSByb3RhdGUoOTApIi8+PHJlY3QgY2xhc3M9ImNscy0yIiB4PSI3MjQuMjMiIHk9IjE0Ni43NiIgd2lkdGg9IjUxLjQ0IiBoZWlnaHQ9IjEyMDYuNCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMTQ5OS45NSAxNDk5Ljk2KSByb3RhdGUoMTgwKSIvPjxyZWN0IGNsYXNzPSJjbHMtMiIgeD0iODg1Ljc5IiB5PSIzODcuNTgiIHdpZHRoPSIyOS4zOSIgaGVpZ2h0PSI0MjQuOTEiIHRyYW5zZm9ybT0idHJhbnNsYXRlKDExMTIuOTggMTY2MS4xKSByb3RhdGUoLTEzNSkiLz48Y2lyY2xlIGNsYXNzPSJjbHMtMiIgY3g9IjEzNTMuMiIgY3k9Ijc1MCIgcj0iOTEuODUiLz48Y2lyY2xlIGNsYXNzPSJjbHMtMiIgY3g9IjE0Ni44IiBjeT0iNzUwIiByPSI5MS44NSIvPjxjaXJjbGUgY2xhc3M9ImNscy0yIiBjeD0iNzUwIiBjeT0iMTQ2LjgiIHI9IjkxLjg1Ii8+PGNpcmNsZSBjbGFzcz0iY2xzLTIiIGN4PSI3NTAiIGN5PSIxMzUzLjIiIHI9IjkxLjg1Ii8+PGNpcmNsZSBjbGFzcz0iY2xzLTIiIGN4PSIxMDUzLjA0IiBjeT0iNDQ5LjM5IiByPSI1NS4xMSIvPjxwYXRoIGNsYXNzPSJjbHMtMiIgZD0iTTEwMjkuNDUsNzI0LjI0aDE3N2MzMC40MSwwLDU4LjcyLTEzLjkyLDc4Ljc5LTM2Ljc3LDEzLjM2LTE1LjIxLDM0LjcyLTI5LjM3LDY4LTI5LjM3LDAsMCw0NCwxODUsMCwxODMuNzEtMzMuMTMtLjk0LTU0LjQyLTE0LjkyLTY3Ljc2LTI5Ljc3LTIwLjItMjIuNDktNDguMjQtMzYuMzYtNzguNDctMzYuMzZoLTE3NyIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMC4wNSAwLjA0KSIvPjxwYXRoIGNsYXNzPSJjbHMtMiIgZD0iTTc3NS42OCwxMDI5LjQ2djE3N2MwLDMwLjQxLDEzLjkyLDU4LjcyLDM2Ljc3LDc4Ljc5LDE1LjIxLDEzLjM2LDI5LjM3LDM0LjcyLDI5LjM3LDY4LDAsMC0xODUsNDQtMTgzLjcxLDBDNjU5LDEzMjAsNjczLDEyOTguNzQsNjg3Ljg4LDEyODUuNGMyMi40OS0yMC4yLDM2LjM2LTQ4LjI0LDM2LjM2LTc4LjQ3di0xNzciIHRyYW5zZm9ybT0idHJhbnNsYXRlKDAuMDUgMC4wNCkiLz48cGF0aCBjbGFzcz0iY2xzLTIiIGQ9Ik00NzAuNDUsNzc1LjY5aC0xNzdjLTMwLjQxLDAtNTguNzIsMTMuOTItNzguNzksMzYuNzctMTMuMzYsMTUuMjEtMzQuNzIsMjkuMzctNjgsMjkuMzcsMCwwLTQ0LTE4NSwwLTE4My43MSwzMy4xMywwLjk0LDU0LjQyLDE0LjkyLDY3Ljc2LDI5Ljc3LDIwLjIsMjIuNDksNDguMjQsMzYuMzYsNzguNDcsMzYuMzZINDcwIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgwLjA1IDAuMDQpIi8+PHBhdGggY2xhc3M9ImNscy0yIiBkPSJNNzI0LjIzLDQ3MC40NnYtMTc3YzAtMzAuNDEtMTMuOTItNTguNzItMzYuNzctNzguNzktMTUuMjEtMTMuMzYtMjkuMzctMzQuNzItMjkuMzctNjgsMCwwLDE4NS00NCwxODMuNzEsMC0wLjk0LDMzLjEzLTE0LjkyLDU0LjQyLTI5Ljc3LDY3Ljc2LTIyLjQ5LDIwLjItMzYuMzYsNDguMjQtMzYuMzYsNzguNDdWNDcwIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgwLjA1IDAuMDQpIi8+PHBhdGggY2xhc3M9ImNscy0yIiBkPSJNOTI1LDU1NC42OWw2NC4xOS02NC4xOWEzNC4zNiwzNC4zNiwwLDAsMCw5LjE4LTMxLjQ1Yy0yLjY2LTEyLjY5LTIuMTQtMzAuODUsMTQuMjgtNDcuMjcsMCwwLDk4LjU1LDU4LjA4LDc5LjI3LDc2LjU0LTE4LjYyLDE3LjgzLTM3LjY1LDE4LjE5LTUwLjcsMTUuMTFhMzQuMzksMzQuMzksMCwwLDAtMzIuMzUsOWwtNjMuMTcsNjMuMTciIHRyYW5zZm9ybT0idHJhbnNsYXRlKDAuMDUgMC4wNCkiLz48cmVjdCBjbGFzcz0iY2xzLTIiIHg9IjU4NC43MiIgeT0iNjg3LjQzIiB3aWR0aD0iMjkuMzkiIGhlaWdodD0iNDI0LjkxIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSg4MTEuOTMgLTE2MC4yNSkgcm90YXRlKDQ1KSIvPjxjaXJjbGUgY2xhc3M9ImNscy0yIiBjeD0iNDQ2Ljk2IiBjeT0iMTA1MC42MSIgcj0iNTUuMTEiLz48cGF0aCBjbGFzcz0iY2xzLTIiIGQ9Ik01NzQuODUsOTQ1LjI0bC02NC4xOSw2NC4xOWEzNC4zNiwzNC4zNiwwLDAsMC05LjE4LDMxLjQ1YzIuNjYsMTIuNjksMi4xNCwzMC44NS0xNC4yOCw0Ny4yNywwLDAtOTguNTUtNTguMDgtNzkuMjctNzYuNTQsMTguNjItMTcuODMsMzcuNjUtMTguMTksNTAuNy0xNS4xMWEzNC4zOSwzNC4zOSwwLDAsMCwzMi4zNS05bDYzLjE3LTYzLjE3IiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgwLjA1IDAuMDQpIi8+PHJlY3QgY2xhc3M9ImNscy0yIiB4PSI4ODUuMTgiIHk9IjY4OC4wNCIgd2lkdGg9IjI5LjM5IiBoZWlnaHQ9IjQyNC45MSIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTM3My4xMyA5MDAuMDkpIHJvdGF0ZSgtNDUpIi8+PGNpcmNsZSBjbGFzcz0iY2xzLTIiIGN4PSIxMDUwLjYxIiBjeT0iMTA1My4wNCIgcj0iNTUuMTEiLz48cGF0aCBjbGFzcz0iY2xzLTIiIGQ9Ik05NDUuMjIsOTI1LjA2bDY0LjE5LDY0LjE5YTM0LjM2LDM0LjM2LDAsMCwwLDMxLjQ1LDkuMThjMTIuNjktMi42NiwzMC44NS0yLjE0LDQ3LjI3LDE0LjI4LDAsMC01OC4wOCw5OC41NS03Ni41NCw3OS4yNy0xNy44My0xOC42Mi0xOC4xOS0zNy42NS0xNS4xMS01MC43YTM0LjM5LDM0LjM5LDAsMCwwLTktMzIuMzVsLTYzLjE3LTYzLjE3IiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgwLjA1IDAuMDQpIi8+PHJlY3QgY2xhc3M9ImNscy0yIiB4PSI1ODUuMDYiIHk9IjM4Ny40OSIgd2lkdGg9IjI5LjM5IiBoZWlnaHQ9IjQyNC45MSIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMTQ0OC4xMSA2MDAuMTIpIHJvdGF0ZSgxMzUpIi8+PGNpcmNsZSBjbGFzcz0iY2xzLTIiIGN4PSI0NDkuMTIiIGN5PSI0NDcuNDgiIHI9IjU1LjExIi8+PHBhdGggY2xhc3M9ImNscy0yIiBkPSJNNTU0LjQsNTc1LjM4bC02NC4xOS02NC4xOUEzNC4zNiwzNC4zNiwwLDAsMCw0NTguNzcsNTAyYy0xMi42OSwyLjY2LTMwLjg1LDIuMTQtNDcuMjctMTQuMjgsMCwwLDU4LjA4LTk4LjU1LDc2LjU0LTc5LjI3LDE3LjgzLDE4LjYyLDE4LjE5LDM3LjY1LDE1LjExLDUwLjdhMzQuMzksMzQuMzksMCwwLDAsOSwzMi4zNWw2My4xNyw2My4xNyIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMC4wNSAwLjA0KSIvPjwvc3ZnPgo=" style="width:24px;height:24px;" data-reactid="11">' )
    output_file.write( ' &nbsp;Main' )
    output_file.write( '</a>\n' )
    output_file.write( '<a href="/final/preview/ftn0_overview.html"> Final Specs </a>\n' )
    output_file.write( '<a href="/draft/preview/ftn0_overview.html"> Draft Specs </a>\n' )
    output_file.write( '<a href="https://futoin.org/" target="_top"> FutoIn Guide </a>\n' )
    output_file.write( '</nav>\n' )
    output_file.write(
            markdown.markdown(
                    ''.join( text ),
                    extensions=['fenced_code'],
                    output_format='html5' ) )
    output_file.write( '\n</body></html>' )
    output_file.close()
    input_file.close()

    #---
    print( "Compiled " + spec_file + "\n" )

if __name__ == '__main__' :
    if len( sys.argv ) < 2 :
        die( "Usage: compilespec.py path_to_spec [...]" )
    for f in sys.argv[1:] :
        compilespec( f )
