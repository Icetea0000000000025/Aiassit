import asyncio
import io
import os
import re
import sys
import time
from datetime import datetime
import speech_recognition as sr
import google.generativeai as genai
import ollama
import edge_tts
from gtts import gTTS
import pygame
from langdetect import detect
from dotenv import load_dotenv

# โหลดตัวแปรจากไฟล์ .env
load_dotenv()

# รองรับการแสดงผลข้อความและ emoji บน Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# ปิดข้อความต้อนรับของ pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
pygame.mixer.init()

# ==========================================
# 1. ตั้งค่าสมอง (Ollama Local AI ในเครื่อง + Gemini สำรอง)
# ==========================================
OLLAMA_MODEL = 'qwen2.5:1.5b'

# ตั้งค่า Gemini API Key จาก Environment Variable (.env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

GEMINI_MODELS = [
    'gemini-3.5-flash-lite',
    'gemini-flash-lite-latest',
    'gemini-3.7-flash',
    'gemini-3.1-flash-lite'
]

SYSTEM_PROMPT = 'คุณคือผู้ช่วย AI ชื่อ Jarvis พูดจาสุภาพ เป็นมิตร ตอบสั้น กระชับ ได้ใจความ ใช้น้ำเสียงผู้หญิง (ลงท้ายด้วยค่ะ/นะคะ) และตอบกลับด้วยภาษาเดียวกับที่ผู้ใช้ถาม ไม่เกิน 2 ประโยค'

def ask_gemini_fallback(prompt):
    if not GEMINI_API_KEY:
        raise RuntimeError("ไม่ได้ระบุ GEMINI_API_KEY ในไฟล์ .env")
    for model_name in GEMINI_MODELS:
        try:
            m = genai.GenerativeModel(model_name=model_name, system_instruction=SYSTEM_PROMPT)
            res = m.generate_content(prompt)
            if res and res.text:
                return res.text
        except Exception:
            continue
    raise RuntimeError("ไม่สามารถเชื่อมต่อ Gemini ได้ในขณะนี้")

def ask_ai(prompt):
    """เรียกใช้งาน Ollama ในเครื่องเป็นหลัก (ไม่จำกัดโควตา ฟรีตลอดกาล)"""
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': prompt}
            ],
            options={
                'temperature': 0.7,
                'num_predict': 90
            }
        )
        return response['message']['content'].strip()
    except Exception as e:
        print(f"⚠️ Ollama ในเครื่องขัดข้อง ({e}) กำลังสลับไปใช้ Cloud AI...")
        return ask_gemini_fallback(prompt)

# ==========================================
# 2. ตั้งค่าปาก (Edge-TTS เสียงเป็นธรรมชาติ พร้อม Fallback)
# ==========================================
def get_voice_for_text(text):
    if re.search(r'[\u0e00-\u0e7f]', text):
        return "th-TH-PremwadeeNeural"
    if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
        return "ja-JP-NanamiNeural"
    if re.search(r'[\uac00-\ud7af]', text):
        return "ko-KR-SunHiNeural"
    if re.search(r'[\u4e00-\u9fff]', text):
        return "zh-CN-XiaoxiaoNeural"
    try:
        lang = detect(text)
        if lang == 'fr':
            return "fr-FR-DeniseNeural"
        elif lang == 'de':
            return "de-DE-KatjaNeural"
    except Exception:
        pass
    return "en-US-JennyNeural"

async def _synthesize_edge_tts(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

def speak(text):
    print(f"🤖 Jarvis: {text}")
    audio_bytes = None
    
    # 1. พยายามใช้ Edge-TTS (เสียงเป็นธรรมชาติ ไม่ยืด ไม่ยานคาง)
    try:
        voice = get_voice_for_text(text)
        audio_bytes = asyncio.run(_synthesize_edge_tts(text, voice))
    except Exception:
        pass
        
    # 2. หาก Edge-TTS ขัดข้อง ให้ใช้ Google TTS สำรองทันที
    if not audio_bytes:
        try:
            lang = "th" if re.search(r'[\u0e00-\u0e7f]', text) else "en"
            tts = gTTS(text=text, lang=lang)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            audio_bytes = fp.getvalue()
        except Exception as e:
            print(f"⚠️ ระบบเสียงพูดขัดข้อง: {e}")
            return

    # เล่นเสียงผ่านลำโพง
    if audio_bytes:
        try:
            sound_stream = io.BytesIO(audio_bytes)
            pygame.mixer.music.load(sound_stream)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.04)
        except Exception as e:
            print(f"⚠️ การเล่นเสียงขัดข้อง: {e}")

# ==========================================
# 3. ตั้งค่าหู (Speech-to-Text ปรับให้จับเสียงไวขึ้น)
# ==========================================
recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.5 
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

def calibrate_mic(source):
    print("🎙️ กำลังปรับจูนเสียงไมโครโฟนรอบข้าง...")
    recognizer.adjust_for_ambient_noise(source, duration=1.0)
    print("✨ ปรับจูนเสร็จเรียบร้อย พร้อมฟังคำสั่งค่ะ!")

def listen(source):
    print("\n🎤 กำลังฟัง... (พูดได้เลยค่ะ)")
    try:
        audio = recognizer.listen(source, timeout=6, phrase_time_limit=10)
        text = recognizer.recognize_google(audio, language="th-TH")
        print(f"👤 คุณ: {text}")
        return text
    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        print("⚠️ ฟังไม่ค่อยถนัดเลยค่ะ รบกวนพูดอีกครั้งนะคะ")
        return None
    except Exception as e:
        print(f"⚠️ เกิดข้อผิดพลาด: {e}")
        return None

# ==========================================
# 4. เริ่มเดินเครื่อง (Main Loop)
# ==========================================
if __name__ == "__main__":
    speak("สวัสดีค่ะ เจ้านาย ระบบพร้อมทำงานแล้วค่ะ")
    
    with sr.Microphone() as source:
        calibrate_mic(source)
        
        try:
            while True:
                user_input = listen(source)
                
                if user_input:
                    # ถ้าพูดคำว่า ปิดระบบ ให้หยุดการทำงานของโปรแกรม
                    if "ปิดระบบ" in user_input or "ลาก่อน" in user_input:
                        speak("ลาก่อนค่ะ ไว้เรียกใช้งานใหม่นะคะ")
                        break
                    
                    try:
                        # ข้อมูลวันเวลาปัจจุบัน
                        now = datetime.now()
                        days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
                        current_time_str = f"วัน{days[now.weekday()]} ที่ {now.day}/{now.month}/{now.year} เวลา {now.strftime('%H:%M น.')}"
                        
                        # สร้าง Prompt ส่งให้ Ollama
                        prompt = f"บริบท: ขณะนี้คือ {current_time_str}\nคำถามของผู้ใช้: {user_input}\n(ตอบสั้น กระชับ ตรงประเด็น ไม่เกิน 2 ประโยค)"
                        
                        # คิดคำตอบด้วย Ollama ในเครื่อง
                        reply_text = ask_ai(prompt)
                        speak(reply_text)
                        
                    except Exception as e:
                        print(f"⚠️ AI ไม่สามารถตอบได้ในขณะนี้ ({e}) กรุณาลองใหม่ค่ะ")
        except KeyboardInterrupt:
            print("\n🛑 หยุดการทำงานของระบบ (Ctrl+C)")
            speak("ปิดระบบเรียบร้อยแล้วค่ะ")