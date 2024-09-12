import sys
import io
import requests

def exec_code(code):
    output = io.StringIO()
    original_stdout = sys.stdout
    namespace = {}
    
    try:
        sys.stdout = output
        exec(code, namespace,namespace)  
    except Exception as e:
        return {"output": f"{e}"}
    finally:
        sys.stdout = original_stdout
    
    result = output.getvalue()
    if result == "":
        result = "empty, add a print statement maybe to debug if needed!"
    
    return {"output": result}

