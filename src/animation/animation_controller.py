import subprocess
import time

process = subprocess.Popen(['python', 'src/animation/thinking_siri_animation.py'])

# Wait for 5 seconds
time.sleep(5)

process.terminate()
process.wait()