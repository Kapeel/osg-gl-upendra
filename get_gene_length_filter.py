#!/usr/bin/env python

import sys

input = sys.argv[1]

genes = {} # empty list

with open(input, "rU") as fh_in:
	for line in fh_in:
		line = line.strip()
		if line[0] == ">":
			gene_names = line
			genes[gene_names] = ''
		else:
			genes[gene_names]+=line

for (name,val) in genes.items():
    val = len(val)
    print(name[1:] + "\t" + str(val)) 
