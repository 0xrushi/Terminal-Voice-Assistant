import argparse
import os
import wave
from datetime import datetime
import threading
import pyaudio
import keyboard
from openai import OpenAI
import pvporcupine
from pvrecorder import PvRecorder
from dotenv import load_dotenv
import pyttsx3
import sounddevice as sd
import pyautogui
import time
import pyperclip
import subprocess

from PyQt5.QtCore import QTimer
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QMovie, QPalette, QColor
from PyQt5.QtCore import Qt, QSize

from src.chains.bash_chain import bash_chain
from src.chains.bash_chain.ask_user_yes_no_get_reason import ask_user_yes_no_get_reason
from src.utils.chrmadb.generate_db import get_relevant_history
from src.utils.subprocess_caller import get_command_logs
from src.utils.helpers import print_and_speak, record_and_transcribe_plain_text, transcribe_audio, record_audio
# from src.animation import animation_controller
# from src.animation.thinking_siri_animation import GIFPlayer

load_dotenv()
engine = pyttsx3.init()
transcription = ""
TAB_INDEX2=2
resp = {
    "reason": None
}

        

def wake_word_detection(access_key, keyword_paths, audio_device_index=-1):
    """
    Detects a wake word in the audio stream from the specified audio device.

    Args:
        access_key (str): The access key for the Porcupine service.
        keyword_paths (List[str]): The paths to the keyword model files.
        audio_device_index (int, optional): The index of the audio device to use. Defaults to -1.

    Returns:
        bool: True if a wake word is detected, False otherwise.

    Raises:
        Exception: If an error occurs during the wake word detection process.
    """
    try:
        # Create Porcupine object
        porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=keyword_paths)

        # Initialize PvRecorder
        recorder = PvRecorder(frame_length=porcupine.frame_length, device_index=audio_device_index)
        recorder.start()

        print('Listening for wake word... (press Ctrl+C to exit)')
        while True:
            pcm = recorder.read()
            result = porcupine.process(pcm)
            if result >= 0:
                print('[%s] Wake word detected!' % str(datetime.now()))
                recorder.stop()
                return True
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'recorder' in locals():
            recorder.delete()
        if 'porcupine' in locals():
            porcupine.delete()
        
def ask_yes_no_by_voice(prompt):
    """
    Asks a yes/no question via voice and expects a vocal response. The response is recorded and transcribed to determine if the answer is 'yes' or 'no'.

    Args:
        prompt (str): The question to ask the user via text-to-speech.

    Returns:
        bool: True if the user responded with 'yes', False if 'no', and None if unclear.
    """
    client = OpenAI()

    print_and_speak(prompt)

    filename = "confirmation.wav"
    record_audio(filename)

    with open(filename, "rb") as audio_file:
        confirmation = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        response_text = confirmation.text.lower().strip()
        print("Transcribed confirmation:", response_text)

    # Determine the user's response based on transcription
    if "yes" in response_text:
        return True
    elif "no" or "não" in response_text:
        return False
    elif "stop" in response_text:
        return "STOP"
    else:
        return None
    
def type_text(text):
    try:
        # pane id indexing starts at 0
        # command = f'source ~/.zshrc && echo -e "\\n{text}\\n" | wezterm cli send-text --pane-id 1 --no-paste'
        command = f'source ~/.zshrc && echo -e "\\n{text}\\n" | wezterm cli send-text --pane-id 1 --no-paste > /tmp/wezterm_output.txt 2>&1'
        subprocess.run(['zsh', '-c', command], check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while sending text: {e}")
    except Exception as e:
        print(f"Unexpected error occurred while sending text: {e}")
        
# def switch_tab(ind):
#     if not ind:
#         raise ValueError("This switch tab index is empty")
#     time.sleep(0.3)
#     pyautogui.keyDown('alt')
#     pyautogui.press(str(ind))
#     pyautogui.keyUp('alt')
#     time.sleep(0.3)
    
def run_command(command: str):
    time.sleep(0.5)
    cwd = os.getcwd()
    type_text(command)
    time.sleep(0.5)
    
def replace_quotes(text):
    bad_double_quotes = ['“', '”', '„']
    bad_single_quotes = ['‘', '’']

    for bad_double in bad_double_quotes:
        text = text.replace(bad_double, '"')
    
    for bad_single in bad_single_quotes:
        text = text.replace(bad_single, "'")
    
    return text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--keyword_paths', nargs='+', required=True, help='Absolute paths to keyword model files')
    parser.add_argument('--audio_device_index', type=int, default=-1)
    parser.add_argument('--show_audio_devices', action='store_true')
    
    args = parser.parse_args()
    global resp
    
    if args.show_audio_devices:
        for i, device in enumerate(PvRecorder.get_available_devices()):
            print('Device %d: %s' % (i, device))
        return
    
    access_key = os.getenv("PICOVOICE_ACCESS_KEY")
    # if wake_word_detection(access_key, args.keyword_paths, 1):
    if True:
        message_ok = False
        # show animation
        process = subprocess.Popen(['python', 'src/animation/thinking_siri_animation.py'])
        is_first_run = True
        clean_command = ''
        while not message_ok:
            print(f"---\n{resp}\n{resp.get('reason')}")
            if resp.get("reason")is None:
                # Record audio in a separate thread
                if False:
                    command = record_and_transcribe_plain_text()
                else:
                    command = input("enter command: ")
                
                command = clean_command + "\n\n" + command
            
            else:
                command = clean_command + "\n\n" + resp.get("reason")
                
            if is_first_run:
                historical_commands_from_rag = get_relevant_history(command)
            # uncomment this to enable openai instead of open interpreter
            # message, clean_command = bash_chain.run(command, historical_commands_from_rag)
            message, clean_command = bash_chain.run_openinterpreter(command, historical_commands_from_rag)
            clean_command = replace_quotes(clean_command)
            print(clean_command)
            message_ok = message=="ok"
            
            # should i run it
            command_success = ask_yes_no_by_voice(message)
            
            if command_success == True:
                run_command(clean_command)
                
                # ask_confirm = ask_yes_no_by_voice(msg)
                resp = ask_user_yes_no_get_reason()
                print("line 206 received resp", resp)
                if resp.get("exit") == True and resp.get("response")=="yes" and resp.get("reason")==None:
                    print_and_speak(resp.get("your_next_message"))
                    message_ok = False
                elif (resp.get("response")=="yes" and resp.get("reason")is not None) or (resp.get("response")=="no"):
                    message_ok = True
                    
        process.terminate()
        process.wait()

if __name__ == '__main__':
    # run_command(f"script -a {os.getcwd()}/command_logs.txt")
    while True:
        main()    
    run_command("exit")
    # sys.exit(app.exec_())