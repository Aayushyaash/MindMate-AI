# MindMate - AI-Powered Mental Health & Wellness Platform

<div align="center">

![MindMate](https://img.shields.io/badge/MindMate-Mental_Health_AI-blue)
![Django](https://img.shields.io/badge/Django-5.1-darkgreen)
![Gemini](https://img.shields.io/badge/Gemini-3.0-orange)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

*A full-featured, real-time AI-powered mental health and wellness platform with voice capabilities, interactive games, and psychological assessments.*

</div>

---

> **Team Project** — Built collaboratively as a group project. Original repository maintained by the team lead ([KumarAryan0530/MindMate-AI](https://github.com/KumarAryan0530/MindMate-AI)). My contributions are listed below.

### 👥 Team

| Role | Name | GitHub |
|------|------|--------|
| Team Lead | Kumar Aryan | [@KumarAryan0530](https://github.com/KumarAryan0530) |
| Member | Riti Kumari | [@ritikumari020](https://github.com/ritikumari020) |
| Member | Aayush Yash | [@Aayushyaash](https://github.com/Aayushyaash) |

### My Contributions
- **Voice**: Real-time voice call integration using Twilio WebRTC and ElevenLabs TTS pipeline
- **AI Assessments**: PHQ-9 psychological assessment quizzes with Gemini Flash/Pro and automatic model fallback
- **Games**: Cognitive wellness games, mood-tracking gamification, and stress-relief mini-games with leaderboards
- **Real-time**: WebSocket consumers for live AI chat via Django Channels with real-time progress updates
- **Auth & Profiles**: User authentication with django-allauth, mental health history tracking, privacy-focused storage
- **Analytics**: Journal entry management, prescription tracking, and mental health assessment reporting

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technical Stack](#technical-stack)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [License](#license)

---

## 🎯 Overview

**MindMate** is a mental health and wellness platform that uses AI to provide accessible, personalized support. Built with Django 5.1, it includes real-time voice interactions, AI-driven psychological assessments (PHQ-9), and a wellness gaming system.

---

## ✨ Features

### 🎤 Voice-Based Interactions
- Real-time voice calls with AI assistants
- Twilio-powered WebRTC connectivity
- ElevenLabs text-to-speech for natural conversations

### 🤖 AI-Powered Assessments
- Psychological assessment quizzes (PHQ-9)
- Google Gemini Flash/Pro with automatic fallback
- Personalized mental health scoring
- Startup health checks for all API connections

### 🎮 Interactive Games & Activities
- Cognitive wellness games
- Mood-tracking gamification
- Stress-relief mini-games with leaderboards

### 👥 User Management
- Secure authentication with django-allauth
- User profiles with mental health history
- Privacy-focused data storage

### 📊 Analytics & Reporting
- Comprehensive mental health assessments
- Journal entry management
- Prescription tracking

### 🔄 Real-time Features
- WebSocket support via Django Channels
- Live chat with AI assistants
- Real-time progress updates

---

## 🛠️ Technical Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | Django 5.1, Python 3.8+, Django Channels 4.0, Daphne 4.0 |
| **Task Queue** | Celery 5.3 with Redis |
| **AI/ML** | Google Gemini (Flash/Pro), Cloudflare AI, `google-genai` SDK |
| **Voice** | Twilio Voice API, ElevenLabs Conversational AI |
| **Frontend** | Django Templates, Bootstrap 5, WebSocket API |
| **Infrastructure** | Redis, SQLite, ngrok (dev) |
| **Testing** | pytest, pytest-django, pytest-cov |

---

## 🏗️ System Architecture

```mermaid
graph TD
    User["👤 Users"] <--> UI["🌐 Django Web UI<br/>(Port: 8000)"]
    UI <--> API["🔌 Daphne ASGI Server"]
    
    subgraph Backend["Backend Services"]
        API --> Auth["🔐 Authentication"]
        API --> Core["⚙️ Core Logic Engine"]
        API --> Voice["🎤 Voice Processor"]
    end
    
    subgraph Storage["Storage Layer"]
        Core --> DB[("🗄️ Database")]
        Auth --> Cache[("⚡ Redis")]
        Voice --> Media[("📁 Media Storage")]
    end
    
    subgraph External["External Services"]
        Core --> Gemini["🤖 Google Gemini API"]
        Voice --> TTS["🔊 ElevenLabs TTS"]
        Auth --> Twilio["📞 Twilio Voice API"]
    end
    
    Cache --> Tasks["⏱️ Celery Task Queue"]
    Tasks --> Beat["🔄 Celery Beat Scheduler"]
```

---

## 📦 Prerequisites

### Required Software
- **Python 3.8+**
- **Redis** (for caching and Celery)
- **ngrok** (for voice call webhooks)

### API Keys Required
| Service | Purpose | Get From |
|---------|---------|----------|
| Google Gemini | AI Chat, Quiz, Prescription OCR | [ai.google.dev](https://ai.google.dev/) |
| Cloudflare AI | Sentiment Analysis | [dash.cloudflare.com](https://dash.cloudflare.com/) |
| Twilio | Voice Calls | [twilio.com/console](https://www.twilio.com/console) |
| ElevenLabs | Text-to-Speech | [elevenlabs.io](https://elevenlabs.io/) |

---

## 🚀 Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Aayushyaash/MindMate-AI.git
cd MindMate-AI
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 5. Initialize Database

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## 🖥️ Running the Application

You need to run **5 services** in separate terminal windows:

### Terminal 1: Redis

```bash
# Using Docker
docker run -d --name redis -p 6379:6379 redis:latest

# Or if Redis is installed locally
redis-server
```

### Terminal 2: ngrok (for Voice Calls)

```bash
ngrok http 8000
# Copy the https:// URL and update NGROK_URL in .env
```

### Terminal 3: Daphne Server (Main Application)

```powershell
# Windows
.\venv\Scripts\Activate.ps1
daphne -b 0.0.0.0 -p 8000 perplex.asgi:application
```

```bash
# macOS/Linux
source venv/bin/activate
daphne -b 0.0.0.0 -p 8000 perplex.asgi:application
```

### Terminal 4: Celery Worker

```powershell
# Windows
.\venv\Scripts\Activate.ps1
celery -A perplex worker -l info -P solo
```

```bash
# macOS/Linux
source venv/bin/activate
celery -A perplex worker -l info
```

### Terminal 5: Celery Beat (Scheduler)

```powershell
# Windows
.\venv\Scripts\Activate.ps1
celery -A perplex beat -l info
```

```bash
# macOS/Linux
source venv/bin/activate
celery -A perplex beat -l info
```

### Access Points

| Service | URL |
|---------|-----|
| **Web App** | http://localhost:8000 |
| **Admin Panel** | http://localhost:8000/admin |
| **Voice Calls** | http://localhost:8000/voice/ |
| **Games** | http://localhost:8000/games/ |

---

## 📁 Project Structure

```
mindmate/
├── accounts/              # User authentication & profiles
│   ├── models.py
│   ├── views.py
│   └── forms.py
│
├── app/                   # Core application
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── games/                 # Gamification & wellness games
│   ├── models.py
│   └── views.py
│
├── voice_calls/           # Voice integration module
│   ├── consumers.py       # WebSocket consumers
│   ├── tasks.py           # Celery tasks
│   └── routing.py
│
├── perplex/               # Django project settings
│   ├── settings.py
│   ├── asgi.py
│   ├── celery.py
│   ├── urls.py
│   └── services/
│       ├── gemini_service.py
│       ├── cloudflare_service.py
│       ├── elevenlabs_service.py
│       ├── twilio_service.py
│       └── health_check.py
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── templates/
├── media/
├── requirements.txt
├── .env.example
└── README.md
```

---

## 📝 License

MIT License — demo/portfolio project for educational purposes.
