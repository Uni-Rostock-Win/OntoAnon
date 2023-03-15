# OntoAnon
***An Application For Anonymizing Ontologies.***

OntoAnon iterates through all triples of a graph and anonymizes/removes the data while preserving the ontology structure. Data is preserved by keeping standard vocabulary like the ontology languages *OWL, RDF(S), SHACL*, but also standardized ontologies like *FOAF, DC, SKOS*. A full list of kept namespaces can be found [here](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.namespace.html#namespace-utilities). OntoAnon runs locally, so no data leaves the computer. It allows sharing the structural data and using online tools like [neontometrics](http://neontometrics.com) or the OntolOlogy Pitfall Scanner ([OOPS](https://oops.linkeddata.es/)), without giving away company secrets.

OntoAnon builds on the python GUI TKinter and [rdflib](https://rdflib.readthedocs.io/en/stable/index.html). The former is preinstalled with current python versions, the latter can be acquired using pip or the corresponding pipfile.

The tool is part of a publication currently under review. The development of the tool was part of a bachelor thesis by Robert Schlücker, cf. https://github.com/Junech1/Ontology-Anonymisation for the original repository.