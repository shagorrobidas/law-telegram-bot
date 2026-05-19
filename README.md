# ⚖️ Bangla Law Assistant (Bangla Chat Bot)

[![AI Engine](https://img.shields.io/badge/AI-Groq%20Llama%203.3%2070B-orange?style=for-the-badge)](https://console.groq.com/)
[![Framework](https://img.shields.io/badge/Telegram-python--telegram--bot%20v22.7-blue?style=for-the-badge)](https://python-telegram-bot.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Bangla Law Assistant** is an advanced AI-powered Telegram Chatbot specifically customized to act as a **Senior Bangladeshi Advocate, Legal Researcher, and Cyber Law Specialist**. Powered by Groq's high-speed **Llama 3.3 70B** model and built with asynchronous, non-blocking network operations, this bot provides detailed, precise, and legally sound advice in Bengali based on official Bangladeshi laws and court precedents.

---

## 🌟 Key Features

### 1. 🔍 AI Legal Research & Judgment Analysis
* **Official Data Integrity:** Grounded strictly in official Bangladeshi sources (e.g., [BDLaws](https://bdlaws.minlaw.gov.bd/), Supreme Court, Ministry of Law, NLASO, and Bangladesh Police).
* **Precedent Analysis:** Automatically extracts case names, court levels, key legal questions, observations, and long-term implications when analyzing judgments.
* **Drafting Intelligence:** Generates professional drafts adhering to Bangladeshi court formats (proper heading, party info, relevant sections, prayer, verification, and advocate signature areas).

### 2. 🛡️ Specialized Legal Modes
* **Bangladesh Cyber Law Specialist:** Detailed guidance on online fraud, bKash/Nagad scams, digital harassment, fake IDs, OTP fraud, digital evidence collection, and police complaint steps.
* **Land & Property Law:** Expert guidance on property disputes, Mutat/Namjari (নামজারি), Khatian (খতিয়ান), registration processes, heirs/inheritance (ওয়ারিশ), and identifying fake deeds.
* **Family Law Specialist:** Muslim family code guides, divorce registration, Denmohor (দেনমোহর), child custody, and domestic violence support.
* **Business & Corporate Advisor:** Quick advice on company registration, Trade Licenses, VAT/TIN, shareholder agreements, NDAs, and startup legal support.

### 3. 💾 Advanced Persistent Context (Advanced Bot Only)
* **Local JSON Database:** Remembers conversation context across days.
* **Smart Token Truncation:** Automatically truncates history to prevent Groq API Daily Token Limit (TPD) exhaustion while keeping the AI contextually aware.

---

## 📂 Project Architecture

The repository contains two robust versions of the bot:

1. **`bangla_chatbot_groq.py` (Basic Bot):**
   * Lightweight, memory-only session storage.
   * Asynchronous, non-blocking Groq API interface.
   * Best for fast, stateless, and high-concurrency deployments.

2. **`bangla_chatbot_groq_advance.py` (Advanced Bot):**
   * Built-in file database persistent system (`chatbot_database.json`).
   * Remembers conversations across restarts.
   * Tracks user interaction statistics and activity trends.

---

## 🚀 Setup & Installation Guide

Follow these steps to configure and run the bot on your system:

### 1. Clone the Repository
```bash
git clone git@github.com:shagorrobidas/telegram-bot.git
cd telegram-bot
```

### 2. Setup Virtual Environment
Create and activate a isolated Python environment to keep packages clean:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Install Dependencies
Install the required asynchronous APIs and utilities:
```bash
pip install --upgrade pip
pip install python-telegram-bot groq python-dotenv httpx
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```bash
touch .env
```
Open `.env` and fill in your credential tokens:
```ini
# Telegram Bot Token (Generated via @BotFather on Telegram)
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN

# Groq API Key (Generated via console.groq.com)
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

---

## 🎯 How to Run the Bot

Make sure your virtual environment is active, then launch your preferred version:

### Run the Basic Bot
```bash
python bangla_chatbot_groq.py
```

### Run the Advanced Bot (With Database support)
```bash
python bangla_chatbot_groq_advance.py
```

---

## 📋 Interactive Commands

Once the bot is running, you can use these commands inside your Telegram chat:

| Command | Description |
| :--- | :--- |
| `/start` | Starts the bot and prints the custom welcome legal introduction. |
| `/help` | Displays helper menus with example questions (Cyber crime, property, marriage). |
| `/info` | Displays bot specifications, AI engine version, and legal behavior guidelines. |
| `/clear` | Resets conversation memory / clears current session database to free up tokens. |
| `/stats` | *(Advanced Bot Only)* Displays your interaction statistics and active logs. |

---

## 🛡️ Legal AI Behavioral Rules

To maintain high safety standards, the bot enforces the following rules strictly in its prompt:
* Always warns that AI responses are for informative purposes and strongly recommends consulting a registered professional advocate for actual court representations.
* Never guarantees a specific legal outcome in court.
* Always references official laws, sections, and relevant codes (e.g., Penal Code 1860, Digital Security Act 2018).

---

## 🤝 Contributing & Support

Developed with ❤️ by **[Shagor Robidas](https://github.com/shagorrobidas)**. 

Feel free to open issues or pull requests to extend support for additional legal resources!
