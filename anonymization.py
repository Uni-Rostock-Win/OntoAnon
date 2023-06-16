from tkinter import messagebox

import rdflib, time
from rdflib import Graph, Literal, URIRef, BNode
from rdflib.namespace import Namespace

predefined_ns = [ns for ns in rdflib.namespace._NAMESPACE_PREFIXES_RDFLIB.values()] + [ns for ns in rdflib.namespace._NAMESPACE_PREFIXES_CORE.values()]
predefined_ns.append(rdflib.Namespace("http://www.w3.org/2003/11/swrl#")) # This one was missing

def anonymize(filename, fileformat, anony_path, dict_path, all_ns):
    # Create a Graph
    start_time = time.time()
    g = Graph(store="SimpleMemory")
    



    try:
        # Parse in an ontologie file
        if (fileformat == 'The file is missing, an url or not supported.' or fileformat == ''):
            g.parse(filename)
        else:
            g.parse(filename, fileformat)
    except:
        messagebox.showerror("Error", "Ontology file could not be parsed by RDFlib. Please check the file for errors!")

    # identifing the different elements in the ontology
    namespaces, objects, predicates, subjects = identify_elements(g)

    translator = {}

    # translate the namespaces
    namespace_translator = []
    namespace_to_generic_namespace(namespaces, namespace_translator, all_ns)
    translator.update({element[0][1]:element[1][1] for element in namespace_translator})

    # translate the subjects

    subject_translator = subject_to_generic_subject(subjects, namespace_translator, all_ns)
    translator.update(subject_translator)

    # translate the predicates
    predicat_translator = predicate_to_generic_predicat(predicates, namespace_translator, subject_translator, all_ns)
    translator.update(predicat_translator)

    # translate the objects
    object_translator = object_to_generic_object(objects, namespace_translator, subject_translator, predicat_translator, all_ns)
    translator.update(object_translator)

    # Replaces the subjects, predicates and objects in the graph with the anonymized elements
    g = change_graph(g, subject_translator, predicat_translator, object_translator)

    # Saving the anonymized graph to the selected file
    #new_graph = g.serialize(format=fileformat)
    new_graph = g.serialize(format='xml')

    with open(anony_path, 'w') as fp:
        fp.write(new_graph)

    # Saves the translation dictionary
    outputTranslator = ""
    for k,v in translator.items():
        if not isinstance(k, rdflib.BNode):
            outputTranslator += ("\n" + str(k) + " => " + str(v))
    with open(dict_path, 'w', encoding="utf-8") as fp:
        fp.write(outputTranslator)
    end_time = time.time()
    execution_time = int(end_time - start_time)
    
    # Showing a message that the process is finished.
    messagebox.showinfo("System-Message", f"Anonymization is finished.\nExecution time: {execution_time} seconds")

# identifying the elements of a ontology graph
def identify_elements(g):
    # init lists
    namespaces = []
    subjects = []
    predicates = []
    objects = []

    # get the namespaces
    for namespace in g.namespaces():
        namespaces.append(namespace)

    # Loop through each triple in the graph (subj, pred, obj)
    for subj, pred, obj in g:
        # elements to the coresponding lists
        subjects.append(subj)
        predicates.append(pred)
        objects.append(obj)

    # delete doubles
    namespaces = list(dict.fromkeys(namespaces))
    subjects = list(dict.fromkeys(subjects))
    predicates = list(dict.fromkeys(predicates))
    objects = list(dict.fromkeys(objects))
    return namespaces, objects, predicates, subjects

