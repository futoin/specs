#!/bin/bash

function compile(){
	local src="$1"
	
	mkdir -p $src/meta

	for f in $src/*.md;
	do
        ./tools/compilespec.py $f
	done
}

compile draft
compile final
