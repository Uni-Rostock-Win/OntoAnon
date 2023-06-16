from tkinter import *
from tkinter import messagebox, simpledialog, commondialog, Toplevel
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfile
from rdflib.util import guess_format
import rdflib

import anonymization


# choosing the ontology file
def choose_open_file():
    filename = askopenfilename(title="Ontology File")
    onto_text.delete(0, END)
    onto_text.insert(0, filename)

# choosing where to store the anonymized ontology
def choose_anon_file():
        path = asksaveasfile(title="Anonymized File")
        anon_text.delete(0, END)
        anon_text.insert(0, path)
        start = "<_io.TextIOWrapper name='"
        end = "' mode='w' encoding='cp1252'>"
        filename = anon_filename.get()[anon_filename.get().find(start)+len(start):anon_filename.get().rfind(end)]
        anon_text.delete(0, END)
        anon_text.insert(0, filename)

# choosing where to store the dictionary file
def choose_dict_file():
        filename = asksaveasfile(title="Dictionary File")
        dict_text.delete(0, END)
        dict_text.insert(0, filename)
        start = "<_io.TextIOWrapper name='"
        end = "' mode='w' encoding='cp1252'>"
        filename = dict_filename.get()[dict_filename.get().find(start)+len(start):dict_filename.get().rfind(end)]
        dict_text.delete(0, END)
        dict_text.insert(0, filename)

def choose_namespaces():
    global SELECTED_NS
    values = [str(val) for val in anonymization.predefined_ns]
    values += [str(e) for e in SELECTED_NS if str(e) not in values]
    def add_value():
        global SELECTED_NS
        new_value = new_value_entry.get()
        if new_value:
            values.append(new_value)
            listbox.insert(tk.END, new_value) 
            listbox.selection_set(tk.END, tk.END)
            new_value_entry.delete(0, tk.END)
            SELECTED_NS.append(new_value)
        else:
            messagebox.showwarning("Warning", "Please enter a value.")

    def select_all():
        listbox.select_set(0, tk.END)

    def deselect_all():
        listbox.selection_clear(0, tk.END)

    def submit_selection():
        global SELECTED_NS
        SELECTED_NS = [listbox.get(index) for index in listbox.curselection()]
        predefinied_NS = [ns for ns in  anonymization.predefined_ns if str(ns) in SELECTED_NS]
        custom_NS = [rdflib.Namespace(ns) for ns in SELECTED_NS if ns not in predefinied_NS]
        SELECTED_NS = predefinied_NS + custom_NS
        root.destroy()

    
    root = tk.Tk()
    root.geometry("500x400")
    root.title("Value Selection")

    # Frame for the listbox and scrollbar
    frame = ttk.Frame(root)
    frame.pack(pady=2, padx=2, fill=tk.BOTH)

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Listbox
    listbox = tk.Listbox(frame, width=300, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)
    i = 0
    for value in values:
        listbox.insert(tk.END, value)
        if value in [str(element) for element in  SELECTED_NS]:
            listbox.select_set(tk.END, tk.END)
            # listbox.activate(tk.END)
            i += 1
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)
    scrollbar.config(command=listbox.yview)
    if len(SELECTED_NS) == 0:
        select_all()
    # Entry for adding new values
    new_value_entry = ttk.Entry(root)
    new_value_entry.pack(pady=5, fill=tk.X)

    # Buttons
    add_button = ttk.Button(root, text="Add Value", command=add_value)
    add_button.pack(fill=tk.X)
    select_all_button = ttk.Button(root, text="Select All", command=select_all)
    select_all_button.pack(fill=tk.X, pady=5)
    deselect_all_button = ttk.Button(root, text="Deselect All", command=deselect_all)
    deselect_all_button.pack(fill=tk.X)
    submit_button = ttk.Button(root, text="Submit", command=submit_selection)
    submit_button.pack(fill=tk.X, pady=10)

    root.mainloop()
    

