#!/bin/bash

function compile(){
	local src="$1"
	
	mkdir -p $src/{meta,preview}
	./tools/compilespec.py $src/*.md
}

compile draft
compile final
