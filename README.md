# 🤖 Jarvis AI Voice Assistant (ผู้ช่วยเสียง AI ภาษาไทย)

ผู้ช่วยสั่งการด้วยเสียงอัจฉริยะ (AI Voice Assistant) สไตล์ Jarvis รองรับภาษาไทยและหลายภาษา รันโมเดลภาษาขนาดใหญ่ (LLM) บนเครื่องของคุณเองผ่าน **Ollama** โดยไม่มีค่าใช้จ่าย ไม่จำกัดโควตา และมาพร้อมเสียงพูดสังเคราะห์ธรรมชาติจาก **Microsoft Edge-TTS**

---

## ✨ คุณสมบัติเด่น (Features)
- 🧠 **Local LLM (Ollama):** ประมวลผลผ่านโมเดล `qwen2.5:1.5b` บนเครื่องของคุณโดยตรง (เร่งความเร็วด้วยการ์ดจอ NVIDIA CUDA) ฟรีตลอดชีพ ไม่จำกัดโควตา
- ☁️ **Cloud Fallback (Gemini AI):** มีระบบสำรองสลับไปเรียก Google Gemini อัตโนมัติ หากยังไม่ได้เปิด Ollama
- 🎙️ **Speech-to-Text:** ระบบรับฟังและรู้จำเสียงพูดภาษาไทยผ่านไมโครโฟน
- 🗣️ **Natural TTS (Edge-TTS):** เสียงพูดสังเคราะห์ผู้หญิงที่เป็นธรรมชาติ นุ่มนวล ชัดเจน ไม่ยานคาง (เสียงคุณเปรมวดี) พร้อม Fallback สู่ Google TTS
- 🌐 **Multilingual Support:** สลับภาษาพูดอัตโนมัติ (ไทย, อังกฤษ, ญี่ปุ่น, เกาหลี, จีน ฯลฯ)
- 🔒 **Security First:** แยกจัดการ API Key ผ่านไฟล์ `.env` ปลอดภัยสำหรับขึ้น GitHub

---

## 🛠️ ข้อกำหนดเบื้องต้น (Prerequisites)
1. **ระบบปฏิบัติการ:** Windows 10 / 11 (รองรับ Linux และ macOS)
2. **Python:** แนะนำ **Python 3.11 หรือ 3.12/3.13** (ไม่แนะนำ Python 3.14 เนื่องจาก PyAudio ยังไม่มี Pre-built wheel)
3. **ไมโครโฟนและลำโพง:** สำหรับการรับฟังและส่งเสียงพูด
4. **Ollama:** ติดตั้งจาก [ollama.com](https://ollama.com)

---

## 🚀 วิธีติดตั้งและเริ่มต้นใช้งาน (Installation Guide)

### 1. โคลนโปรเจกต์ (Clone Repository)
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. ติดตั้ง Dependencies
ติดตั้งแพ็กเกจที่จำเป็นทั้งหมดผ่านคำสั่ง:
```bash
pip install -r requirements.txt
```

### 3. ดาวน์โหลดโมเดลใน Ollama
เปิด Terminal/PowerShell แล้วสั่งดึงโมเดลภาษาไทย:
```bash
ollama pull qwen2.5:1.5b
```

### 4. ตั้งค่า Environment Variables (ทางเลือก)
คัดลอกไฟล์ `.env.example` เป็น `.env`:
```bash
cp .env.example .env   # สำหรับ macOS/Linux
copy .env.example .env # สำหรับ Windows PowerShell/CMD
```
หากต้องการเปิดใช้งานระบบสำรอง Google Gemini ให้ใส่ API Key ลงในไฟล์ `.env` (ขอคีย์ฟรีได้ที่ [Google AI Studio](https://aistudio.google.com/)):
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🎙️ วิธีรันโปรแกรม (Usage)

รันโปรแกรมด้วยคำสั่ง:
```bash
python jarvis.py
```
*(บน Windows หากมีหลายเวอร์ชัน แนะนำให้ระบุ: `py -3.13 jarvis.py`)*

### ตัวอย่างคำสั่งเสียงที่พูดได้:
- *"สวัสดี สบายดีไหม"*
- *"วันนี้เป็นวันอะไร"*
- *"ช่วยแนะนำเมนูอาหารเย็นหน่อย"*
- *"ปิดระบบ"* หรือ *"ลาก่อน"* (เพื่อออกจากโปรแกรม)
- หรือกด `Ctrl + C` บนคีย์บอร์ดเพื่อหยุดการทำงาน

---

## 📁 โครงสร้างโปรเจกต์ (Project Structure)
```text
├── jarvis.py          # โค้ดหลักของโปรแกรม
├── requirements.txt   # รายการไลบรารีที่จำเป็น
├── .env.example       # แม่แบบไฟล์ตัวแปรแวดล้อม
├── .gitignore         # กำหนดไฟล์ที่ไม่ให้อัปโหลดขึ้น Git
└── README.md          # คู่มือการใช้งาน
```

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).