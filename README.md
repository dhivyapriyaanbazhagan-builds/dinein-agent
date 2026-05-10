# 🍽️ AI-Assisted Dining Agent (Intent → Decision → Action)

A hands-on project exploring how systems can move from **user intent → decision-making → action**, inspired by Swiggy MCP.

---

## 🚀 What is this?

This project simulates how an AI-powered system can:

* Understand **free-text user intent**
* Convert it into structured preferences
* Discover and rank options
* Suggest the best match
* (Simulated) complete an action like booking

---

## 🧠 Why this project?

With the introduction of **Swiggy MCP**, AI systems can now:

* Interact with real-world services
* Discover and compare options
* Take actions on behalf of users

👉 Instead of navigating apps, users can simply express intent.

This project explores:

> **How do systems make decisions when given vague human input?**

---

## 🎯 Example

### Input

```
Dinner for 2, quiet place, not too far, 4+ rating
```

### System flow

* Parses intent using Gemini
* Converts to structured preferences
* Finds matching restaurants (mock data)
* Ranks options
* Suggests the best fit

---

## 🏗️ Architecture

```
User Input (Free-text)
 ↓
AI Parser (Gemini)
 ↓
Structured Preferences
 ↓
Mock MCP Tools
(Restaurants + Maps)
 ↓
Ranking / Decision Logic
 ↓
Suggested Output
---

## 🧩 Key Components

### 1️⃣ AI Parser

* Uses Gemini
* Converts natural language → structured input

### 2️⃣ Mock MCP Tools

Simulated versions of:

* Restaurant discovery (Swiggy-style)
* Distance/ETA (Maps-style)
* Booking flow

### 3️⃣ Decision Layer

* Ranks options based on:

 * rating
 * distance
 * preference match

---

## 🔧 Tech Stack

* Python
* Streamlit (UI)
* Gemini (AI parsing)
* Mock MCP tools (Swiggy + Maps simulation)

---

## ⚠️ Note

This project uses **mock data and simulated APIs**.

Why?

* Swiggy MCP requires Builders Club access
* Focus was on **decision logic and agent flow**, not API plumbing

👉 The system is designed so real MCP APIs can be plugged in easily.

---

## 🔮 Future Scope

* Integrate real **Swiggy MCP**
* Integrate real **Google Maps MCP**
* Add **WhatsApp Cloud API**
* Introduce **multi-agent architecture**
* Add **evaluation & observability layers**

---

## 💡 Key Insight

> The hardest part isn’t calling APIs.
> It’s interpreting intent and making decisions under uncertainty.

---

## 🤝 Inspiration

Inspired by:

* Swiggy MCP
* Emerging “intent-first” product experiences

---

## 👋 Closing Thought

We’re moving from:

**Apps that users navigate**
→
**Systems that act on user intent**

---

## 📌 Run Locally

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

---

## 📣 Author

Built as a personal learning exploration into AI-driven decision systems.

---
