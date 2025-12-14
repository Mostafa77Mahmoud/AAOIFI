# AAOIFI Standards PDF to JSON Processor

## Overview
This project processes 61 AAOIFI Sharia standards from PDF format to MongoDB-ready JSON files using Google Gemini 2.5 Flash AI for accurate Arabic text extraction.

## Project Structure
```
├── AAOIFI_Standards_Complete/  # Input: Place PDF files here
├── json_standards/              # Output: Generated JSON files
├── logs/                        # Processing logs
├── src/
│   ├── config.py               # Configuration and constants
│   ├── pdf_processor.py        # Gemini API integration for PDF processing
│   └── json_builder.py         # JSON structure building and validation
└── main.py                     # Main entry point
```

## How to Use

### 1. Add PDF Files
Place all 61 AAOIFI standard PDF files in the `AAOIFI_Standards_Complete/` folder with this naming format:
- `معيار (1) المتاجرة في العملات.pdf`
- `معيار (2) ....pdf`
- ...
- `معيار (61) ....pdf`

### 2. Set Up API Key
Make sure `GEMINI_API_KEY` is set in your environment secrets.

### 3. Run the Processor
```bash
python main.py
```

## Output JSON Format
Each standard is converted to a JSON file (`SS01.json` to `SS61.json`) with this structure:
```json
{
  "id": "SS01",
  "title": "اسم المعيار",
  "text": "النص الكامل للمعيار",
  "sections": [
    {"sec_id": "1", "heading": "المقدمة", "text": "..."},
    {"sec_id": "1.1", "heading": "التعريفات", "text": "..."}
  ],
  "keywords": ["كلمة1", "كلمة2"],
  "aliases": ["الاسم البديل بالعربية", "English Alias"],
  "pages": ["1", "2", "3"]
}
```

## Features
- Automatic PDF file detection and sorting
- Smart file upload (Files API for large files, inline for smaller ones)
- Retry mechanism for failed extractions
- Complete Arabic language support
- MongoDB-ready JSON output
- Detailed logging for each processing step

## Dependencies
- google-genai (Gemini AI SDK)
- pydantic
- Python 3.11

## Environment Variables
- `GEMINI_API_KEY`: Google AI API key for Gemini access