# translates the namespaces to generic namespaces
def namespace_to_generic_namespace(namespaces, translator, all_ns):
    name_counter = 0
    standard_ns = False

    for name_element in namespaces:
        # check if namespace standard namespace
        for ns in all_ns:
            if (URIRef(name_element[1]) in Namespace(ns)) :
                standard_ns = True
                translator.append([name_element, name_element])

        # check if namespace has an URL and translate it with an URIRef, otherwise it becomes a Literal
        if ('http' in name_element[1]) and (standard_ns == False):
            if '#' in name_element[1]:
                translator.append([name_element, ("Namespace" + str(name_counter),
                                                  URIRef("http://anonym-url.anon/Namespace" + str(name_counter) + "#"))])
            else:
                translator.append([name_element, ("Namespace" + str(name_counter),
                                                  URIRef("http://anonym-url.anon/Namespace" + str(name_counter) + "/"))])
        elif standard_ns == False:
            translator.append([name_element, Literal("Namespace" + str(name_counter))])
        name_counter = name_counter + 1

        standard_ns = False

# translates the subjects to generic subjects
def subject_to_generic_subject(subjects:list, namespace_translator:list, all_ns:list):
    """Translates a list of subjects

    Args:
        subjects (list): The subjects (list of URIRefs) to be translated
        namespace_translator (list): The already translated namespaces
        all_ns (list): The list of standard-Namespaces

    Returns:
        dict: key value pair for original and translated values
    """
    subject_translator = {}
    subj_counter = 0
    standard_ns = False
    for subj_element in subjects:
        #check if namespace standard namespace
        for ns in all_ns:
            if (URIRef(subj_element) in Namespace(ns)) :
                standard_ns = True
                subject_translator.update({subj_element: subj_element})
            protocol = "http://" if ('http' in subj_element) else ""
            protocol = "urn:" if ('urn:' in subj_element) else protocol
        # check if subject contains an URIRef, if not translate it as normal Literal
        if protocol != "" and (standard_ns == False):

            # check if URIRef is a known namespace
            is_namespace = False
            namespace_count = 0
            for element in namespace_translator:
                if element[0][1][:-1] in subj_element:
                    is_namespace = True
                    break
                namespace_count = namespace_count +1

            # if URIRef is a known namespace translate it accordingly
            # if not translate it as normal URIRef
            if is_namespace:
                new_string = str(namespace_translator[namespace_count][1][1] + 'Subject' + str(subj_counter))
                subject_translator.update({subj_element: URIRef(new_string)})
            else:
                if '#' in subj_element:
                    subject_translator.update({subj_element: URIRef(protocol + "anonym-subj-url.anon#Subject" + str(subj_counter))})
                else:
                    subject_translator.update({subj_element: URIRef(protocol + "anonym-subj-url.anon/Subject" + str(subj_counter))})
        elif standard_ns == False:
            if '_:' in subj_element.n3():
                subject_translator.update({subj_element: BNode(subj_element)})
            else:
                subject_translator.update({subj_element: Literal("Subject" + str(subj_counter), datatype=subj_element.datatype, lang=subj_element.language)})
        subj_counter = subj_counter + 1
        standard_ns = False
    return subject_translator

# translates the predicates to generic predicates
def predicate_to_generic_predicat(predicates: list, namespace_translator: list, subject_translator: dict, all_ns:list)-> dict:
    predicate_translator = {}
    predicat_counter = 0
    standard_ns = False
    for pred_element in predicates:
        # check if namespace standard namespace
        for ns in all_ns:
            if (URIRef(pred_element) in Namespace(ns)) :
                standard_ns = True
                predicate_translator.update({pred_element: pred_element})
        protocol = "http://" if ('http' in pred_element) else ""
        protocol = "urn:" if ('urn:' in pred_element) else protocol        
        if protocol != "" and (standard_ns == False):
            # check if URIRef is a known namespace
            is_namespace = False
            namespace_count = 0
            for element in namespace_translator:
                if element[0][1][:-1] in pred_element:
                    is_namespace = True
                    break
                namespace_count = namespace_count +1

            # check if URI is known subject
            is_subject = False
            subject_value = ''
            if pred_element in subject_translator:
                is_subject = True
                subject_value = subject_translator[pred_element]

            if is_subject:
                predicate_translator.update({pred_element: URIRef(subject_value)})

            # if URIRef is a known namespace translate it accordingly
            # if not translate it as normal URIRef
            elif is_namespace:
                new_string = str(namespace_translator[namespace_count][1][1] + 'Predicate' + str(predicat_counter))
                predicate_translator.update({pred_element: URIRef(new_string)})
            else:
                if '#' in pred_element:
                    predicate_translator.update({pred_element: URIRef(protocol + "anonym-pred-url.anon#Predicate" + str(predicat_counter))})
                else:
                    predicate_translator.update({pred_element: URIRef(protocol + "anonym-pred-url.anon/Predicate" + str(predicat_counter))})
        elif not standard_ns:
            predicate_translator.update({pred_element: Literal("Predicate" + str(predicat_counter))})
        predicat_counter = predicat_counter + 1

        standard_ns = False
    return predicate_translator
