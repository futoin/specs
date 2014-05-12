#!/usr/bin/python3

import json
import markdown
import sys
import os
import codecs
import re

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
        print( "Skipping " + spec_file + "\n" )
        return

    #---
    input_file = codecs.open( spec_file, mode="r", encoding="utf-8" )


    #---
    text = []
    json_text = []
    parsing_iface = False
    parsing_schema = False
    schema_re = re.compile( '^`Schema\\(([a-z0-9\-_]+)\\){`$' )
    curr_line = 1

    for l in input_file:
        try:
            m = schema_re.match( l )

            if m is not None:
                if parsing_iface or parsing_schema :
                    print( "Current Schema: " + str( parsing_schema ) + "\n" )
                    die( str(curr_line) + ': Unable to parse Schema in scope of another Schema or Iface\n' )

                parsing_schema = m.group(1)
                text.append('<div class="futoin-schema">')
                text.append('<p>' + parsing_schema + '</p>')

            elif l == '`}Schema`\n' :
                schema = json.dumps( json.loads( ''.join( json_text ) ) )

                with codecs.open( os.path.join( meta_dir, parsing_schema + '.schema.json' ),
                                "w",
                                encoding="utf-8",
                                errors="xmlcharrefreplace"
                ) as f:
                    f.write( schema )

                parsing_schema = False
                json_text = []
                text.append('</div>')

            elif l == '`Iface{`\n' :
                if parsing_iface or parsing_schema :
                    die( str(curr_line) + ': Unable to parse Iface in scope of Schema or another Iface\n' )

                parsing_iface = True
                text.append('<div class="futoin-iface">')

            elif l == '`}Iface`\n' :
                if not parsing_iface:
                    die( str(curr_line) + ': Unexpected end of Iface' )

                iface = json.loads( ''.join( json_text ) )
                iface_name = iface['iface']
                iface = json.dumps( iface )

                with codecs.open( os.path.join( meta_dir, iface_name + '.iface.json' ),
                                "w",
                                encoding="utf-8",
                                errors="xmlcharrefreplace"
                ) as f:
                    f.write( iface )


                parsing_iface = False
                json_text = []
                text.append('</div>')

            else :
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
    output_file = codecs.open( html_file, "w",
                            encoding="utf-8",
                            errors="xmlcharrefreplace"
    )

    output_file.write( '<html><head><title>' + os.path.basename( spec_file ) + '</title></head><body>' )
    output_file.write( markdown.markdown( ''.join( text ), output_format='html5' ) )
    output_file.write( '</body></html>' )
    output_file.close()
    input_file.close()

    #---
    print( "Compiled " + spec_file + "\n" )

if __name__ == '__main__' :
    if len( sys.argv ) < 2 :
        die( "Usage: compilespec.py path_to_spec [...]" )
    for f in sys.argv[1:] :
        compilespec( f )
