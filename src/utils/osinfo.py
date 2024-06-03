import subprocess
import platform
import json

def get_python_version():
    try:
        result = subprocess.run(['python', '--version'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Failed to get Python version: {e}"

def get_conda_version():
    try:
        result = subprocess.run(['conda', '--version'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Failed to get Conda version: {e}"

def get_os_version():
    try:
        os_info = platform.uname()
        return {
            "system": os_info.system,
            "machine": os_info.machine,
        }
    except Exception as e:
        return f"Failed to get OS version: {e}"

def get_details():
    info = {
        "Python Version": get_python_version(),
        "Conda Version": get_conda_version(),
        "OS Version": get_os_version()
    }
    
    return json.dumps(info)
