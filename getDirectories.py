import json
from pathlib import Path

def get_directory_tree(path):
    """
    Recursively builds a nested dictionary representing the directory tree.
    Only includes directories (folders), ignoring files.
    """
    path_obj = Path(path)
    tree = {}
    
    try:
        # Iterate through everything in the current directory
        for item in path_obj.iterdir():
            # If it's a directory, add it to our tree and recurse
            if item.is_dir():
                tree[item.name] = get_directory_tree(item)
    except PermissionError:
        # Ignore folders that the system won't let us read
        pass
        
    return tree

if __name__ == "__main__":
    # Add the paths you want to scan here
    directories_to_scan = [
        "/Users/erickosterloh/ComputerScienceCourseWork",
        "/Users/erickosterloh/OtherSchoolWork",
        "/Users/erickosterloh/Misc",
        # Example using the current AgenticSorter project folder:
        # "/Users/erickosterloh/PersonalProjects/AgenticSorter"
    ]
    
    overall_tree = {}
    
    for directory in directories_to_scan:
        path_obj = Path(directory)
        
        if path_obj.exists() and path_obj.is_dir():
            print(f"Scanning: {path_obj.absolute()}...")
            # Store the result under the absolute path as the root key
            overall_tree[str(path_obj.absolute())] = get_directory_tree(path_obj)
        else:
            print(f"Warning: Directory not found or invalid: {directory}")

    # Print the resulting tree data structure as nicely formatted JSON
    print("\n=== Directory Tree ===")
    print(json.dumps(overall_tree, indent=4))

    # NOTE: You can now pass `overall_tree` to your LLM agent so it knows
    # exactly what folders exist without hallucinating!