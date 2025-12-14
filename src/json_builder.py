import json
import logging
from pathlib import Path
from typing import Optional

from src.config import JSON_OUTPUT_DIR, STANDARD_ID_PREFIX

logger = logging.getLogger(__name__)


def format_standard_id(number: int) -> str:
    return f"{STANDARD_ID_PREFIX}{number:02d}"


def build_standard_json(
    standard_number: int,
    extracted_data: dict
) -> dict:
    standard_id = format_standard_id(standard_number)
    
    standard_json = {
        "id": standard_id,
        "title": extracted_data.get("title", ""),
        "text": extracted_data.get("text", ""),
        "sections": extracted_data.get("sections", []),
        "keywords": extracted_data.get("keywords", []),
        "aliases": extracted_data.get("aliases", []),
        "pages": extracted_data.get("pages", []),
    }
    
    for section in standard_json["sections"]:
        if "sec_id" not in section:
            section["sec_id"] = ""
        if "heading" not in section:
            section["heading"] = ""
        if "text" not in section:
            section["text"] = ""
    
    return standard_json


def save_standard_json(standard_number: int, data: dict) -> Optional[Path]:
    try:
        standard_id = format_standard_id(standard_number)
        output_path = JSON_OUTPUT_DIR / f"{standard_id}.json"
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved JSON: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error saving JSON for standard {standard_number}: {e}")
        return None


def validate_json_for_mongodb(data: dict) -> bool:
    required_fields = ["id", "title", "text", "sections", "keywords", "aliases", "pages"]
    
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return False
    
    if not isinstance(data["sections"], list):
        logger.warning("sections must be a list")
        return False
    
    if not isinstance(data["keywords"], list):
        logger.warning("keywords must be a list")
        return False
    
    if not isinstance(data["aliases"], list):
        logger.warning("aliases must be a list")
        return False
    
    if not isinstance(data["pages"], list):
        logger.warning("pages must be a list")
        return False
    
    return True
