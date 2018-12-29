import sys, getopt
import rdflib
import os
import relations
import datetime
import zipfile

from rdflib.namespace import RDF, RDFS, OWL
from rdflib import BNode, Literal, URIRef

from os import listdir
from os.path import isfile, join

from ontobio.ontol_factory import OntologyFactory


USE_INSTANCES = False


ofactory = OntologyFactory()

ontologies = { }

# LOADING ONTOLOGIES
print("Loading Ontologies...")
ontologies['go'] = ofactory.create('go')
ontologies['bfo'] = ofactory.create('bfo')
ontologies['ro'] = ofactory.create('ro')
ontologies['cl'] = ofactory.create('cl')
ontologies['zfa'] = ofactory.create('zfa')
ontologies['uberon'] = ofactory.create('uberon')
ontologies['emapa'] = ofactory.create('emapa')
#ontologies['chebi'] = ofactory.create('chebi')
print("Done.")


# DOING SOME TESTS
print("Start Tests:")
[ontonode] = ontologies['go'].search("GO:0005737")
print("Search: " , ontonode , ":\t" , ontologies['go'].label(ontonode))

[ontonode] = ontologies['bfo'].search("BFO:0000066")
print("Search: " , ontonode , ":\t" , ontologies['bfo'].label(ontonode))

[ontonode] = ontologies['ro'].search("RO:0002333")
print("Search: " , ontonode , ":\t" , ontologies['ro'].label(ontonode))

[ontonode] = ontologies['cl'].search("CL:0000746")
print("Search: " , ontonode , ":\t" , ontologies['cl'].label(ontonode))

[ontonode] = ontologies['zfa'].search("ZFA:0001180")
print("Search: " , ontonode , ":\t" , ontologies['zfa'].label(ontonode))

[ontonode] = ontologies['uberon'].search("UBERON:0000955")
print("Search: " , ontonode , ":\t" , ontologies['uberon'].label(ontonode))

[ontonode] = ontologies['emapa'].search("EMAPA:16486")
print("Search: " , ontonode , ":\t" , ontologies['emapa'].label(ontonode))

#[ontonode] = ontologies['chebi'].search("CHEBI:33839")
#print("Search: " , ontonode , ":\t" , ontologies['chebi'].label(ontonode))
print("Done.")

def getOntology(curie):
    prefix = curie[0:curie.index(":")].lower()
    return ontologies[prefix]



# LOADING CURIE UTIL (URI <-> CURIE)
print("Initializing CurieUtil...")
import requests
url = 'https://raw.githubusercontent.com/prefixcommons/biocontext/master/registry/go_context.jsonld'
r = requests.get(url)
from src.curieutil import CurieUtil
mapping = CurieUtil.parseContext(r.json())
curie = CurieUtil(mapping)
print("Done.")



def isGO(label):
    return "GO:" in label or "GO_" in label

def isBFO(label):
    return "BFO:" in label

def isRO(label):
    return "RO:" in label

def isUberon(label):
    return "UBERON:" in label

def isCL(label):
    return "CL:" in label

def isZFA(label):
    return "ZFA_" in label

def isEMAPA(label):
    return "EMAPA:" in label

def isOntology(label):
    return isGO(label) or isBFO(label) or isRO(label) or isUberon(label) or isCL(label) or isZFA(label) or isEMAPA(label)

def hashTrim(text):
    if "/" in text:
        return text.substring(text.lastIndexOf("/") + 1).strip()



def isBlankNode(node):
    return isinstance(node, BNode)

def isLiteralNode(node):
    return isinstance(node, Literal)

def isURINode(node):
    return isinstance(node, URIRef)

def labels(graph, node):
    if isBlankNode(node):
        return None
    results = []
    for obj in graph.objects(node, RDFS.label):
        results.append(obj)
    if len(results) == 0:
        results = None
    return results


def shortLabel(URI):
    short = curie.getCurie(URI)
    if not short:
        return URI[URI.rfind("/")+1:]
    return short.strip()


