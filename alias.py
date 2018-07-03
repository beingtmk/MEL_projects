#batch fetch
from Bio import Entrez
import time
# import xml.etree.ElementTree as ET
import xml.dom.minidom

import json


def main(compound):
    #print("pls enter a term:")
    #compound = input()

    try:
        from urllib.error import HTTPError, URLError  # for Python 3
    except ImportError:
        from urllib2 import HTTPError  # for Python 2
    Entrez.email = "beingtmk@iitg.ernet.in"
    search_results = Entrez.read(Entrez.esearch(db="gene",
                                                term=compound,
                                                usehistory="y", sort="relevance"))
    count = int(search_results["Count"])
    #print("Found %i results" % count)
    #print(search_results["IdList"])

    for id in search_results["IdList"]:

        attempt = 1
        while attempt <= 3:
            try:
                print("running")
                search = Entrez.read(Entrez.esummary(db="gene", id=id))
                print("*Downloaded")
                print()
                break

            except URLError or HTTPError as err:
                print("Received error from server %s" % err)
                print("Attempt %i of 3" % attempt)
                attempt += 1
                time.sleep(15)

        organism = search['DocumentSummarySet']['DocumentSummary'][0]["Organism"]["ScientificName"]

        if(organism == "Homo sapiens"):

            alias = search['DocumentSummarySet']['DocumentSummary'][0]['OtherAliases']
            aliases_1 = alias.replace(" ", "")
            aliases = aliases_1.split(',')
            break

    return aliases

print("Insert file name")
file = input()

data = open(file, "r").read()

#remove the last empty element
genes = data.split("\n")[:-1]

dict = {}


for idx,gene in enumerate(genes):
    print("**Downloading " + str(idx+1) + " of " + str(len(genes)) + " : " + str(gene) )
    #print()
    alias = main(gene)

    dict[gene] = alias


    with open('result.json', 'w') as fp:
        json.dump(dict, fp)


print("gene_alias.json successfully created.")
