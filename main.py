from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfile
from rdflib.util import guess_format

import anonymization, time

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
    if (onto_filename.get() == "" or onto_format.get() == "" or anon_filename.get() == "" or dict_filename.get() == "" ):
        messagebox.showerror("Error", "Not all values set!")
    else:
        anonymization.anonymize(onto_filename.get(), onto_format.get(), anon_filename.get(), dict_filename.get())


# Main window
if __name__ == '__main__':
    # create a window
    window = Tk()
    # set window title
    window.title("Ontology Anonymization Tool")
    # set window size
    window.geometry("450x260")
    # set minimum row size for row 0
    window.rowconfigure(0, {'minsize': 10})

    # variables to store the chosen filepaths and ontology format
    onto_filename = StringVar(window)
    onto_format = StringVar(window)
    anon_filename = StringVar(window)
    dict_filename = StringVar(window)

    # labels for the GUI
    Label(window, text="Select a local ontology file and a place to store the translation dictionary.", anchor='w',
          font=("Arial", 10)).grid(row=1, column=0, sticky="W", padx=10, columnspan=4)
    Label(window, text="Ontology File:", anchor='w', font=("Arial", 10)).grid(row=3, column=0, sticky="W", padx=10,
          columnspan=4)
    Label(window, text="Ontology Format:", anchor='w', font=("Arial", 10)).grid(row=5, column=0, sticky="W", padx=10,
          columnspan=4)
    Label(window, text="Anonymized File:", anchor='w', font=("Arial", 10)).grid(row=7, column=0, sticky="W", padx=10,
          columnspan=4)
    Label(window, text="Dictionary File:", anchor='w', font=("Arial", 10)).grid(row=9, column=0, sticky="W", padx=10,
          columnspan=4)

    # textfields for the GUI
    onto_text = Entry(window, font=("Arial", 10), textvariable=onto_filename)
    onto_text.grid(row=4, column=0, sticky=EW, padx=10, columnspan=4)
    format_text = Entry(window, font=("Arial", 10), textvariable=onto_format)
    format_text.grid(row=6, column=0, sticky=EW, padx=10, columnspan=4)
    anon_text = Entry(window, font=("Arial", 10), textvariable=anon_filename)
    anon_text.grid(row=8, column=0, sticky=EW, padx=10, columnspan=4)
    dict_text = Entry(window, font=("Arial", 10), textvariable=dict_filename)
    dict_text.grid(row=10, column=0, sticky=EW, padx=10, columnspan=4)

    # buttons for the GUI
    Button(window, text='Ontology File', command=choose_open_file).grid(row=2, column=0, padx=5, sticky=EW)
    Button(window, text='Identify Format', command=identify_file_format).grid(row=2, column=1, padx=5, sticky=EW)
    Button(window, text='Anonymized File', command=choose_anon_file).grid(row=2, column=2, padx=5, sticky=EW)
    Button(window, text='Dictionary File', command=choose_dict_file).grid(row=2, column=3, padx=5, sticky=EW)

    Button(window, text='Anonymize', command=anonymize).grid(row=11, column=0, padx=5, sticky=EW)

    # run window in loop
    window.mainloop()