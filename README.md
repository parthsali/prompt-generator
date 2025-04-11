# Technical Question Analyzer 📸

A Streamlit application that uses Google's Gemini AI to analyze technical questions from images. Perfect for educators, students, and technical interviewers who want to digitize and structure their question banks.

## Features

- Upload multiple images containing technical questions
- Automatic question type detection (MCQ, coding, run-code)
- Structured JSON output for each question
- Question number detection
- Comprehensive LLM prompt generation
- Clean and intuitive UI

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variable:
   ```bash
   export GEMINI_API_KEY='your-api-key-here'
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Requirements

- Python 3.7+
- Google Gemini API key
- Stable internet connection

## Note

Temporary files are automatically cleaned up after processing. 