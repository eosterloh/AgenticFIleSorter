import shutil
import json
import time
from pathlib import Path
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from langchain_ollama import ChatOllama
from getDirectories import get_directory_tree

from file_reader import read_file_forLLM
import argparse
## Two phases really, need everything to move at the beginning, and then we have to move whenever something
##detected. Lets do something like, on run, move everything not sorted into a good folder, then, wait
## for something to be added and then move it.

def move_file(srcfile: str, destination: str):
    """
    Moves a file into the correct sorted directory.
    
    Args:
        srcfile: The absolute path of the file to be moved.
        destination: The absolute path of the directory to put the file in.
    """
    try:
        dest_path = Path(destination)
        # Ensure destination exists
        dest_path.mkdir(parents=True, exist_ok=True)
        
        print(f"Agent moving: {srcfile} -> {destination}")
        shutil.move(srcfile, destination)
        return f"Successfully moved to {destination}"
    except Exception as e:
        print(f"Error moving file {srcfile}: {e}")
        return f"Failed to move file: {e}"
    
def make_new_dir(path: str, newname: str):
    """
    Creates a new folder when sorting if a suitable one doesn't exist.

    Args:
        path: The absolute path/directory that the new directory should be created inside.
        newname: The name of the new directory.
    """
    try:
        newpath = Path(path) / newname
        newpath.mkdir(parents=True, exist_ok=True)
        print(f"Agent created directory: {newpath}")
        return f"Successfully created directory {newpath}"
    except Exception as e:
        print(f"Error creating directory {newname} at {path}: {e}")
        return f"Failed to create directory: {e}"


model = ChatOllama(model="llama3.1:8b", temperature=0)
llm_with_tools = model.bind_tools([move_file, make_new_dir], tool_choice="any")

def get_system_prompt(filepath):
    directories_to_scan = [
        "/Users/erickosterloh/ComputerScienceCourseWork",
        "/Users/erickosterloh/OtherSchoolWork",
        "/Users/erickosterloh/Misc"
    ]
    
    current_tree = {}
    for directory in directories_to_scan:
        path_obj = Path(directory)
        if path_obj.exists() and path_obj.is_dir():
            current_tree[str(path_obj.absolute())] = get_directory_tree(path_obj)
            
    tree_json = json.dumps(current_tree, indent=2)


    fp = filepath
    filename = filepath.split("/")[-1]
    filecontent = read_file_forLLM(filepath)

    return (
        "system", 
        f"""You are an autonomous file-sorting agent. Your job is to organize my files into the correct directories based on their context and file type.

### DIRECTORY RULES
Base Directory: /Users/erickosterloh

1. RESTRICTED DIRECTORIES (DO NOT TOUCH OR MOVE FILES FROM HERE):
   - /Users/erickosterloh/Applications
   - /Users/erickosterloh/Movies
   - /Users/erickosterloh/Pictures
   - /Users/erickosterloh/go
   - /Users/erickosterloh/Public
   - /Users/erickosterloh/node_modules
   - /Users/erickosterloh/PersonalProjects

2. SOURCE DIRECTORIES (Move unsorted files AWAY from these):
   - /Users/erickosterloh/Documents
   - /Users/erickosterloh/Downloads
   - /Users/erickosterloh/Desktop

3. TARGET DIRECTORIES (Where files should be moved TO):
   - /Users/erickosterloh/ComputerScienceCourseWork
   - /Users/erickosterloh/OtherSchoolWork
   - /Users/erickosterloh/Misc

### CURRENT FOLDER STRUCTURE
Here is the current nested directory structure of your Target Directories. Use this to determine if a suitable folder already exists before creating a new one:

{tree_json}

### FILE CONTENT OR NAME
#### PATH

{fp}

#### NAME

{filename}

#### CONTENT(if it cannot be ingested filecontent will be None)
{filecontent}


### YOUR TASKS
When you receive a file path from the user, you must decide where it belongs. 
- You should dynamically categorize files by creating specific sub-folders inside the Target Directories (e.g., moving a syllabus to a "Fall_2024" folder inside "OtherSchoolWork").
- If a suitable sub-folder does not exist, you must call the `make_new_dir` tool FIRST before calling the `move_file` tool.
- CRITICAL INSTRUCTION: You are a programmatic script. You do not have the ability to talk to the user. You MUST output a tool call to either `move_file` or `make_new_dir`. Even if the file has no content, use the filename to make your best guess and call a tool. Do NOT return conversational text.
"""
)

