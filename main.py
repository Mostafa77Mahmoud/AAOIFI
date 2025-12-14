#!/usr/bin/env python3
"""
AAOIFI Standards PDF to JSON Processor
Processes 61 Sharia standards from PDF to MongoDB-ready JSON format.
Uses Google Gemini 2.5 Flash for accurate text extraction.
"""

import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from src.config import (
    PDF_INPUT_DIR,
    JSON_OUTPUT_DIR,
    LOGS_DIR,
    TOTAL_STANDARDS,
    GEMINI_API_KEY,
)
from src.pdf_processor import process_pdf_with_gemini
from src.json_builder import (
    build_standard_json,
    save_standard_json,
    validate_json_for_mongodb,
)

log_filename = LOGS_DIR / f"processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def convert_hindi_to_arabic_numerals(text: str) -> str:
    hindi_to_arabic = {
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
    }
    for hindi, arabic in hindi_to_arabic.items():
        text = text.replace(hindi, arabic)
    return text


def extract_standard_number(filename: str) -> int:
    normalized = convert_hindi_to_arabic_numerals(filename)
    
    match = re.search(r"معيار\s*\((\d+)\)", normalized)
    if match:
        return int(match.group(1))
    
    match = re.search(r"معيار[–\-](\d+)", normalized)
    if match:
        return int(match.group(1))
    
    match = re.search(r"المعيار[–\-]الشرعي[–\-]رقم[–\-](\d+)", normalized)
    if match:
        return int(match.group(1))
    
    match = re.search(r"\((\d+)\)", normalized)
    if match:
        return int(match.group(1))
    
    match = re.search(r"رقم[–\-](\d+)", normalized)
    if match:
        return int(match.group(1))
    
    match = re.search(r"(\d+)", normalized)
    if match:
        return int(match.group(1))
    
    return 0


def get_pdf_files() -> List[Path]:
    pdf_files = list(PDF_INPUT_DIR.glob("*.pdf"))
    pdf_files.extend(PDF_INPUT_DIR.glob("*.PDF"))
    
    pdf_files = list(set(pdf_files))
    pdf_files.sort(key=lambda x: extract_standard_number(x.name))
    
    return pdf_files


def process_single_pdf(pdf_path: Path) -> Tuple[bool, str, int]:
    standard_number = extract_standard_number(pdf_path.name)
    
    if standard_number == 0:
        return False, f"Could not extract standard number from: {pdf_path.name}", 0
    
    logger.info(f"Processing standard {standard_number}: {pdf_path.name}")
    
    extracted_data = process_pdf_with_gemini(pdf_path, standard_number)
    
    if not extracted_data:
        return False, f"Failed to extract data from: {pdf_path.name}", standard_number
    
    standard_json = build_standard_json(standard_number, extracted_data)
    
    if not validate_json_for_mongodb(standard_json):
        return False, f"Invalid JSON structure for: {pdf_path.name}", standard_number
    
    output_path = save_standard_json(standard_number, standard_json)
    
    if not output_path:
        return False, f"Failed to save JSON for: {pdf_path.name}", standard_number
    
    return True, str(output_path), standard_number


def print_summary(
    total: int,
    successful: List[int],
    failed: List[Tuple[int, str]],
    output_dir: Path
) -> None:
    print("\n" + "=" * 60)
    print("ملخص المعالجة - Processing Summary")
    print("=" * 60)
    print(f"إجمالي الملفات المعالجة: {total}")
    print(f"الملفات الناجحة: {len(successful)}")
    print(f"الملفات الفاشلة: {len(failed)}")
    print(f"مجلد الإخراج: {output_dir.absolute()}")
    print("=" * 60)
    
    if successful:
        print("\nالمعايير المعالجة بنجاح:")
        for num in sorted(successful):
            print(f"  - SS{num:02d}")
    
    if failed:
        print("\nالمعايير الفاشلة:")
        for num, reason in failed:
            if num > 0:
                print(f"  - SS{num:02d}: {reason}")
            else:
                print(f"  - {reason}")
    
    print("\n" + "=" * 60)


def main():
    logger.info("Starting AAOIFI Standards PDF to JSON Processor")
    logger.info(f"PDF Input Directory: {PDF_INPUT_DIR.absolute()}")
    logger.info(f"JSON Output Directory: {JSON_OUTPUT_DIR.absolute()}")
    
    if not GEMINI_API_KEY:
        print("\n" + "=" * 60)
        print("تحذير: مفتاح GEMINI_API_KEY غير موجود!")
        print("Warning: GEMINI_API_KEY is not set!")
        print("Please add GEMINI_API_KEY to your environment secrets.")
        print("=" * 60)
        logger.warning("GEMINI_API_KEY is not configured. Processing cannot continue.")
        return
    
    pdf_files = get_pdf_files()
    
    if not pdf_files:
        print("\n" + "=" * 60)
        print("لا توجد ملفات PDF في المجلد!")
        print("No PDF files found in the input directory!")
        print(f"Please add PDF files to: {PDF_INPUT_DIR.absolute()}")
        print("=" * 60)
        print("\nExpected file naming format:")
        print("  معيار (1) المتاجرة في العملات.pdf")
        print("  معيار (2) ....pdf")
        print("  ...")
        print("  معيار (61) ....pdf")
        print("=" * 60)
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    successful: List[int] = []
    failed: List[Tuple[int, str]] = []
    
    for pdf_path in pdf_files:
        success, message, standard_num = process_single_pdf(pdf_path)
        
        if success:
            successful.append(standard_num)
            logger.info(f"Successfully processed standard {standard_num}")
        else:
            failed.append((standard_num, message))
            logger.error(f"Failed to process: {message}")
    
    print_summary(len(pdf_files), successful, failed, JSON_OUTPUT_DIR)
    
    logger.info("Processing completed")
    logger.info(f"Log file saved to: {log_filename}")


if __name__ == "__main__":
    main()
