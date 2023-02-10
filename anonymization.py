from tkinter import messagebox
from rdflib import Graph, Literal, URIRef

def anonymize(filename, fileformat, anony_path, dict_path):
    # Create a Graph
    g = Graph()

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
    namespace_to_generic_namespace(namespaces, namespace_translator)
    translator.extend(namespace_translator)
    print(namespace_translator)

    # translate the subjects
    subject_translator = []
    subject_to_generic_subject(subjects, subject_translator, namespace_translator)
    translator.extend(subject_translator)

    # translate the predicates
    predicat_translator = []
    predicat_to_generic_predicat(predicates, predicat_translator, namespace_translator)
    translator.extend(predicat_translator)

    # translate the objects
    object_translator = []
    object_to_generic_object(objects, object_translator, namespace_translator)
    translator.extend(object_translator)

    # Replaces the subjects, predicates and objects in the graph with the anonymized elements
    change_graph(g,subject_translator,predicat_translator,object_translator)

    # Saving the anonymized graph to the selected file
    new_graph = str(g.serialize(format=fileformat).decode('utf-8'))
    new_graph = new_graph[2:]
    new_graph = new_graph[:-3]

    with open(anony_path, 'w') as fp:
        fp.write(new_graph)

    # Saves the translation dictionary
    with open(dict_path, 'w') as fp:
        fp.write("\n".join(str(item) for item in translator))

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
    # print('namespaces: ')
    # print(namespaces)
    # print('subjects: ')
    # print(subjects)
    # print('predicates: ')
    # print(predicates)
    # print('objects: ')
    # print(objects)
    return namespaces, objects, predicates, subjects

# translates the namespaces to generic namespaces
def namespace_to_generic_namespace(namespaces, translator):
    name_counter = 0
    for name_element in namespaces:
        # check if namespace has an URL and translate it with an URIRef, otherwise it becomes a Literal
        if 'http' in name_element[1]:
            if '#' in name_element[1]:
                translator.append([name_element, ("Namespace" + str(name_counter),
                                                  URIRef(
                                                      "http://anonym-url.anon/Namespace" + str(name_counter) + "#"))])
            else:
                translator.append([name_element, ("Namespace" + str(name_counter),
                                                  URIRef("http://anonym-url.anon/Namespace" + str(name_counter) + "/"))])
        else:
            translator.append([name_element, Literal("Namespace" + str(name_counter))])
        name_counter = name_counter + 1

# translates the subjects to generic subjects
def subject_to_generic_subject(subjects, subject_translator, namespace_translator):
    subj_counter = 0
    for subj_element in subjects:

        # check if subject contains an URIRef, if not translate it as normal Literal
        if 'http' in subj_element:

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
                new_string = str(namespace_translator[namespace_count][1][1][:-1] + '/Subject' + str(subj_counter))
                subject_translator.append([subj_element, URIRef(new_string)])
            else:
                subject_translator.append([subj_element, URIRef("http://anonym-url.anon/Subject" + str(subj_counter))])
        else:
            subject_translator.append([subj_element, Literal("Subject" + str(subj_counter))])
        subj_counter = subj_counter + 1

# translates the predicates to generic predicates
def predicat_to_generic_predicat(predicates, predicat_translator, namespace_translator):
    predicat_counter = 0
    for pred_element in predicates:
        # check if predicate contains an URIRef, if not translate it as normal Literal
        if 'http' in pred_element:

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
                new_string = str(namespace_translator[namespace_count][1][1] + 'Predicate' + str(predicat_counter))
                predicat_translator.append([pred_element, URIRef(new_string)])
            else:
                predicat_translator.append([pred_element, URIRef("http://anonym-url.anon/Predicate" + str(predicat_counter))])
        else:
            predicat_translator.append([pred_element, Literal("Predicate" + str(predicat_counter))])
        predicat_counter = predicat_counter + 1

# translates the objects to generic objects
def object_to_generic_object(objects, object_translator, namespace_translator):
    object_counter = 0
    for obj_element in objects:

        # check if pbjecgs contains an URIRef, if not translate it as normal Literal
        if 'http' in obj_element:

            # check if URIRef is a known namespace
            is_namespace = False
            namespace_count = 0
            for element in namespace_translator:
                if element[0][1][:-1] in obj_element:
                    is_namespace = True
                    break
                namespace_count = namespace_count +1

            # if URIRef is a known namespace translate it accordingly
            # if not translate it as normal URIRef
            if is_namespace == True:
                new_string = str(namespace_translator[namespace_count][1][1] + 'Object' + str(object_counter))
                object_translator.append([obj_element, URIRef(new_string)])
            else:
                object_translator.append([obj_element, URIRef("http://anonym-url.anon/Object" + str(object_counter))])
        else:
            object_translator.append([obj_element, Literal("Object" + str(object_counter))])
        object_counter = object_counter + 1

# Removes the old triple and adds the anonymized triple to the graph
def change_graph(g,subject_translator,predicat_translator,object_translator):
    for subj in subject_translator:
        for pred in predicat_translator:
            for obj in object_translator:
                if (subj[0], pred[0], obj[0]) in g:
                    g.remove((subj[0], pred[0], obj[0]))
                    g.add((subj[1], pred[1], obj[1]))