class BehindTheScenesSorter(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        # Cache to store recently processed files and prevent duplicate runs
        self.processed_files = {}
        self.cooldown_seconds = 5 # Ignore events for the same file for 5 seconds

    def on_created(self, event: FileSystemEvent) -> None:
        """
        Overriding only the on_created class to avoid moving stuff that I purposely move
        back to the folder.
        """
        
        if getattr(event, 'is_directory', False):
            return
        
        src_path = Path(event.src_path) #makes a new path
        if not src_path.is_file(): # This is a neccessary double check to prevent error printing
            return
            
        # Ignore hidden/temporary files created by browsers while downloading
        if src_path.name.startswith('.') or src_path.name.endswith('.crdownload') or src_path.name.endswith('.part'):
            return

        # Check our cooldown cache
        current_time = time.time()
        file_key = str(src_path.absolute())
        
        if file_key in self.processed_files:
            if current_time - self.processed_files[file_key] < self.cooldown_seconds:
                # We saw this file recently, ignore this duplicate event
                return
                
        # Record this file as being processed right now
        self.processed_files[file_key] = current_time

        ##Alright now lets add ollama capatbilities. have it choose src_path 1 if some
        # it is a CS related title

        if ("/Users/erickosterloh/Documents" in event.src_path or 
            "/Users/erickosterloh/Downloads" in event.src_path or 
            "/Users/erickosterloh/Desktop" in event.src_path):
        ## When an event happens in any of these three directories, these steps should happen
        ## First the event gets identified, we should then send it to the agent
        ## The agent will be given the event, along with the current file structure in that 
        ## Area, and make a desicion on where to put the file, calling movefile or make directory
        ## If need be
            system_prompt_text = get_system_prompt(event.src_path)
            print(f"Processing new file: {event.src_path}")
            # print(system_prompt_text)
            messages = [
                system_prompt_text,
                ("user", f"Please sort this file: {event.src_path}")
            ]

            print("thinking deep thoughts...")
            ai_msg = llm_with_tools.invoke(messages)
            
            # Print the text response if it decided to chat anyway
            if ai_msg.content:
                print(f"Agent Thoughts: {ai_msg.content}")

            for tool_call in ai_msg.tool_calls:
                # Extract the tool name and arguments chosen by the LLM
                selected_tool = tool_call["name"]
                tool_args = tool_call["args"]
                
                # Execute the corresponding python function
                if selected_tool == "make_new_dir":
                    make_new_dir(**tool_args)
                elif selected_tool == "move_file":
                    move_file(**tool_args)
            print("Great success!")
    ### Thought about using on moved, but this would make it so that we could move files back
    # while running


def passiveSort():
    """Observer function, 
    when activated, calls a chunk of code that runs the agent until the Downloads directory is empty
    we only care about the Downloads as thats where 99% of my files go to.
    """
    event_handler = BehindTheScenesSorter()
    observer = Observer()
    observer.schedule(event_handler, "/Users/erickosterloh/.", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()




def startupSort():
    """
    Runs when file sortagent.py is ran on python, sorts everything out of downloads and into the right spot.
    """
    docs_path = Path("/Users/erickosterloh/Documents")
    downloads_path = Path("/Users/erickosterloh/Downloads")
    desktop_path = Path("/Users/erickosterloh/Desktop")
    directpaths = [docs_path, downloads_path, desktop_path]
    
    for path in directpaths:
        if not path.exists():
            continue
            
        for file_path in path.rglob('*'):
            # Check if the entry is a file (and not a directory)
            if file_path.is_file():
                # Ignore hidden/temporary files
                if file_path.name.startswith('.') or file_path.name.endswith('.crdownload') or file_path.name.endswith('.part'):
                    continue
                    
                abs_path = str(file_path.absolute())
                system_prompt_text = get_system_prompt(abs_path)
                
                print(f"Processing existing file: {abs_path}")
                messages = [
                    system_prompt_text,
                    ("user", f"Please sort this file: {abs_path}")
                ]

                print("thinking deep thoughts...")
                ai_msg = llm_with_tools.invoke(messages)
                
                # Print the text response if it decided to chat anyway
                if ai_msg.content:
                    print(f"Agent Thoughts: {ai_msg.content}")

                for tool_call in ai_msg.tool_calls:
                    # Extract the tool name and arguments chosen by the LLM
                    selected_tool = tool_call["name"]
                    tool_args = tool_call["args"]
                    
                    # Execute the corresponding python function
                    if selected_tool == "make_new_dir":
                        make_new_dir(**tool_args)
                    elif selected_tool == "move_file":
                        move_file(**tool_args)
                print("Great success!")





def main():
    # 1. Create the ArgumentParser object with a description
    parser = argparse.ArgumentParser(description="script for doing agentic sorting of my file system")

    # 2. Add arguments
    parser.add_argument("--passive", action="store_true", help="use to run passive sort")
    parser.add_argument("--startup", action="store_true", help="use to run a one-time startup sort of existing files")

    # 3. Parse the arguments
    args = parser.parse_args()

    # 4. Access and use the arguments
    if args.startup:
        startupSort()
    if args.passive:
        passiveSort()
        

if __name__ == "__main__":
    main()