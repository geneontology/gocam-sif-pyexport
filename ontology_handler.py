from ontobio.ontol_factory import OntologyFactory

# LOADING ONTOLOGIES
ontologies = { }
def initOntologies():
    ofactory = OntologyFactory()
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

def getOntology(curie):
    if ":" in curie:
        prefix = curie[0:curie.index(":")].lower()
    elif "_" in curie:
        prefix = curie[0:curie.index("_")].lower()
    else:
        print("WARNING: " + curie + " has no detectable prefix (prefix:xxx or prefix_xxx)")
        return None
    return ontologies[prefix]


# DOING SOME TESTS
def testOntologies():
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
