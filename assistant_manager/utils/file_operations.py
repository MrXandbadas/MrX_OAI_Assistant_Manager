## Staple functions to use in the chat
import json

def write_file(file_name, content):
    with open(file_name, 'w') as f:
        f.write(content)
    return None

def read_file(file_name):
    with open(file_name, 'r') as f:
        return f.read()
    
def save_json(file_name, data):
    """
    Saves a JSON file.

    Args:
        file_name (str): The name of the file to save.
        data (dict): The data to save.

    Returns:
        None
    """
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)


    

def read_json(file_name):
    """
    Reads a JSON file.

    Args:
        file_name (str): The name of the file to read.

    Returns:
        dict: The data from the file.
    """
    try:
        with open(file_name) as json_file:
            data = json.load(json_file)
            return data
    except FileNotFoundError:
        return {}
    
from IPython import get_ipython



def exec_python(cell):
    ipython = get_ipython()
    if ipython is None:
        #hotfix for Mac M1
        from IPython.terminal.embed import InteractiveShellEmbed
        ipython = InteractiveShellEmbed()
    result = ipython.run_cell(cell)
    log = str(result.result)
    if result.error_before_exec is not None:
        log += f"\n{result.error_before_exec}"
    if result.error_in_exec is not None:
        log += f"\n{result.error_in_exec}"

    #Check the logs length
    if len(log) > 1000:
        log = log[:1000]
        log += "\n\n... truncated"
    return log

import subprocess
def exec_sh(script):
    #Mac M1, we just want to run .sh files that are made in a temp folder
    #and then deleted

    #create a temp folder if it doesn't exist
    import os
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    #write the script to a file
    file_name = "tmp/tmp.sh"
    write_file(file_name, script)
    #make it executable
    subprocess.run(["chmod", "u+x", file_name])
    #run it
    result = subprocess.run([file_name], stdout=subprocess.PIPE)
    #delete it
    os.remove(file_name)
    #return the output
    return result.stdout.decode("utf-8")
