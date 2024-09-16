import sys
import io
import subprocess
import tempfile
import os

def exec_code(code, python_interpreter=None):
    code = "import os\n" + code

    if python_interpreter is None:
        python_executable = sys.executable  
    else:
        python_executable = python_interpreter

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
        tmp_file.write(code)
        tmp_filename = tmp_file.name

    try:
        result = subprocess.run(
            [python_executable, tmp_filename],
            capture_output=True,
            text=True,
            timeout=25 
        )

        if result.returncode != 0:
            output = result.stderr.strip()
        else:
            output = result.stdout.strip()
            if not output:
                output = "empty, add a print statement maybe to debug if needed! (don't use if __name__ == '__main__' as that might cause errors)"
        
        return {"output": output}
    
    except subprocess.TimeoutExpired:
        return {"output": "Execution timed out."}
    except Exception as e:
        return {"output": str(e)}
    finally:
        os.unlink(tmp_filename)

