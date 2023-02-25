# Fencviz

Funcenviz is a tool that, given a set of genes it builds a network with the genes by exploiting the human protein protein interactome. Then by performing a function enrichment analysis by Exploiting [g:Profiler](https://biit.cs.ut.ee/gprofiler/gost) highlights proteins in the network that are related to a specific function. The functions can be filtered from p-value and source database.

In order to use this tool first you have to install requirements by running:

```
pip install -r requirements.txt

```

The usage of fencviz is from command line.

```

python3 fencviz.py -l data/gene_symbol.txt


```

The flag -l is the list of input genes. It consist in a .txt file of space separated gene symbols..



https://user-images.githubusercontent.com/104980753/221161672-edfbfc48-8c4d-4200-83f9-bf61fde05f47.mp4





