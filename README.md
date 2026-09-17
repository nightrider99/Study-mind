# StudyMind AI 🧠

**Learn smarter. Practice better. Grow every day.**

An AI-powered learning assistant that helps students study smarter — upload notes, ask questions, generate quizzes and flashcards, and track progress over time.

---

## 📌 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Database Setup (Supabase)](#-database-setup-supabase)
- [Deployment](#-deployment)
- [API Overview](#-api-overview)
- [Developing on Your Phone](#-developing-on-your-phone)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 💡 About

StudyMind AI is a full-stack web application built for students. Upload your study materials (notes, PDFs), then use the app to:

- Ask questions and get answers grounded in **your own** content
- Auto-generate multiple-choice and short-answer quizzes
- Turn key concepts into flashcards for active recall
- Track quiz scores and study sessions over time

The project is designed as a monorepo: a **React + TypeScript** frontend and a **Python FastAPI** backend, deployed independently (Vercel + Render) from a single GitHub repository.

---

## ✨ Features

### 📚 AI Notes & PDF Assistant
- Upload study notes and PDF documents
- Ask questions about uploaded materials
- Get answers based on the provided content, with references to relevant sections where possible

### 📝 Quiz Generator
- Generate multiple-choice questions from study materials
- Create short-answer practice questions
- Take quizzes and receive instant scores
- Review correct answers with explanations

### 🗂️ Smart Flashcards
- Automatically turn important concepts into Q&A flashcards
- Review flashcards for active recall and spaced revision

### 📊 Learning Progress Dashboard
- Track quiz scores and performance over time
- Record completed study sessions
- Identify topics that need more practice

> **Note:** AI-powered features (Q&A, quiz generation, flashcard extraction) are planned and will be layered on top of the core app.

---

## 🛠️ Tech Stack

| Layer      | Technology                          | Hosted On        |
|------------|-------------------------------------|------------------|
| Frontend   | React 18 + TypeScript + Vite        | Vercel           |
| Styling    | Tailwind CSS                        | —                |
| Backend    | Python 3.10+ + FastAPI              | Render           |
| Database   | PostgreSQL (via Supabase)           | Supabase (free)  |
| File Storage | Supabase Storage (PDF uploads)    | Supabase (free)  |
| PDF Parsing | pypdf                              | —                |
| AI (planned) | LLM API integration               | TBD              |

---

## 🏗️ Architecture

