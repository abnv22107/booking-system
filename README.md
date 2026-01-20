# AI Doctor Booking Assistant

A conversational, AI-driven booking assistant that supports document-based question answering (RAG) and a complete end-to-end doctor appointment booking workflow.  
The system is built as a single Streamlit application and is fully deployed for public use.

Live Demo:
https://booking-system-n5zffw5a7rgzlz7ppqemlv.streamlit.app/

---

## 1. Project Overview

The goal of this project is to design and implement a **chat-based AI Booking Assistant** that can:

- Answer user questions using uploaded documents (Retrieval-Augmented Generation).
- Detect booking-related intent and guide the user through a structured booking flow.
- Collect booking details across multiple turns without repetition.
- Confirm details before storing them in a database.
- Send a confirmation email after successful booking.
- Provide an Admin Dashboard to view stored bookings.

This project focuses on **system design, conversational state management, and robustness**, rather than just model usage.

---

## 2. Key Features

### Document-Based Q&A (RAG)

- Users can upload one or more PDF documents.
- Text is extracted, chunked, embedded, and stored in a vector index.
- User questions are answered based on retrieved document context.
- If no documents are uploaded, the assistant responds gracefully with a helpful message.

---

### Conversational Booking Assistant

- Chat-based interface with short-term conversational memory (last 20–25 messages).
- Automatically detects:
  - General queries → routed to the RAG pipeline
  - Booking intent → routed to the booking flow
- Booking is handled through a stateful, multi-turn conversation.

---

### Booking Flow (Slot Filling)

The assistant collects the following details step by step:

1. Full name  
2. Email address  
3. Phone number  
4. Doctor or specialty  
5. Preferred appointment date  
6. Preferred appointment time  

Key characteristics:
- Questions are asked only once.
- User inputs are validated before being accepted.
- The booking proceeds only after explicit user confirmation.

---

### Confirmation & Persistence

- Once all booking details are collected, the assistant:
  - Summarizes the booking details.
  - Asks the user to explicitly confirm or cancel.
- On confirmation:
  - The booking is saved in a SQLite database.
  - A unique booking ID is generated and returned to the user.

Note: SQLite database reset on restart is acceptable as per assignment instructions.

---

### Email Notification

- A confirmation email is sent to the user after successful booking.
- The email includes:
  - Booking ID
  - Doctor or specialty
  - Appointment date and time
- Email failures are handled gracefully:
  - The booking is still saved.
  - The user is informed clearly that email delivery failed.

Email is implemented using SMTP with Gmail App Passwords and Streamlit secrets.

---

### Admin Dashboard (Mandatory)

- Accessible via a sidebar mode selector.
- Displays all stored bookings from the database.
- Supports searching bookings by name or email.
- Demonstrates backend persistence and admin-level visibility.

---

## 3. Architecture Overview

- Frontend & Backend: Streamlit  
- RAG Pipeline: PDF ingestion, chunking, embeddings, vector similarity search  
- Booking System: Intent detection, slot filling, validation, confirmation  
- Database: SQLite  
- Notifications: SMTP-based email service  

---

## 4. Project Structure

project_root/  
├── app/  
│   ├── main.py              # Streamlit entry point  
│   ├── chat_logic.py        # Intent detection & chat memory  
│   ├── booking_flow.py      # Slot filling, validation, confirmation  
│   ├── rag_pipeline.py      # PDF ingestion & retrieval  
│   ├── tools.py             # Database and email utilities  
│   ├── admin_dashboard.py   # Admin dashboard UI  
│   └── config.py  
│  
├── db/  
│   ├── database.py          # SQLite connection  
│   └── models.py            # Database schema  
│  
├── .streamlit/  
│   └── secrets.toml         # Secrets (not committed)  
│  
├── requirements.txt  
└── README.md  

---

## 5. Running the Project Locally

### Prerequisites

- Python 3.9 or higher
- Git
- Streamlit

### Steps

1. Install dependencies  
   pip install -r requirements.txt

2. Run the application  
   streamlit run app/main.py

---

## 6. Deployment

The application is deployed using **Streamlit Cloud**.

- Source code is hosted on a public GitHub repository.
- Secrets (SMTP credentials) are configured using Streamlit Cloud settings.
- The deployed application is accessible through a public URL.

---

## 7. Error Handling & Validation

The system validates and handles:

- Invalid email formats
- Invalid phone numbers
- Invalid date formats (YYYY-MM-DD)
- Missing or invalid PDF uploads
- Database insertion or connection errors
- Email delivery failures

All errors are communicated using **clear, user-friendly messages**, as required.

---
