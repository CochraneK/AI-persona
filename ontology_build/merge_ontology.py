#!/usr/bin/env python3
"""
Merge ICD-11 parts 1-3 into a single diagnosis_ontology.json
"""
import json, os

# Script lives in AI-persona/ontology_build/
ONTOLOGY_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(ONTOLOGY_DIR)  # AI-persona/
BUILD_DIR = os.path.join(ONTOLOGY_DIR, "_build")

# Load three parts
files = ["icd11_part1.json", "icd11_part2.json", "icd11_part3.json"]
all_icd_blocks = []
schema = None

for f in files:
    path = os.path.join(BUILD_DIR, f)
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if schema is None:
        schema = data.get("schema", {})
    all_icd_blocks.extend(data.get("blocks", []))

# Load DSM-5-TR from part3 (it's stored in the third file's extra data)
with open(os.path.join(BASE, "_build/icd11_part3.json"), "r", encoding="utf-8") as f:
    full_part3 = json.load(f)

dsm5tr = full_part3.get("dsm5tr", {})

# Build final ontology
ontology = {
    "meta": {
        "title": "Comprehensive Mental Disorder Diagnosis Ontology",
        "version": "1.0.0",
        "date": "2026-08-29",
        "sources": [
            "ICD-11 Chapter 06 (Mental, Behavioural or Neurodevelopmental Disorders)",
            "DSM-5-TR (Diagnostic and Statistical Manual of Mental Disorders, 5th Edition, Text Revision, 2022)"
        ],
        "description": "Complete hierarchical classification of mental disorders from ICD-11 and DSM-5-TR, "
                       "including diagnostic codes, subtypes, common comorbidities, age of onset, gender ratios, and relevant scales."
    },
    "schema": schema,
    "icd11": {
        "name": "ICD-11 Chapter 06 — Mental, Behavioural or Neurodevelopmental Disorders",
        "code_range": "6A00-6E8Z",
        "blocks": all_icd_blocks
    },
    "dsm5tr": dsm5tr
}

# Save
output_path = os.path.join(BASE, "diagnosis_ontology.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(ontology, f, ensure_ascii=False, indent=2)

# Stats
icd_count = sum(len(b.get("disorders", [])) for b in all_icd_blocks)
dsm_count = sum(len(ch.get("disorders", [])) for ch in dsm5tr.get("chapters", []))

print(f"ICD-11: {len(all_icd_blocks)} blocks, {icd_count} diagnoses")
print(f"DSM-5-TR: {len(dsm5tr.get('chapters', []))} chapters, {dsm_count} diagnoses")
print(f"Total saved to: {output_path}")
print(f"File size: {os.path.getsize(output_path):,} bytes")
