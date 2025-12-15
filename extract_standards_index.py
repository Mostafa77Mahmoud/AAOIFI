#!/usr/bin/env python3
"""
Extract id, title, keywords, and aliases from all standards JSON files
and combine them into a single index file.
"""

import json
from pathlib import Path

def extract_standards_index():
    json_dir = Path("json_standards")
    output_file = Path("standards_index.json")
    
    standards_list = []
    
    json_files = sorted(json_dir.glob("*.json"))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            standard_entry = {
                "id": data.get("id", ""),
                "title": data.get("title", ""),
                "keywords": data.get("keywords", []),
                "aliases": data.get("aliases", [])
            }
            
            standards_list.append(standard_entry)
            print(f"✓ Extracted: {standard_entry['id']} - {standard_entry['title'][:50]}...")
            
        except Exception as e:
            print(f"✗ Error reading {json_file.name}: {e}")
    
    output_data = {
        "total_standards": len(standards_list),
        "standards": standards_list
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ تم حفظ {len(standards_list)} معيار في {output_file}")
    print(f"  Saved {len(standards_list)} standards to {output_file}")

if __name__ == "__main__":
    extract_standards_index()
