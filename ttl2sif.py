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
    print('ttl2sif.py -i <input:directory> [-o <output:directory> -a <output:archive> -l]\n')


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
        elif opt in ("-o", "--output"):
            output_sif = arg
        elif opt in ("-a", "--archive"):
            archive = arg
        elif opt in ("-l", "--label"):
            use_labels = True
        elif opt in ("-d", "--duplicate"):
            duplicate_instances = True
        elif opt in ("-g", "--geneproduct"):
            only_geneproduct = True
            use_labels = False # temporary hack

    if input_ttl is None:
        usage()
        sys.exit(1)

    if not os.path.exists(input_ttl):
        print("Input TTL '" + input_ttl + "' is not a directory or does not exist\n")
        sys.exit(1)

    if not output_sif and not archive:
        print("You must define either the output_sif directory or the archive parameter\n")
        sys.exit(1)        

    # Prepare parameters
    if not input_ttl.endswith("/"):
        input_ttl += "/"
    if output_sif and not output_sif.endswith("/"):
        output_sif += "/"
    if output_sif and not os.path.exists(output_sif):
        os.makedirs(output_sif)
    if archive and not archive.endswith(".zip"):
        archive += ".zip"
        zipped_f = zipfile.ZipFile(archive, 'w')

    # Verbose on parameters
    log("Input TTL:             \t" + input_ttl)
    if output_sif:
        log("Output SIF:            \t" + output_sif)
    if archive:
        log("Archive:               \t" + archive)
    log("Use labels:            \t" + str(use_labels))
    log("Duplicate instances:   \t" + str(duplicate_instances))
    log("Only Gene Products:    \t" + str(only_geneproduct))

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

        # Travel through all causal relationships
        for sub, pred, obj in g:
            if str(pred) in relations.causal.values():

                subName = bestLabel(g, sub, use_labels)
                objName = bestLabel(g, obj, use_labels)

                # Double check: this should be retrieve from BFO or RO directly, but I didn't always got labels for some relations
                predName = shortLabel(pred)
                if use_labels:
                    predName = relations.causal.inv[str(pred)]
                
                if duplicate_instances:
                    if subName in instances.keys():
                        numbers = instances[subName]
                        if sub not in numbers.keys():
                            numbers[sub] = "_" + str(len(numbers) + 1)
                        subName = subName + numbers[sub]
                    else:
                        numbers = { sub: "" }
                        instances[subName] = numbers

                    if objName in instances.keys():
                        numbers = instances[objName]
                        if obj not in numbers.keys():
                            numbers[obj] = "_" + str(len(numbers) + 1)
                        objName = objName + numbers[obj]
                    else:
                        numbers = { obj: "" }
                        instances[objName] = numbers

                if only_geneproduct:
                    nxg.add_edge(subName, objName, relationship=predName)
                else:
                    sif_content += subName + "\t" + predName + "\t" + objName + "\n"

        # In this case, we create a graph containing only GP-GP relationships
        if only_geneproduct:
            # Further graph doc: https://networkx.github.io/documentation/networkx-1.10/tutorial/tutorial.html
            ccs = nx.connected_components(nxg)
            compid = 1
            for cc in ccs:
                gns = geneNodes(cc)
#                print(ttl_file , gns)
                if len(gns) > 1:
                    for i in range(0, len(gns)):
                        sif_content += gns[i] + "\tcausally_related_to\t" + "cc" + str(compid) + "\n"
                    compid += 1
#                elif len(gns) > 0:
#                    sif_content += gns[0] + "\n"

        if len(sif_content) > 0:
            if output_sif:
                f = open(output_sif + ttl_file[0:ttl_file.rfind(".")] + ".sif", 'w')
                f.write(sif_content)
                f.close()

            if archive:
                zpf = zipped_f.open("gocam-sif/" + ttl_file[0:ttl_file.rfind(".")] + ".sif", "w")
                zpf.write(str.encode(sif_content))
                zpf.close()
            count += 1

    if archive:
        zipped_f.close()

    print(count , " TTL files exported to SIF")


if __name__ == "__main__":
    main(sys.argv[1:])
    # ontology_handler.initOntologies()
    # goterm = "GO:0048489"
    # ont = ontology_handler.getOntology(goterm)
    # print("search: " , ont.search(goterm))
    # print("node: " , ont.node(goterm))
    # print("type: " , ont.get_node_type(goterm))
    # print("definition: ", ont.text_definition(goterm))
    # print("is_obsolete: ", ont.is_obsolete(goterm))
    # print("replaced_by: " , ont.replaced_by(goterm))
    # print("logical_definition: ", ont.logical_definitions(goterm))
    # print("synonyms: " , ont.synonyms(goterm))
    # print("label: " , ont.label(goterm))
    # print("xrefs: " , ont.xrefs(goterm))

