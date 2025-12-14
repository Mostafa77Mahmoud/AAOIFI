import os
import time
import logging
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types

from src.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MAX_INLINE_SIZE_MB,
    MAX_RETRIES,
    RETRY_DELAY_SECONDS,
)

logger = logging.getLogger(__name__)

client = None

def get_client():
    global client
    if client is None:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set. Please add it to your environment secrets.")
        client = genai.Client(api_key=GEMINI_API_KEY)
    return client


def get_file_size_mb(file_path: Path) -> float:
    return file_path.stat().st_size / (1024 * 1024)


def upload_file_to_gemini(file_path: Path) -> Optional[types.File]:
    try:
        api_client = get_client()
        logger.info(f"Uploading file to Gemini Files API: {file_path.name}")
        uploaded_file = api_client.files.upload(file=str(file_path))
        
        while uploaded_file.state == "PROCESSING":
            time.sleep(2)
            if uploaded_file.name:
                uploaded_file = api_client.files.get(name=uploaded_file.name)
        
        if uploaded_file.state == "FAILED":
            logger.error(f"File upload failed: {file_path.name}")
            return None
            
        logger.info(f"File uploaded successfully: {uploaded_file.name}")
        return uploaded_file
    except Exception as e:
        logger.error(f"Error uploading file {file_path.name}: {e}")
        return None


def process_pdf_with_gemini(pdf_path: Path, standard_number: int) -> Optional[dict]:
    extraction_prompt = f"""أنت خبير في استخراج وتحليل النصوص من مستندات PDF باللغة العربية.

المهمة: استخرج محتوى هذا المعيار الشرعي (معيار رقم {standard_number}) من AAOIFI بدقة كاملة 100%.

يجب أن تستخرج:

1. **title**: عنوان المعيار الكامل بالعربية
2. **text**: النص الكامل للمعيار مع الحفاظ على التنسيق الأصلي
3. **sections**: قائمة بجميع الأقسام والعناوين الفرعية، كل قسم يحتوي على:
   - sec_id: رقم القسم (مثل 1، 1.1، 2، 2.1، إلخ)
   - heading: عنوان القسم
   - text: نص القسم كاملاً
4. **keywords**: قائمة بالكلمات المفتاحية الرئيسية المتعلقة بالمعيار (10-20 كلمة)
5. **aliases**: الأسماء البديلة للمعيار بالعربية والإنجليزية
6. **pages**: قائمة بأرقام الصفحات الموجودة في المستند

أرجع النتيجة بصيغة JSON صالحة فقط، بدون أي نص إضافي.

مثال على الصيغة المطلوبة:
{{
  "title": "عنوان المعيار",
  "text": "النص الكامل...",
  "sections": [
    {{"sec_id": "1", "heading": "المقدمة", "text": "نص المقدمة..."}},
    {{"sec_id": "1.1", "heading": "التعريفات", "text": "نص التعريفات..."}}
  ],
  "keywords": ["كلمة1", "كلمة2"],
  "aliases": ["الاسم البديل بالعربية", "English Alias"],
  "pages": ["1", "2", "3"]
}}

استخرج المحتوى بدقة مع الحفاظ على جميع الجداول والتنسيقات."""

    file_size_mb = get_file_size_mb(pdf_path)
    
    api_client = get_client()
    
    for attempt in range(MAX_RETRIES):
        try:
            if file_size_mb > MAX_INLINE_SIZE_MB:
                uploaded_file = upload_file_to_gemini(pdf_path)
                if not uploaded_file or not uploaded_file.uri:
                    raise Exception("Failed to upload file to Gemini")
                
                response = api_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=[
                        types.Part.from_uri(
                            file_uri=uploaded_file.uri,
                            mime_type="application/pdf",
                        ),
                        extraction_prompt,
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
            else:
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                
                response = api_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=[
                        types.Part.from_bytes(
                            data=pdf_bytes,
                            mime_type="application/pdf",
                        ),
                        extraction_prompt,
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
            
            if response.text:
                import json
                result = json.loads(response.text)
                logger.info(f"Successfully processed: {pdf_path.name}")
                return result
            else:
                raise Exception("Empty response from Gemini")
                
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {pdf_path.name}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY_SECONDS * (attempt + 1))
            else:
                logger.error(f"All attempts failed for {pdf_path.name}")
                return None
    
    return None
