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

from src.chains import bash_chain
from src.utils.chrmadb.generate_db import get_relevant_history
from src.utils.subprocess_caller import get_command_logs
# from src.animation import animation_controller
# from src.animation.thinking_siri_animation import GIFPlayer

load_dotenv()
engine = pyttsx3.init()
transcription = ""
TAB_INDEX2=2

def print_and_speak(msg: str): 
    print(msg)
    engine.say(msg)
    engine.runAndWait()

def record_audio(filename, sample_rate=16000, chunk_size=512, channels=1, device_id=None):
    """
    Records audio from the default microphone input until the 'esc' key is pressed. 
    The audio is recorded in WAV format and saved to the specified file.

    Args:
    filename (str): The path to the file where the recorded audio will be saved.
        The file extension should be .wav to indicate the format.
    sample_rate (int): The sample rate of the audio recording in Hertz. 
        Common rates include 44100 (CD), 48000 (audio for video), and 16000 (telephony). Default is 16000.
    chunk_size (int): The number of audio frames per buffer. A larger size reduces CPU usage but increases latency.
        Default is 512.
    channels (int): The number of audio channels (1 for mono, 2 for stereo). Default is 1 (mono).
    device_id (int, optional): The ID of the audio input device to use. Default is None, which uses the default device.
    """
    p = pyaudio.PyAudio()
    
    if device_id is None:
        device_id = p.get_default_input_device_info()['index']
        
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    input_device_index=device_id,
                    frames_per_buffer=chunk_size)
    
    frames = []
    print("Recording... (press 'esc' to stop)")

    recording = True
    def stop_recording():
        nonlocal recording
        recording = False

    keyboard.add_hotkey('esc', stop_recording, suppress=True)
    
    try:
        while recording:
            data = stream.read(chunk_size, exception_on_overflow=False)
            frames.append(data)
    finally:
        print("Recording stopped.")
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save the recorded data as a WAV file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        keyboard.unhook_all_hotkeys()

def transcribe_audio(filename):
    """
    Transcribes the audio file specified by the given filename using the OpenAI API.

    Args:
        filename (str): The path to the audio file to be transcribed.

    Returns:
        transcription (str): The transcription of the audio file.
    """
    
    client = OpenAI()
    couldnt_understand = False
    global transcription
    while True:
        is_correct = None
        if not couldnt_understand:
            with open(filename, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
                print(transcription.text)

        prompt = "Is this transcription correct?." if not couldnt_understand else ""
        # is_correct = ask_yes_no_by_voice(prompt)
        is_correct = True
            
        if is_correct:
            return transcription.text
        elif is_correct is False:
            couldnt_understand = False
            msg = "Let's try recording the main command again."
            print_and_speak(msg)
            record_audio(filename)
        else:
            msg = "I couldn't understand. Please say 'yes' or 'no' clearly. "
            print_and_speak(msg)
            couldnt_understand = True
            
def wake_word_detection1(access_key, keyword_paths, audio_device_index=-1):
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

    Notes:
        - This function creates a Porcupine object using the provided access key and keyword paths.
        - It initializes a PvRecorder object with the frame length of the Porcupine object and the specified audio device index.
        - The function enters a loop to continuously read audio frames from the recorder and process them using Porcupine.
        - If a wake word is detected, the function stops the recorder and returns True.
        - If an error occurs, the function prints the error message and continues.
        - Finally, the function deletes the recorder and Porcupine objects.
    """
    try:
        porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=keyword_paths)

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
        print(str(e))
    finally:
        recorder.delete()
        porcupine.delete()
        

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
    pyautogui.write(text, interval=0.1)

def switch_tab(ind):
    if not ind:
        raise ValueError("This switch tab index is empty")
    time.sleep(0.3)
    pyautogui.keyDown('alt')
    pyautogui.press(str(ind))
    pyautogui.keyUp('alt')
    time.sleep(0.3)
    
def run_command(command: str):
    time.sleep(1)
    switch_tab(TAB_INDEX2)
    cwd = os.getcwd()
    pyautogui.press('enter')
    pyautogui.press('enter')
    # type_text(f"cd {cwd}")
    # pyautogui.press('enter')
    type_text(command)
    pyautogui.press('enter')
    time.sleep(1)
    
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
    
    if args.show_audio_devices:
        for i, device in enumerate(PvRecorder.get_available_devices()):
            print('Device %d: %s' % (i, device))
        return
    
    access_key = os.getenv("PICOVOICE_ACCESS_KEY")
    if wake_word_detection(access_key, args.keyword_paths, 1):
        message_ok = False
        
        # show animation
        process = subprocess.Popen(['python', 'src/animation/thinking_siri_animation.py'])
        his = "Command: "
        is_first_run = True
        clean_command = ''
        while not message_ok:
            # Record audio in a separate thread
            record_thread = threading.Thread(target=record_audio, args=("recorded.wav",))
            record_thread.start()
            record_thread.join()
            
            command = transcribe_audio("recorded.wav")
            
            command = clean_command + "\n\n" + command
                
            if is_first_run:
                historical_commands_from_rag = get_relevant_history(command)
                his + command + "\n"
            message, clean_command = bash_chain.run(command, historical_commands_from_rag)
            clean_command = replace_quotes(clean_command)
            print(clean_command)
            message_ok = message=="ok"
            
            command_success = ask_yes_no_by_voice(message)
            
            if command_success == True:
                run_command(clean_command)
                
                msg = "Did that work?"
                ask_confirm = ask_yes_no_by_voice(msg)
                if ask_confirm == True:
                    message_ok = True
                if ask_confirm == False:
                    print_and_speak("Lets try modifying the command again.")
                    message_ok = False
                    
        process.terminate()
        process.wait()

if __name__ == '__main__':
    run_command(f"script -a {os.getcwd()}/command_logs.txt")
    while True:
        main()    
    run_command("exit")
    sys.exit(app.exec_())