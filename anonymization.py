from tkinter import messagebox

import rdflib
from rdflib import Graph, Literal, URIRef, BNode
from rdflib.namespace import Namespace


def anonymize(filename, fileformat, anony_path, dict_path):
    # Create a Graph
    g = Graph()
    all_ns = [ns for ns in rdflib.namespace._NAMESPACE_PREFIXES_RDFLIB.values()] + [str(ns) for ns in rdflib.namespace._NAMESPACE_PREFIXES_CORE.values()]

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

    translator = []

    # translate the namespaces
    namespace_translator = []
    namespace_to_generic_namespace(namespaces, namespace_translator, all_ns)
    translator.extend(namespace_translator)

    # translate the subjects
    subject_translator = []
    subject_to_generic_subject(subjects, subject_translator, namespace_translator, all_ns)
    translator.extend(subject_translator)

    # translate the predicates
    predicat_translator = []
    predicat_to_generic_predicat(predicates, predicat_translator, namespace_translator, subject_translator, all_ns)
    translator.extend(predicat_translator)

    # translate the objects
    object_translator = []
    object_to_generic_object(objects, object_translator, namespace_translator, subject_translator, predicat_translator, all_ns)
    translator.extend(object_translator)

    # Replaces the subjects, predicates and objects in the graph with the anonymized elements
    change_graph(g,subject_translator,predicat_translator,object_translator)

    # Saving the anonymized graph to the selected file
    #new_graph = g.serialize(format=fileformat)
    new_graph = g.serialize(format='xml')

    with open(anony_path, 'w') as fp:
        fp.write(new_graph)

    # Saves the translation dictionary
    outputTranslator = ""
    for item in translator:
        if type(item[0]) == rdflib.term.BNode or item[0] == item: continue
        else: outputTranslator += ("\n" + str(item[0]) + " => " + str(item[1]))
    with open(dict_path, 'w') as fp:
        fp.write(outputTranslator)

    # Showing a message that the process is finished.
    messagebox.showinfo("System-Message", "Anonymization is finished.")

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
        if (subj, pred, obj) not in g:
            raise Exception("It better be!")

    # delete doubles
    namespaces = list(dict.fromkeys(namespaces))
    subjects = list(dict.fromkeys(subjects))
    predicates = list(dict.fromkeys(predicates))
    objects = list(dict.fromkeys(objects))

    # controll results while development
    #print('namespaces: ')
    #print(namespaces)
    #print('subjects: ')
    #print(subjects)
    #print('predicates: ')
    #print(predicates)
    #print('objects: ')
    #print(objects)
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
def subject_to_generic_subject(subjects, subject_translator, namespace_translator, all_ns):
    subj_counter = 0
    standard_ns = False
    for subj_element in subjects:
        #check if namespace standard namespace
        for ns in all_ns:
            if (URIRef(subj_element) in Namespace(ns)) :
                standard_ns = True
                subject_translator.append([subj_element, subj_element])

        # check if subject contains an URIRef, if not translate it as normal Literal
        if ('http' in subj_element) and (standard_ns == False):

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
            if is_namespace == True:
                new_string = str(namespace_translator[namespace_count][1][1] + 'Subject' + str(subj_counter))
                subject_translator.append([subj_element, URIRef(new_string)])
            else:
                if '#' in subj_element:
                    subject_translator.append([subj_element, URIRef("http://anonym-subj-url.anon#Subject" + str(subj_counter))])
                else:
                    subject_translator.append([subj_element, URIRef("http://anonym-subj-url.anon/Subject" + str(subj_counter))])
        elif standard_ns == False:
            if '_:' in subj_element.n3():
                subject_translator.append([subj_element, BNode(subj_element)])
            else:
                subject_translator.append([subj_element, Literal("Subject" + str(subj_counter), datatype=subj_element.datatype, lang=subj_element.language)])
        subj_counter = subj_counter + 1

        standard_ns = False

