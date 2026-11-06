"""
Matcher & Evaluation Engine: Evaluates postings with strict exclusion and conditional language checks.
"""
import re
from config import USER_PROFILE

def evaluate_job(job):
    """
    Evaluates job suitability by enforcing:
    1. Graduation/Thesis/Spring exclusions.
    2. Conditional language requirements (allows C#/Rust only if Python is present).
    3. Accurate regex-based skill detection and scoring.
    """
    title = job.get("title", "").strip()
    description = job.get("description", "").strip()
    full_text = f"{title} {description}".lower()
    title_lower = title.lower()

    # Rule 1: Exclude generic single-word titles
    if title_lower in ["engineer", "developer", "software engineer"]:
        return None

    # Rule 2: Hard blacklist check (Graduation projects, PhD, Spring dates, 6-month commitments)
    for forbidden in USER_PROFILE["blacklist_keywords"]:
        pattern = r'\b' + re.escape(forbidden) + r'\b'
        if re.search(pattern, full_text):
            return None

    # Rule 3: Ensure role aligns with student/intern relevance
    is_relevant_role = any(
        keyword in title_lower 
        for keyword in USER_PROFILE["mandatory_title_keywords"]
    )
    if not is_relevant_role:
        return None

    # Rule 4: Conditional language filter (e.g., C# allowed ONLY IF Python is also present)
    has_unpreferred = any(
        re.search(r'\b' + re.escape(lang) + r'\b', full_text) 
        for lang in USER_PROFILE["unpreferred_languages"]
    )
    has_python = bool(re.search(r'\bpython\b', full_text))
    
    if has_unpreferred and not has_python:
        return None

    # Rule 5: Skill boundary matching
    matched_skills = []
    missing_skills = []

    for skill in USER_PROFILE["skills"]:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, full_text):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    # Base scoring logic
    score = 40

    if any(k in title_lower for k in ["machine learning", "ai", "speech", "audio", "data"]):
        score += 25
    if any(k in title_lower for k in ["intern", "internship", "working student", "student"]):
        score += 20
    if any(k in full_text for k in USER_PROFILE["summer_boost_keywords"]):
        score += 15

    score += len(matched_skills) * 5
    score = min(100, score)

    return {
        "title": title,
        "company": job.get("company", "Tech Enterprise"),
        "location": job.get("location", "Europe / Remote"),
        "url": job.get("url", "#"),
        "source": job.get("source", "Aggregator"),
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills[:4]
    }