# translates the objects to generic objects
def object_to_generic_object(objects, namespace_translator, subject_translator, predicat_translator, all_ns):
    object_counter = 0
    object_translator = {}
    for obj_element in objects:
        # check if namespace standard namespace
        standard_ns = False
        for ns in all_ns:
            if (URIRef(obj_element) in Namespace(ns)) :
                standard_ns = True
                object_translator.update({obj_element: obj_element})
                break
        protocol = "http://" if ('http' in obj_element) else ""
        protocol = "urn:" if ('urn:' in obj_element) else protocol  
        if protocol != "" and not standard_ns:

            # check if URIRef is a known namespace
            is_namespace = False
            namespace_count = 0
            for element in namespace_translator:
                if URIRef(obj_element) in Namespace(element[0][1]):
                    is_namespace = True
                    break
                namespace_count += 1

            # check if URI is known subject
            translationValue = ''
            if obj_element in subject_translator:
                translationValue = subject_translator[obj_element]

            # check if URI is known subject
            elif obj_element in predicat_translator:
                translationValue = predicat_translator[obj_element]

            if translationValue != '':
                object_translator.update({obj_element: URIRef(translationValue)})
            # if URIRef is a known namespace translate it accordingly
            # if not translate it as normal URIRef
            elif is_namespace:
                new_string = str(namespace_translator[namespace_count][1][1] + 'Object' + str(object_counter))
                object_translator.update({obj_element: URIRef(new_string)})
            else:
                if '#' in obj_element:
                    object_translator.update({obj_element: URIRef(protocol + "anonym-obj-url.anon#Object" + str(object_counter))})
                else:
                    object_translator.update({obj_element: URIRef(protocol + "anonym-obj-url.anon/Object" + str(object_counter))})
        elif not standard_ns:
            if type(obj_element) == rdflib.Literal:
                if(obj_element.isdigit()):
                    object_translator.update({obj_element: obj_element})
                else: 
                    object_translator.update({obj_element: Literal("Object" + str(object_counter), datatype=obj_element.datatype, lang=obj_element.language)})
            #     object_translator.append([obj_element, obj_element])
            elif type(obj_element) == rdflib.BNode:
                object_translator.update({obj_element: BNode(obj_element)})
            else:
                object_translator.update({obj_element: obj_element})
        elif standard_ns and type(obj_element) == rdflib.term.Literal:
            object_translator.update({obj_element: Literal("Object" + str(object_counter), datatype=obj_element.datatype, lang=obj_element.language)})
        object_counter += 1
        standard_ns = False
    return object_translator


def change_graph(g: rdflib.Graph, subject_translator: dict, predicate_translator: dict, object_translator: dict)-> rdflib.Graph:
    """Removes the old triple and adds the anonymized triple to the graph

    Args:
        g (rdflib.Graph): The original graph with the non-translated values
        subject_translator (dict): a dict containing original and translated values for subjects
        predicate_translator (dict): a dict containing original and translated values for predicates
        object_translator (dict): a dict containing original and translated values for objects

    Returns:
        rdflib.Graph: the new, translated graph.
    """
    new_g = rdflib.Graph(store="SimpleMemory")
    for s, p, o in g:
        new_g.add((subject_translator[s], predicate_translator[p], object_translator[o]))
    return new_g