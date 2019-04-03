import os, datetime, sys, getopt, rdflib, zipfile
import relations, ontology_handler

from rdflib.namespace import RDF, RDFS, OWL
from rdflib import BNode, Literal, URIRef

from os import listdir
from os.path import isfile, join

import networkx as nx


# LOADING CURIE UTIL (URI <-> CURIE)
import requests
from src.curieutil import CurieUtil
curie = None
def initCurieUtil():
    print("Initializing CurieUtil...")
    url = 'https://raw.githubusercontent.com/prefixcommons/biocontext/master/registry/go_context.jsonld'
    r = requests.get(url)
    mapping = CurieUtil.parseContext(r.json())
    global curie
    curie = CurieUtil(mapping)
    print("Done.")



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
    """
    Returns either the CURIE or the value after the last / found
    """
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
            if ontology_handler.isOntology(nodeSL):
                onto = ontology_handler.getOntology(nodeSL)
                if onto is None:
                    print("ONTO is null !" , nodeSL, onto)
                # FIX: ontobio needs to have a curie with ":", but ZFA (e.g. ZFA_0001109) are sent back with "_"
                if "_" in nodeSL:
                    nodeSL = nodeSL.replace("_", ":")
                [ontonode] = onto.search(nodeSL)
                nodeName = onto.label(ontonode)
            else:
                temp = labels(graph, nodeTypes[0])
                if temp:
                    nodeName = temp[0]
    else:
        nodeName = str(node)
    
    # this case can happened when a term is deprecated, e.g. GO:0001142
    if not nodeName:
        print("WARNING: " + nodeSL + " has no label (see " , node , ")")
        return nodeSL
#        print(ontology_handler.getOntology(nodeSL).search(nodeSL))
#        print(ontology_handler.getOntology(nodeSL).label(ontology_handler.getOntology(nodeSL).search(nodeSL)))
    return nodeName

def geneNodes(nodes):
    gn = []
    for node in nodes:
        if not ontology_handler.isOntology(node):
            gn.append(node)
    return gn

def log(message):
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ":\t" , message)

def usage():
    print('ttl2count.py -i <input:directory>\n')


def main(argv):
    input_ttl = None
    output_sif = None
    archive = None

    # If true, try to change the URI into their labels (either searching rdfs:label or probing their respective ontology)
    use_labels = False

    # If true, any separate instance of a same node will be duplicated as ^2, ^3, ^4 etc, so it stays unique in SIF
    duplicate_instances = False

    only_geneproduct = False
    

    try:
        opts, args = getopt.getopt(argv, "hi:o:a:ldg", ["input=", "output=", "archive=", "label", "duplicate", "geneproduct"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--input"):
            input_ttl = arg

    if input_ttl is None:
        usage()
        sys.exit(1)

    # Prepare parameters
    if not input_ttl.endswith("/"):
        input_ttl += "/"

    # Verbose on parameters
    log("Input TTL:             \t" + input_ttl)

    # Then start initializing CurieUtil and Ontologies
    initCurieUtil()
    ontology_handler.initOntologies()


    # List TTL files
    ttl_files = [f for f in listdir(input_ttl) if isfile(join(input_ttl, f))]
    count = 0

    # Travel through all TTL files
    for ttl_file in ttl_files:
        g = rdflib.Graph()
        g.parse(input_ttl + ttl_file, format="ttl")

        # Dictionary to handle multiple instances of the same entity (when duplicate_instances is true)
        instances = { }

        # String variable storing the triples before writing a SIF file (either in archive or output_sif directory)
        sif_content = ""

        # Create temporary graph (1 / GO-CAM)
        nxg = nx.Graph()

        causal_count = 0
        # Travel through all causal relationships
        for sub, pred, obj in g:
            if str(pred) in relations.true_causal.values():
                causal_count += 1
        print(ttl_file + "\t" +  str(causal_count))



if __name__ == "__main__":
    main(sys.argv[1:])