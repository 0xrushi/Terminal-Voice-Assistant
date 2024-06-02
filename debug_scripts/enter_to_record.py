import pyaudio
import wave
import keyboard
import threading

def record_audio(filename, sample_rate=44100, chunk_size=1024, channels=2):
    p = pyaudio.PyAudio()

    # Open stream
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk_size)

    print("Press Enter to start recording and release to stop.")

    frames = []
    recording = False

    def start_recording():
        nonlocal recording
        recording = True
        print("Recording...")

        while recording:
            data = stream.read(chunk_size)
            frames.append(data)

        print("Recording finished")

        # Save the recorded data as a WAV file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()

    def stop_recording():
        nonlocal recording
        recording = False

    # Keyboard event listeners
    keyboard.on_press_key("enter", lambda _: threading.Thread(target=start_recording).start())
    keyboard.on_release_key("enter", lambda _: stop_recording())

    keyboard.wait("esc")

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    filename = "output.wav"
    record_audio(filename)
