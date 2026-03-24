import re

ATS_SECTIONS = {
    "education":  ["education", "qualification", "degree", "university", "college", "b.tech", "bachelor"],
    "experience": ["experience", "internship", "work", "employment", "project"],
    "skills":     ["skills", "technical skills", "technologies", "tools"],
    "contact":    ["email", "phone", "linkedin", "github", "contact"],
}

def check_ats(text: str) -> dict:
    score = 100
    issues = []
    tips = []
    text_lower = text.lower()
    word_count = len(text.split())

    # Check sections
    sections_found = {}
    for section, keywords in ATS_SECTIONS.items():
        found = any(kw in text_lower for kw in keywords)
        sections_found[section] = found
        if not found:
            issues.append(f"Missing '{section}' section heading")
            score -= 10

    # Check contact info
    has_email = bool(re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text))
    has_phone = bool(re.search(r"(\+91|0)?[\s\-]?[6-9]\d{9}|(\+1)?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}", text))

    if not has_email:
        issues.append("No email address found")
        score -= 10
    if not has_phone:
        issues.append("No phone number found")
        score -= 5

    # Check length
    if word_count < 200:
        issues.append("Resume too short — less than 200 words")
        score -= 10
        tips.append("Add more detail to your experience and skills sections")
    elif word_count > 1200:
        issues.append("Resume too long — more than 1200 words")
        score -= 5
        tips.append("Trim to 1-2 pages for better ATS performance")

    # Check for LinkedIn
    if "linkedin" not in text_lower:
        tips.append("Add your LinkedIn profile URL")
        score -= 5

    # Check for GitHub (important for tech roles)
    if "github" not in text_lower:
        tips.append("Add your GitHub profile URL for tech roles")

    # Positive tips
    if has_email and has_phone:
        tips.append("Good — contact information is present")
    if word_count >= 200 and word_count <= 1200:
        tips.append("Good — resume length is appropriate")

    return {
        "ats_score":      max(0, min(100, score)),
        "sections_found": sections_found,
        "issues":         issues,
        "tips":           tips,
        "word_count":     word_count
    }