def types(graph, node, includeIndividual):
    if isBlankNode(node):
        return None
    results = []
    #    for sub, pred, obj in graph:
    for obj in graph.objects(node, RDF.type):
        if includeIndividual or (not includeIndividual and obj not in relations.owl['individual']):
            results.append(obj)
    if len(results) == 0:
        results = None
    return results

def bestLabel(graph, node, use_labels):
    nodeTypes = types(graph, node, False)
    nodeSL = shortLabel(nodeTypes[0])
    nodeName = nodeSL
    if nodeTypes:
        if use_labels:
            if isOntology(nodeSL):
                onto = getOntology(nodeSL)
                [ontonode] = onto.search(nodeSL)
                nodeName = onto.label(ontonode)
            else:
                temp = labels(graph, nodeTypes[0])
                if temp:
                    nodeName = temp[0]
    else:
        nodeName = str(node)
    return nodeName


def log(message):
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ":\t" , message)


def main(argv):
    input_ttl = None
    output_sif = None
    archive = None
    use_labels = False

    try:
        opts, args = getopt.getopt(argv, "hi:o:a:l", ["input=", "output=", "archive=", "label"])
    except getopt.GetoptError:
        print('ttl2sif.py -i <input:directory> [-o <output:directory> -a <output:archive> -l]')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('ttl2sif.py -i <input:directory> [-o <output:directory> -a <output:archive> -l]')
            sys.exit()
        elif opt in ("-i", "--input"):
            input_ttl = arg
        elif opt in ("-o", "--output"):
            output_sif = arg
        elif opt in ("-a", "--archive"):
            archive = arg
        elif opt in ("-l", "--label"):
            use_labels = True

    if not input_ttl.endswith("/"):
        input_ttl += "/"
    if output_sif and not output_sif.endswith("/"):
        output_sif += "/"
    if output_sif and not os.path.exists(output_sif):
        os.makedirs(output_sif)
    if archive and not archive.endswith(".zip"):
        archive += ".zip"

    log("Input TTL: \t" + input_ttl)
    if output_sif:
        log("Output SIF:\t" + output_sif)
    if archive:
        log("Archive:   \t" + archive)
        zipped_f = zipfile.ZipFile(archive, 'w')
    if use_labels:
        log("Use labels:\t" + str(use_labels))


    ttl_files = [f for f in listdir(input_ttl) if isfile(join(input_ttl, f))]
    count = 0

    # travel through all ttl files
    for ttl_file in ttl_files:
        g = rdflib.Graph()
        g.parse(input_ttl + ttl_file, format="ttl")

        content = "";
        # travel through all causal relationships
        for sub, pred, obj in g:
            if str(pred) in relations.causal.values():

                subName = bestLabel(g, sub, use_labels)
                objName = bestLabel(g, obj, use_labels)

                predName = shortLabel(pred)
                if use_labels:
                    predName = relations.causal.inv[str(pred)]
                #print(predName)
                content += subName + "\t" + predName + "\t" + objName + "\n"

        if output_sif:
            f = open(output_sif + ttl_file[0:ttl_file.rfind(".")] + ".sif", 'w')
            print('write to ' + output_sif + ttl_file[0:ttl_file.rfind(".")] + ".sif")
            f.write(content)
            f.close()

        if archive:
            zpf = zipped_f.open("gocam-sif/" + ttl_file[0:ttl_file.rfind(".")] + ".sif", "w")
            zpf.write(str.encode(content))
            zpf.close()

        count += 1

    if archive:
        zipped_f.close()

    print(count , " TTL files exported to SIF")


if __name__ == "__main__":
    main(sys.argv[1:])






# TRASH CODE

    # g=rdflib.Graph()
    # g.load('http://dbpedia.org/resource/Semantic_Web')

    # for s,p,o in g:
    #    print(s,p,o)

#        nodes = g.objects('http://model.geneontology.org/5b528b1100001416/5b528b1100001469', RDF.type)
#        nodes = g.triples((URIRef('http://model.geneontology.org/5b528b1100001416/5b528b1100001469'), RDF.type, None))
#        for node in nodes:
#            print(node)

#        for s, p, o in g.triples((None, RDF.type, None)):
#            print(s, p , o)