# translates the predicates to generic predicates
def predicat_to_generic_predicat(predicates, predicat_translator, namespace_translator, subject_translator, all_ns):
    predicat_counter = 0
    standard_ns = False
    for pred_element in predicates:
        # check if namespace standard namespace
        for ns in all_ns:
            if (URIRef(pred_element) in Namespace(ns)) :
                standard_ns = True
                predicat_translator.append([pred_element, pred_element])

        if ('http' in pred_element) and (standard_ns == False):
            # check if URIRef is a known namespace
            is_namespace = False
            namespace_count = 0
            for element in namespace_translator:
                if element[0][1][:-1] in pred_element:
                    is_namespace = True
                    break
                namespace_count = namespace_count +1

            # if URIRef is a known namespace translate it accordingly
            # if not translate it as normal URIRef
            if is_namespace == True:

                # check if URI is known subject
                is_subject = False
                subject_value = ''
                for element in subject_translator:
                    if pred_element == element[0]:
                        is_subject = True
                        subject_value = element[1]

                if is_subject == True:
                    predicat_translator.append([pred_element, URIRef(subject_value)])
                else:
                    new_string = str(namespace_translator[namespace_count][1][1] + 'Predicate' + str(predicat_counter))
                    predicat_translator.append([pred_element, URIRef(new_string)])
            else:
                if '#' in pred_element:
                    predicat_translator.append([pred_element, URIRef("http://anonym-pred-url.anon#Predicate" + str(predicat_counter))])
                else:
                    predicat_translator.append([pred_element, URIRef("http://anonym-pred-url.anon/Predicate" + str(predicat_counter))])
        elif standard_ns == False:
            predicat_translator.append([pred_element, Literal("Predicate" + str(predicat_counter))])
        predicat_counter = predicat_counter + 1

        standard_ns = False

# translates the objects to generic objects
def object_to_generic_object(objects, object_translator, namespace_translator, subject_translator, predicat_translator, all_ns):
    object_counter = 0

    for obj_element in objects:
        # check if namespace standard namespace
        standard_ns = False
        for ns in all_ns:
            if (URIRef(obj_element) in Namespace(ns)) :
                standard_ns = True
                object_translator.append([obj_element, obj_element])
                break

        if ('http' in obj_element) and (standard_ns == False):

            # check if URIRef is a known namespace
            is_namespace = False
            namespace_count = 0
            for element in namespace_translator:
                if URIRef(obj_element) in Namespace(element[0][1]):
                    is_namespace = True
                    break
                namespace_count = namespace_count +1

            # if URIRef is a known namespace translate it accordingly
            # if not translate it as normal URIRef
            if is_namespace == True:

                # check if URI is known subject
                is_subject = False
                subject_value = ''
                for element in subject_translator:
                    if obj_element == element[0]:
                        is_subject = True
                        subject_value = element[1]

                # check if URI is known subject
                is_predicat = False
                predicate_value = ''
                for element in predicat_translator:
                    if obj_element == element[0]:
                        is_predicat = True
                        is_subject = False
                        predicate_value = element[1]

                if is_subject == True:
                    object_translator.append([obj_element, URIRef(subject_value)])
                elif is_predicat == True:
                    object_translator.append([obj_element, URIRef(predicate_value)])
                else:
                    new_string = str(namespace_translator[namespace_count][1][1] + 'Object' + str(object_counter))
                    object_translator.append([obj_element, URIRef(new_string)])
            else:
                if '#' in obj_element:
                    object_translator.append([obj_element, URIRef("http://anonym-obj-url.anon#Object" + str(object_counter))])
                else:
                    object_translator.append([obj_element, URIRef("http://anonym-obj-url.anon/Object" + str(object_counter))])
        elif standard_ns == False:
            if '"' in obj_element.n3() and '<' in obj_element.n3() and type(obj_element) != rdflib.Literal:
                print("test")
            if type(obj_element) == rdflib.Literal:
                if(obj_element.isdigit()):
                    object_translator.append([obj_element, obj_element])
                else: 
                    object_translator.append([obj_element, Literal("Object" + str(object_counter), datatype=obj_element.datatype, lang=obj_element.language)])
            #     object_translator.append([obj_element, obj_element])
            elif type(obj_element) == rdflib.BNode:
                object_translator.append([obj_element, BNode(obj_element)])
            else:
                object_translator.append([obj_element, obj_element])
        elif standard_ns == True and type(obj_element) == rdflib.term.Literal:
            object_translator.append([obj_element, Literal("Object" + str(object_counter), datatype=obj_element.datatype, lang=obj_element.language)])
        object_counter = object_counter + 1

        standard_ns = False

# Removes the old triple and adds the anonymized triple to the graph
def change_graph(g,subject_translator,predicat_translator,object_translator):
    for subj in subject_translator:
        for pred in predicat_translator:
            for obj in object_translator:
                if (subj[0], pred[0], obj[0]) in g:
                    g.remove((subj[0], pred[0], obj[0]))
                    g.add((subj[1], pred[1], obj[1]))
