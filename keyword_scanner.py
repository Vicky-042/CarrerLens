import re
import nltk
from nltk.corpus import stopwords

# Download stopwords
nltk.download('stopwords', quiet=True)
STOPWORDS = set(stopwords.words('english'))

# Extended stopwords for better filtering
EXTENDED_STOPWORDS = STOPWORDS.union({
    'offer', 'opportunities', 'seeking', 'apply', 'send', 'careers', 'email',
    'available', 'remote', 'job', 'position', 'role', 'company', 'please',
    'requirements', 'skills', 'experience', 'work', 'team', 'year', 'years',
    'type', 'time', 'ability', 'benefits', 'salary', 'location', 'per',
    'day', 'week', 'month', 'development', 'professional', 'work', 'quality'
})

# Tech keywords that should be kept (even if short)
TECH_KEYWORDS = {
    'api', 'aws', 'css', 'html', 'sql', 'git', 'ci', 'cd', 'ml', 'ai',
    'iot', 'rpa', 'etl', 'elk', 'oops', 'ddd', 'tdd', 'bdd', 'uml', 'jwt'
}

def is_valid_keyword(word):
    """Check if word should be included as keyword"""
    # Keep tech keywords regardless of length
    if word in TECH_KEYWORDS:
        return True
    
    # Reject numbers
    if word.isdigit():
        return False
    
    # Reject if mostly numbers
    if sum(c.isdigit() for c in word) / len(word) > 0.5:
        return False
    
    # Must be at least 3 chars (unless tech keyword)
    if len(word) < 3:
        return False
    
    # Reject if contains multiple numbers (like 120000, 160000)
    if len(re.findall(r'\d', word)) > 2:
        return False
    
    return True

def clean_text(text):
    text = text.lower()
    # Keep alphanumeric, hyphens, dots (for versions like 3.9)
    text = re.sub(r'[^a-z0-9\s\-\.]', '', text)
    # Remove multiple spaces and split
    words = text.split()
    # Filter: remove extended stopwords and invalid keywords
    words = [word for word in words if word not in EXTENDED_STOPWORDS and is_valid_keyword(word)]
    return words

def scan_resume_vs_jd(resume_text, jd_text):
    resume_words = set(clean_text(resume_text))
    jd_words = set(clean_text(jd_text))
    
    # Common & missing keywords
    common = jd_words.intersection(resume_words)
    missing = jd_words - resume_words
    
    # Calculate match score
    match_score = (len(common) / len(jd_words) * 100) if jd_words else 0
    
    # Calculate keyword categories
    tech_missing = {w for w in missing if w in TECH_KEYWORDS or any(tech in w for tech in ['python', 'java', 'node', 'react', 'angular', 'vue', 'django', 'flask', 'spring'])}
    
    other_missing = missing - tech_missing
    
    return round(match_score, 2), list(common), list(missing), list(tech_missing), list(other_missing)