# identifing the format of the ontology
def identify_file_format():
    try:
        format = guess_format(onto_filename.get())
        format_text.delete(0,END)
        format_text.insert(0,format)
    except Exception:
        format_text.delete(0,END)
        format_text.insert(0,'The file is missing, an url or not supported.')

# calling the anonymization method
def anonymize():
    global SELECTED_NS
    if len(SELECTED_NS) == 0:
        SELECTED_NS = anonymization.predefined_ns
    if (onto_filename.get() == "" or onto_format.get() == "" or anon_filename.get() == "" or dict_filename.get() == "" ):
        messagebox.showerror("Error", "Not all values set!")
    else:
        anonymization.anonymize(onto_filename.get(), onto_format.get(), anon_filename.get(), dict_filename.get(), SELECTED_NS)


if __name__ == '__main__':
    global SELECTED_NS
    if "SELECTED_NS" not in globals():
        SELECTED_NS = []
# Main window
    # create a window
    main_window = Tk()
    # set window title
    main_window.title("Ontology Anonymization Tool")
    # set window size
    main_window.geometry("550x260")
    # set minimum row size for row 0
    main_window.rowconfigure(0, {'minsize': 10})

    # variables to store the chosen filepaths and ontology format
    onto_filename = StringVar(main_window)
    onto_format = StringVar(main_window)
    anon_filename = StringVar(main_window)
    dict_filename = StringVar(main_window)

    # labels for the GUI
    Label(main_window, text="Select a local ontology file and a place to store the translation dictionary.", anchor='w',
          font=("Arial", 10)).grid(row=1, column=0, sticky="W", padx=10, columnspan=4)
    Label(main_window, text="Ontology File:", anchor='w', font=("Arial", 10)).grid(row=3, column=0, sticky="W", padx=10,
          columnspan=4)
    Label(main_window, text="Ontology Format:", anchor='w', font=("Arial", 10)).grid(row=5, column=0, sticky="W", padx=10,
          columnspan=4)
    Label(main_window, text="Anonymized File:", anchor='w', font=("Arial", 10)).grid(row=7, column=0, sticky="W", padx=10,
          columnspan=4)
    Label(main_window, text="Dictionary File:", anchor='w', font=("Arial", 10)).grid(row=9, column=0, sticky="W", padx=10,
          columnspan=4)

    # textfields for the GUI
    onto_text = Entry(main_window, font=("Arial", 10), textvariable=onto_filename)
    onto_text.grid(row=4, column=0, sticky=EW, padx=10, columnspan=5)
    format_text = Entry(main_window, font=("Arial", 10), textvariable=onto_format)
    format_text.grid(row=6, column=0, sticky=EW, padx=10, columnspan=5)
    anon_text = Entry(main_window, font=("Arial", 10), textvariable=anon_filename)
    anon_text.grid(row=8, column=0, sticky=EW, padx=10, columnspan=5)
    dict_text = Entry(main_window, font=("Arial", 10), textvariable=dict_filename)
    dict_text.grid(row=10, column=0, sticky=EW, padx=10, columnspan=5)

    # buttons for the GUI
    Button(main_window, text='Ontology File', command=choose_open_file).grid(row=2, column=0, padx=5, sticky=EW)
    Button(main_window, text='Identify Format', command=identify_file_format).grid(row=2, column=1, padx=5, sticky=EW)
    Button(main_window, text='Anonymized File', command=choose_anon_file).grid(row=2, column=2, padx=5, sticky=EW)
    Button(main_window, text='Dictionary File', command=choose_dict_file).grid(row=2, column=3, padx=5, sticky=EW)
    Button(main_window, text='Namespaces', command=choose_namespaces).grid(row=2, column=4, padx=5, sticky=EW)

    Button(main_window, text='Anonymize', command=anonymize).grid(row=11, column=0, padx=5, sticky=EW)

    # run window in loop
    main_window.mainloop()