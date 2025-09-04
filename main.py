# Mehrdad Hasanzade
# Hitwithit id in Youtube and Telegram
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
from pynput import keyboard
import speech_recognition as sr
from bidi.algorithm import get_display
from arabic_reshaper import reshape
import openai

FS = 16000
CHANNEL = 1
FILENAME = "record.wav"
openai.api_key = "YOUR_API_KEY"
is_recording = False
frames = []

def reshaper(text):
    return get_display(reshape(text))

def start_recorder():
    global frames, is_recording
    is_recording = True
    frames = []
    print("start recording!...")
    def callback(indata, frames_count, time_info, status):
        if is_recording:
            frames.append(indata.copy())
        
    stream = sd.InputStream(
        samplerate=FS,
        channels=CHANNEL,
        callback=callback,
        dtype="int16"
    )
    
    stream.start()
        
        
    def on_press(key):
        global is_recording
        try:
            if key == keyboard.Key.esc:
                is_recording = False
                stream.stop()

                print("stop recording...")
                return False
        except:
            pass
        
    with keyboard.Listener(on_press=on_press) as linstener:
        linstener.join()
        
 
    audio_data = np.concatenate(frames,axis=0)
    write(FILENAME, FS, audio_data)
    print(f"file saved! {FILENAME}")
    
    
def speech_to_text(filename, lang="fa-IR"):
    recon = sr.Recognizer()
    
    with sr.AudioFile(filename) as source:
        audio_data = recon.record(source)
        try:
            text = recon.recognize_google(audio_data, language=lang)
            print("text extracted!",reshaper(text))
            return text
        except sr.UnknownValueError:
            print("google not recon!")
        except sr.RequestError:
            print("connection faild!")
        return None
    


def structed_text(message, prompt="این متن رو بر اساس موضوع شرح بیماری و تاریخ و اسم بیمار و نام دارو طبقه بندی و ساختار مند بهم تحویل بده", model="gpt-4o-mini"):
    
    text = [
        {"role":"system","content" : prompt},
        {"role":"user", "content": message}
    ]
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=text,
            temperature=0.7,
            max_tokens=500
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error is {e}")
    return answer
    
        
    
      


if __name__ == '__main__':
    start_recorder()
    text = speech_to_text(FILENAME)
    print(structed_text(text))            