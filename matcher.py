"""
Matcher & Evaluation Engine:
Stage 1: Zero-cost Python regex pre-filtering (exclusions & language rules).
Stage 2: Claude Haiku semantic scoring for shortlisted postings.
"""
import json
import os
import re
from anthropic import Anthropic
from dotenv import load_dotenv
from config import USER_PROFILE

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=api_key) if api_key else None
MODEL_NAME = "claude-haiku-5-5"


def _score_with_claude(title, company, location, description, base_score):
    """Uses Claude Haiku to evaluate role fit and return (score, reason)."""
    if not client or len(description) < 40:
        return base_score, "Heuristic score applied (API skipped or short description)."

    skills_str = ", ".join(USER_PROFILE["skills"])
    prompt = f"""You are a strict technical recruiter evaluating an internship posting for a 3rd-year B.Sc. Computer Engineering student with an EU (Hungarian) passport (no visa sponsorship needed in Europe).

Candidate Skills: {skills_str}
Target: Summer 2027 ML / AI / Audio / Software Engineering Internship in Europe.
Hard Rejections: PhD/Master-only roles, mandatory full-time thesis (afstudeerstage), or Spring/Winter 2027 start dates.

Job Title: {title}
Company: {company}
Location: {location}
Description:
{description[:2000]}

Respond ONLY with valid JSON in this exact format:
{{"score": <integer 0-100>, "reason": "<one concise sentence explaining the fit or mismatch>"}}"""

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = next(
            (block.text for block in response.content if block.type == "text"), ""
        ).strip()

        # Clean potential markdown code fences if returned
        raw_text = re.sub(r"^```(?:json)?|```$", "", raw_text, flags=re.MULTILINE).strip()
        data = json.loads(raw_text)

        ai_score = max(0, min(100, int(data.get("score", base_score))))
        reason = str(data.get("reason", "Evaluated by Claude Haiku.")).strip()
        return ai_score, reason

    except Exception as e:
        return base_score, f"Fallback heuristic score (API error: {type(e).__name__})"


def evaluate_job(job, use_ai=True):
    """
    Evaluates job suitability by enforcing:
    1. Graduation/Thesis/Spring exclusions.
    2. Conditional language requirements (allows C#/Rust only if Python is present).
    3. Accurate regex-based skill detection + optional Claude Haiku reasoning.
    """
    title = job.get("title", "").strip()
    description = job.get("description", "").strip()
    full_text = f"{title} {description}".lower()
    title_lower = title.lower()

    # Rule 1: Exclude generic single-word titles
    if title_lower in ["engineer", "developer", "software engineer"]:
        return None

    # Rule 2: Hard blacklist check
    for forbidden in USER_PROFILE["blacklist_keywords"]:
        pattern = r"\b" + re.escape(forbidden) + r"\b"
        if re.search(pattern, full_text):
            return None

    # Rule 3: Ensure role aligns with student/intern relevance
    is_relevant_role = any(
        keyword in title_lower
        for keyword in USER_PROFILE["mandatory_title_keywords"]
    )
    if not is_relevant_role:
        return None

    # Rule 4: Conditional language filter
    has_unpreferred = any(
        re.search(r"\b" + re.escape(lang) + r"\b", full_text)
        for lang in USER_PROFILE["unpreferred_languages"]
    )
    has_python = bool(re.search(r"\bpython\b", full_text))

    if has_unpreferred and not has_python:
        return None

    # Rule 5: Skill boundary matching
    matched_skills = []
    missing_skills = []

    for skill in USER_PROFILE["skills"]:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, full_text):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    # Stage 1: Base heuristic score
    score = 40
    if any(k in title_lower for k in ["machine learning", "ai", "speech", "audio", "data"]):
        score += 25
    if any(k in title_lower for k in ["intern", "internship", "working student", "student"]):
        score += 20
    if any(k in full_text for k in USER_PROFILE["summer_boost_keywords"]):
        score += 15

    score += len(matched_skills) * 5
    score = min(100, score)

    company = job.get("company", "Tech Enterprise")
    location = job.get("location", "Europe / Remote")
    ai_reason = "Heuristic match."

    # Stage 2: Semantic evaluation with Claude Haiku
    if use_ai:
        score, ai_reason = _score_with_claude(
            title=title,
            company=company,
            location=location,
            description=description,
            base_score=score,
        )

    return {
        "title": title,
        "company": company,
        "location": location,
        "url": job.get("url", "#"),
        "source": job.get("source", "Aggregator"),
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills[:4],
        "ai_reason": ai_reason,
    }
