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

from openai import OpenAI
from dotenv import load_dotenv
import json
import pyttsx3
import colorlog
from colorlog import ColoredFormatter

handler = colorlog.StreamHandler()
formatter = ColoredFormatter(
	"%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
	datefmt=None,
	reset=True,
	log_colors={
		'DEBUG':    'cyan',
		'INFO':     'green',
		'WARNING':  'yellow',
		'ERROR':    'red',
		'CRITICAL': 'red,bg_white',
	},
	secondary_log_colors={},
	style='%'
)
handler.setFormatter(formatter)
logger = colorlog.getLogger('example')
logger.addHandler(handler)

load_dotenv()

engine = pyttsx3.init()

def is_shutdown_request(prompt: str) -> bool:
    """
    Use OpenAI to determine if a prompt asks for shutdown or exit and return JSON true or false.

    Parameters:
        prompt (str): The input prompt from the user.

    Returns:
        str: JSON 'true' if the prompt is asking for shutdown or exit, 'false' otherwise.
    """
    client = OpenAI()
    messages=[
            {"role": "system", "content": "You are Nami. Determine if the user is asking you to stop or exit or shutdown or cancel yourself."},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "Respond with 'true' or 'false'."}
        ]
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )
    
    content = response.choices[0].message.content.strip().lower()

    if "true" in content:
        return True
    else:
        return False
    
def record_and_transcribe_plain_text():
    record_thread = threading.Thread(target=record_audio, args=("recorded.wav",))
    record_thread.start()
    record_thread.join()
    
    response = transcribe_audio("recorded.wav")
    return response

def print_and_speak(msg: str):
    global engine
    logger.info(msg)
    if not bool(os.getenv("TYPE_ONLY")):
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
        # is_correct = ask_yes_no_by_voice(prompt), commenting to skip one ask user check
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

if __name__ == "__main__":
    msg = is_shutdown_request("hey nami, cancel this command")
    print("x")
    print(msg)