import os                   # file path and existence checks
import json                 # Vosk returns JSON strings; parse into Python dicts
import queue                # a thread-safe FIFO used to biffer mic audio chunks
import sounddevice as sd    # records raw audio from microphone
import vosk                 # offline speech recognition engine and model wrapper
import pyttsx3              # offline text-to-speech engine

# Initialize text-to-speech
engine = pyttsx3.init()             # Creates a TTS engine
engine.setProperty("rate", 175)     # Controls speak back speed
engine.setProperty("volume", 1.0)   # Controls speak back volume (1.0 is max)

# Change windows voices
voices = engine.getProperty("voices")
engine.setProperty("voices", voices[0].id)  # Different indecies change voice

# Path to Vosk model folder
VOSK_MODEL_PATH = os.path.join("models", "vosk-model-small-en-us-0.15")     

# Initialize recognizer model
if not os.path.exists(VOSK_MODEL_PATH):
    raise FileNotFoundError("Could not find Vosk model folder at " + VOSK_MODEL_PATH)
model = vosk.Model(VOSK_MODEL_PATH)         # Loads model into memory

def listen_to_voice(duration=5, samplerate=16000):                  # default listen = 5 sec, at 16000Hz, standard for speech models
    """Record audio with sounddevice and transcribe using Vosk."""
    print("Recording for", duration, "seconds... speak now!")

    # Creates a FIFO queue for temp hold of audio chunks
    # decouples the recording and processing
    q = queue.Queue()       


    def callback(indata,        # raw recorded samples (np.array or bytes) 
                 frames,        # how many samples are in block
                 time,          # timing info
                 status):       # prints status if something goes wrong
        if status:
            print(status)
        q.put(bytes(indata))    # converts chunk to raw bytes, and pushes to queue

    # Opens the audio stream
    with sd.RawInputStream(samplerate=samplerate,       # sample rate matches model 
                           blocksize=8000,              # each callback handles 0.5s of audio
                           dtype="int16",               # sets data type to int16 bit
                           channels=1,                  # mono (set by Vosk)
                           callback=callback):
        rec = vosk.KaldiRecognizer(model, samplerate)   # sets up live speech recognizer that accepts streaming audio
        
        # Main listenining loop
        while True:
            try:
                data = q.get(timeout=duration)      # waits for next audio chunk from queue
            except queue.Empty:                     # Breaks when queue is empty
                break
            
            # Feeds each chunk into Vosk
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    return text
        # Final partial result if nothing else
        final = json.loads(rec.FinalResult()).get("text", "")
        print("Final result:", final)
        return final

# Speaks text over the computer speakers
def speak_text(text):
    """Speak text aloud."""
    engine.say(text)
    engine.runAndWait()