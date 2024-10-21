import sys
import subprocess
import shlex


def exec_code(code, python_interpreter=None):
    code = "import os\n" + code

    if python_interpreter is None:
        python_executable = sys.executable
    else:
        python_executable = python_interpreter

    command = [python_executable, "-c", code]

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=85)

        if result.returncode != 0:
            output = result.stderr.strip()
            error = True
        else:
            output = result.stdout.strip()
            error = False
            if not output:
                output = "empty, add a print statement maybe to debug if needed! (don't use if __name__ == '__main__' as that might cause errors). You dont have to write code again if you think no print statements are expected."
                error = False

        return {"output": output, "error": error}

    except subprocess.TimeoutExpired:
        return {"output": "Execution timed out.", "error": True}
    except Exception as e:
        return {"output": str(e), "error": True}
