"""
Configuration and Technical Candidate Profile Specification.
Contains filtering rules, technical skills, and candidate metadata for Selim Sarıkaya.
"""

USER_PROFILE = {
    "name": "Selim Sarıkaya",
    "degree": "B.Sc. in Computer Engineering (Undergraduate, MEF University)",
    "citizenship": "Hungarian & Turkish Citizen (EU Passport)",
    
    # Target roles for automated ingestion
    "target_roles": [
        "Machine Learning Intern",
        "AI Engineer Intern",
        "Audio AI Intern",
        "Speech Recognition Intern",
        "NLP / LLM Intern",
        "Python Developer Intern",
        "Software Engineering Intern"
    ],

    # Core technical skills extracted directly from Resume
    "skills": [
        # Programming & Core Foundations
        "python", "pytorch", "c++", "java", "sql", "linux", "bash",
        # Audio & Speech AI Domain
        "librosa", "whisper", "speech recognition", "dsp", "digital signal processing",
        "stft", "spectrogram", "mel-spectrogram", "ffmpeg", "audio classification",
        # Machine Learning, Deep Learning & NLP
        "deep learning", "machine learning", "cnn", "2d cnn", "nlp", "nlg",
        "large language models", "llm", "knowledge graphs", "neo4j", "sparql", "wikidata",
        "scikit-learn", "numpy", "pandas",
        # DevOps & Engineering
        "docker", "git", "github", "containerization", "rest api"
    ],

    # Allowed role keywords in job titles to ensure student/intern level relevance
    "mandatory_title_keywords": [
        "intern", "internship", "trainee", "praktikum", "praktikant", "student", 
        "working student", "werkstudent", "junior", "engineer", "developer", 
        "machine learning", "ml", "ai", "data", "software", "research"
    ],

    # Excluded keywords: Filters out senior positions, irrelevant fields, and off-cycle / long-term dates
    "blacklist_keywords": [
        # Off-cycle spring start dates and long commitments (incompatible with academic calendar)
        "february", "feb 2027", "spring 2027", "start: february", "starting in february",
        "6 months", "six months", "full year", "12 months", "one year",
        # Non-engineering and operational departments
        "social media", "marketing", "sales", "recruiter", "talent acquisition",
        "human resources", "compliance", "accountant", "receptionist", "content creator",
        # Seniority and tenure levels unsuitable for undergraduates
        "phd", "doctorate", "postdoc", "senior", "lead", "principal", "staff engineer",
        "5+ years", "7+ years", "10+ years"
    ],

    # Target keywords for preferred summer internship window (June - September/October 2027)
    "summer_boost_keywords": [
        "summer", "summer 2027", "june", "july", "august", "3 months", "three months", "summer intern"
    ],

    # Priority target locations across Europe and remote ecosystems
    "allowed_locations": [
        "remote", "europe", "germany", "deutschland", "netherlands", "amsterdam",
        "berlin", "munich", "worldwide", "eu", "anywhere", "switzerland", "austria"
    ]
}

# Emulated browser headers to avoid automated scraping rejections
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
