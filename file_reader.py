from docx import Document
from PyPDF2 import PdfReader
import typing



def read_file_forLLM(filepath: str):
    """
    given a filepath, gets the extension, then calls the correct helper function that returns
    the first part of the file(depending on what extension it is) if it ends
    """
    split = filepath.split("/")
    filename = split[len(split)-1]
    ext = filename.split(".")


    if (ext[1] == ".txt" or ext[1] ==".md" or ext[1] ==".csv" or ext[1] ==".json" or ext[1] ==".py" or
     ext[1] ==".js"):
        return defaultopen(filepath)
    elif(ext[1] == ".pdf"):
        return pdfopen(filepath)
    elif(ext[1] == ".docx"):
        return docxopen(filepath)
    else:
        #just sort these off file names, at the end we will want to list this so that 
        # I can manually sort them.
        None

    


def defaultopen(filepath):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            print("Default is being inserted into context.")
            return content[0:1000]
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def pdfopen(filepath):
    file = PdfReader(filepath)
    page1 = file.pages[0]
    print("PDF is being inserted into context.")
    return page1.extract_text()


def docxopen(filepath):
    try:
        # Open the .docx file
        document = docx.Document(filename)
        
        full_text = []
        # Iterate through paragraphs to extract text
        for para in document.paragraphs:
            full_text.append(para.text)
            
        # Join paragraphs into a single string with newlines
        full_text_string = '\n'.join(full_text)
        
        # Use regex to find all "words" (sequences of alphanumeric characters)
        words = re.findall(r'\w+', full_text_string)
        
        # Get the first n words
        first_n_words_list = words[:n]
        
        # Join the words back into a string with spaces
        first_n_words_string = ' '.join(first_n_words_list)
        print("Docx is being inserted into context.")
        return first_n_words_string

    except FileNotFoundError:
        return f"Error: The file '{filename}' was not found."
    except Exception as e:
        return f"An error occurred: {e}"