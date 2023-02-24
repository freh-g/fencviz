# Fencviz

Funcenviz is a tool that, given a set of genes it builds a network with the genes by exploiting the human protein protein interactome. Then by performing a function enrichment analysis by Exploiting [g:Profiler](https://biit.cs.ut.ee/gprofiler/gost) highlights proteins in the network that are related to a specific function. The functions can be filtered from p-value and source database.

The usage of the tool is from command line.

```

python3 fencviz.py -l data/gene_symbol.txt


```

The flag -l is the list of genes that the model is taking as input. It consist in a txt file with space separated list of gene symbols.



