from bidict import bidict

true_causal = bidict({
    "directly_activates": "http://purl.obolibrary.org/obo/RO_0002406",
    "directly_inhibits": "http://purl.obolibrary.org/obo/RO_0002408",

    "directly_positively_regulates": "http://purl.obolibrary.org/obo/RO_0002629",
    "directly_negatively_regulates": "http://purl.obolibrary.org/obo/RO_0002630",

    "causally_upstream_of": "http://purl.obolibrary.org/obo/RO_0002411",
    "causally_upstream_of_positive_effect": "http://purl.obolibrary.org/obo/RO_0002304",
    "causally_upstream_of_negative_effect": "http://purl.obolibrary.org/obo/RO_0002305",

    "causally_upstream_of_or_within": "http://purl.obolibrary.org/obo/RO_0002418",
    "causally_upstream_of_or_within_positive_effect": "http://purl.obolibrary.org/obo/RO_0004047",
    "causally_upstream_of_or_within_negative_effect": "http://purl.obolibrary.org/obo/RO_0004046",

    "positively_regulates": "http://purl.obolibrary.org/obo/RO_0002213",
    "negatively_regulates": "http://purl.obolibrary.org/obo/RO_0002212",

    "results_in_acquisition_of_features_of": "http://purl.obolibrary.org/obo/RO_0002315",
    "transports_or_maintains_localization_of": "http://purl.obolibrary.org/obo/RO_0002313",
    "results_in_movement_of": "http://purl.obolibrary.org/obo/RO_0002565"
})

all = bidict({
    "enabled_by": "http://purl.obolibrary.org/obo/RO_0002333",
    "occurs_in": "http://purl.obolibrary.org/obo/BFO_0000066",

    "has_input": "http://purl.obolibrary.org/obo/RO_0002233",
    "has_output": "http://purl.obolibrary.org/obo/RO_0002234",

    "part_of": "http://purl.obolibrary.org/obo/BFO_0000050",
    "has_part": "http://purl.obolibrary.org/obo/BFO_0000051",

    "directly_activates": "http://purl.obolibrary.org/obo/RO_0002406",
    "directly_inhibits": "http://purl.obolibrary.org/obo/RO_0002408",

    "directly_provides_input_for": "http://purl.obolibrary.org/obo/RO_0002413",
    "directly_positively_regulates": "http://purl.obolibrary.org/obo/RO_0002629",
    "directly_negatively_regulates": "http://purl.obolibrary.org/obo/RO_0002630",

    "causally_upstream_of": "http://purl.obolibrary.org/obo/RO_0002411",
    "causally_upstream_of_positive_effect": "http://purl.obolibrary.org/obo/RO_0002304",
    "causally_upstream_of_negative_effect": "http://purl.obolibrary.org/obo/RO_0002305",

    "causally_upstream_of_or_within": "http://purl.obolibrary.org/obo/RO_0002418",
    "causally_upstream_of_or_within_positive_effect": "http://purl.obolibrary.org/obo/RO_0004047",
    "causally_upstream_of_or_within_negative_effect": "http://purl.obolibrary.org/obo/RO_0004046",

    "positively_regulates": "http://purl.obolibrary.org/obo/RO_0002213",
    "negatively_regulates": "http://purl.obolibrary.org/obo/RO_0002212",

    "results_in_acquisition_of_features_of": "http://purl.obolibrary.org/obo/RO_0002315",
    "transports_or_maintains_localization_of": "http://purl.obolibrary.org/obo/RO_0002313",
    "results_in_movement_of": "http://purl.obolibrary.org/obo/RO_0002565"
})

rdfs = bidict({
    "label": "http://www.w3.org/2000/01/rdf-schema#"
})

rdf = bidict({
    "type": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
})

owl = bidict({
    "individual": "http://www.w3.org/2002/07/owl#NamedIndividual"
})
