#!/bin/bash

function compile(){
	local src="$1"
	local dst="${src}_preview"
	
	mkdir -p $dst

	for f in $src/*.md;
	do
		local df=$(echo $f | sed -e "s,^$src,$dst," -e "s/\.md$/.html/g" )
		echo "<html><head><title>$(basename $f)</title></head><body>" > $df
		cat $f | \
			sed -e "s/\.md)/.html)/g" | \
			markdown >> $df
		echo "</body></html>" >> $df
	done
}

compile draft
