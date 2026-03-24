try:
    from text_extractor import extract_text
    print("✓ text_extractor OK")
except Exception as e:
    print(f"✗ text_extractor ERROR: {e}")

try:
    from keyword_scanner import scan_resume_vs_jd
    print("✓ keyword_scanner OK")
except Exception as e:
    print(f"✗ keyword_scanner ERROR: {e}")

print("Done!")