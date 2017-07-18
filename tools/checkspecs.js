'use strict';

var async_steps = require( 'futoin-asyncsteps' );
var SpecTools = require('futoin-invoker').SpecTools;
var iface_cache = {};

async_steps()
    .add(
        (as) => {
            as.forEach(
                process.argv.slice(2),
                (as, k, v) => {
                    console.log('Checking :' + v);
                    var m = v.match( /^(.+)\/([^-]+)-([0-9]+\.[0-9])+-iface\.json$/)

                    SpecTools.loadIface(
                        as,
                        {
                            iface: m[2],
                            version: m[3],
                        },
                        [ m[1] ],
                        iface_cache
                    );
                }
            );
        },
        (as, err) => {
            console.log(err + ': ' + as.state.error_info);
        }
    )
    .execute();
