import subprocess

def run_get_sessions():
    """
    Runs the get_iterm2_sessions.py script as a subprocess.
    """
    try:
        result = subprocess.run(['python', 'src/utils/iterm2/get_iterm2_sessions.py'], capture_output=True, text=True)
        print(result.stdout)
        return result.stdout
        print("Errors:")
        print(result.stderr)
    except Exception as e:
        print(f"An error occurred: {e}")

# # Example usage
# if __name__ == "__main__":
#     run_get_sessions()