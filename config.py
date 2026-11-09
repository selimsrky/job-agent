"""
Configuration and Technical Candidate Profile Specification.
Includes strict graduation/off-cycle exclusions and candidate preferences.
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

    # Secondary languages: acceptable ONLY IF Python is also supported as an alternative
    "unpreferred_languages": ["c#", ".net", "golang", "ruby", "rust"],

    # Mandatory title keywords to enforce student/intern scope
    "mandatory_title_keywords": [
        "intern", "internship", "trainee", "praktikum", "praktikant", "student", 
        "working student", "werkstudent", "junior", "engineer", "developer", 
        "machine learning", "ml", "ai", "data", "software", "research"
    ],

    # Hard blacklist: Exclude thesis/graduation roles, off-cycle spring starts, and senior roles
    "blacklist_keywords": [
        # Dutch/German thesis and graduation projects (incompatible with 3-month summer internship)
        "graduation assignment", "graduation project", "graduation thesis", 
        "afstudeerstage", "afstuderen", "master thesis", "bachelor thesis", 
        "master's thesis", "diplomarbeit", "thesis internship", "thesis project",

        # Off-cycle spring/winter start dates and long commitments
        "january", "february", "march", "april", "spring 2027", "winter 2027",
        "start: february", "starting in february", "start: march", "starting in march",
        "6 months", "six months", "full year", "12 months", "one year",

        # Non-engineering and operational departments
        "social media", "marketing", "sales", "recruiter", "talent acquisition",
        "human resources", "compliance", "accountant", "receptionist", "content creator",

        # Seniority and tenure levels unsuitable for undergraduates
        "phd", "doctorate", "postdoc", "senior", "lead", "principal", "staff engineer",
        "5+ years", "7+ years", "10+ years"
    ],

    # Priority target summer keywords (June - September/October window)
    "summer_boost_keywords": [
        "summer", "summer 2027", "june", "july", "august", "3 months", "three months", "summer intern"
    ],

    # Regional target locations across Europe and remote ecosystems
    "allowed_locations": [
        "remote", "europe", "germany", "deutschland", "netherlands", "amsterdam",
        "berlin", "munich", "worldwide", "eu", "anywhere", "switzerland", "austria"
    ]
}

# Emulated browser headers to avoid automated scraping blocks
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
