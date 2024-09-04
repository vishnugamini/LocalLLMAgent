import sys
import io

def exec_code(code):
    code = "import os\n" + code
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
        result = "empty, add a print statement maybe to debug!"
    
    return {"output": result}

