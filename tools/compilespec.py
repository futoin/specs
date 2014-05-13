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
        print( "- Skipping " + spec_file + "\n" )
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
    in_header = True
    spec_ver = ''

    for l in input_file:
        try:
            if in_header :
                pair = l.split( ':', 2 )

                if len( pair ) == 2 :
                    tag, value = pair
                    value = value.strip()

                    if tag == 'Version' :
                        spec_ver = value
                    elif tag in ('Copyright','Authors') :
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
            m = schema_re.match( l )

            if m is not None:
                if parsing_iface or parsing_schema :
                    print( "Current Schema: " + str( parsing_schema ) + "\n" )
                    die( str(curr_line) + ': Unable to parse Schema in scope of another Schema or Iface\n' )

                parsing_schema = m.group(1)
                text.append('<p class="futoin-schema">Schema: ' + parsing_schema + '</p>\n')

            elif l == '`}Schema`\n' :
                schema = json.dumps( json.loads( ''.join( json_text ) ) )
                spec_major_ver = spec_ver.split('.')
                spec_major_ver = spec_major_ver[0]

                schema_file = parsing_schema + '-' + spec_major_ver + '-schema.json'

                with codecs.open( os.path.join( meta_dir, schema_file ),
                                "w",
                                encoding="utf-8",
                                errors="xmlcharrefreplace"
                ) as f:
                    f.write( schema )

                schema_file_nover = os.path.join( meta_dir, parsing_schema + '-schema.json' )
                try:
                    os.unlink( schema_file_nover )
                except OSError:
                    pass
                os.symlink( schema_file, schema_file_nover )

                parsing_schema = False
                json_text = []

            elif l == '`Iface{`\n' :
                if parsing_iface or parsing_schema :
                    die( str(curr_line) + ': Unable to parse Iface in scope of Schema or another Iface\n' )

                parsing_iface = True

            elif l == '`}Iface`\n' :
                if not parsing_iface:
                    die( str(curr_line) + ': Unexpected end of Iface' )

                iface = json.loads( ''.join( json_text ) )
                iface_name = iface['iface']
                iface_major_ver = iface['version'].split('.')
                iface_major_ver = iface_major_ver[0]
                iface = json.dumps( iface )

                iface_file = iface_name + '-' + iface_major_ver + '-iface.json'

                with codecs.open( os.path.join( meta_dir, iface_file ),
                                "w",
                                encoding="utf-8",
                                errors="xmlcharrefreplace"
                ) as f:
                    f.write( iface )

                iface_file_nover = os.path.join( meta_dir, iface_name + '-iface.json' )
                try:
                    os.unlink( iface_file_nover )
                except OSError:
                    pass
                os.symlink( iface_file, iface_file_nover )

                parsing_iface = False
                json_text = []

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
    spec_major_ver = spec_ver.split('.')
    spec_major_ver = spec_major_ver[0]
    html_ver_file = html_file.replace( '.html', '-' + spec_major_ver + '.html' )
    
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

    try :
        os.unlink( html_file )
    except OSError:
        pass
    os.symlink( os.path.basename( html_ver_file ), html_file )

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
