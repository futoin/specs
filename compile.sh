#!/bin/bash

function compile(){
	local src="$1"
	
	mkdir -p $src/{meta,preview}
	ls $src/*.md | grep -v 'ftnX_' | sort -V | xargs python ./tools/compilespec.py
	ls $src/meta/*-?.?-iface.json | xargs cid tool exec node -- ./tools/checkspecs.js
}

compile draft
compile final
