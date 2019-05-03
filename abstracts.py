#batch fetch
from Bio import Entrez
import time
# import xml.etree.ElementTree as ET
import xml.dom.minidom

try:
    from urllib.error import HTTPError  # for Python 3
except ImportError:
    from urllib2 import HTTPError  # for Python 2
Entrez.email = "beingtmk@gmail.com"

gene = input("pls enter a term:")

#getting aliases
alias_results = Entrez.read(Entrez.esearch(db="gene",
                                            term=gene,
                                            usehistory="y", sort="relevance"))
count = int(alias_results["Count"])
#print("Found %i results" % count)
#print(search_results["IdList"])

print("**Running alias download.")
for id in alias_results["IdList"]:

    attempt = 1
    while attempt <= 3:
        try:
            search = Entrez.read(Entrez.esummary(db="gene", id=id))
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


print("*Downloaded:")
print(aliases)

print()

while(input("Want to remove any from the list of aliases: (y/n)") == 'y'):
    str = input("Enter a alias to remove: ")
    #print(str)
    aliases.remove(str)
    print("Want to remove any more from the list of aliases: (y/n)")

print("Want to add any to the list of aliases: (y/n)")
while(input() == 'y'):
    str = input("Enter a alias to remove: ")
    aliases.append(str)
    print("Want to add any more to the list of aliases: (y/n)")

print("*Updated Aliases:")
print(aliases)

# aliases = ["GPER", "GPER1", "GPR30", "GPCR-bR", "G Protein-Coupled Estrogen Receptor 1", "G-Protein Coupled Estrogen Receptor 1"]

#abstract download
dict = {}

for compound in aliases:
    search_results = Entrez.read(Entrez.esearch(db="pubmed",
                                                term=compound, usehistory='y'))

    count = int(search_results["Count"])
    print("Found %i results for %s" %(count, compound))

    batch_size = min(50, count)
    #batch_size = 0;
    if(not batch_size):
        continue

    for start in range(0,count,batch_size):
        end = min(count, start+batch_size)
        print("Going to download record %i to %i" % (start+1, end))
        attempt = 1
        while attempt <= 3:
            try:
                fetch_handle = Entrez.efetch(db="pubmed",rettype="xml",
                                             retmode="text",retstart=start,
                                             retmax=batch_size,
                                             webenv=search_results["WebEnv"],
                                             query_key=search_results["QueryKey"])
                break
            except HTTPError as err:
                if 500 <= err.code <= 599:
                    print("Received error from server %s" % err)
                    print("Attempt %i of 3" % attempt)
                    attempt += 1
                    time.sleep(15)
                else:
                    raise
        data = fetch_handle.read()
        # xml = ET.fromstring(data)
        element = xml.dom.minidom.parseString(data)
        fetch_handle.close()

        for i in range(0, batch_size):

            try:
                PMID = element.getElementsByTagName('PMID')[i].childNodes[0].data
                article = element.getElementsByTagName('AbstractText')[i]
                article_data = article.childNodes[0].data
                #print(article_data)
            except (IndexError, AttributeError):
                article_data = None

            if PMID not in dict.keys():
                dict[PMID] = article_data
            #print(PMID)

print("output file name:")
output = input()


import json
with open(output, 'w') as fp:
    json.dump(dict, fp)

print("%s successfully created."%output)
