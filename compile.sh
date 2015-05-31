#!/bin/bash

function compile(){
	local src="$1"
	
	mkdir -p $src/{meta,preview}
	ls $src/*.md | grep -v 'ftnX_' | xargs python ./tools/compilespec.py
}

compile draft
compile final
