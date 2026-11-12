# Job Agent (Autonomous Career CLI & Matcher)

An automated Python job scraper and profile matching engine designed to track machine learning, audio AI, and developer internship opportunities across open remote feeds.

## Overview
- **Feed Ingestion:** Collects recent postings with automated headers and rate-limiting.
- **Competency Matching:** Evaluates postings against target skills (PyTorch, Whisper, Librosa, Knowledge Graphs, Docker) and filters out senior or PhD requirements.
- **Dashboard Reporting:** Generates a lightweight, dark-themed HTML report (`report.html`) with direct application links.

## Project Structure
```text
job-agent/
├── config.py       # Profile parameters, skills, and exclusion rules
├── scraper.py      # HTTP request ingestion logic
├── matcher.py      # Scoring logic and keyword verification
├── main.py         # Orchestrator and HTML report generator
├── requirements.txt
└── README.md

## Filtering & Scoring Logic

- **Academic Calendar Guard:** Automatically discards off-cycle spring/winter start dates (February, March, 6 months) and Dutch/German graduation thesis assignments (Afstudeerstage, Master's Thesis).
- **Conditional Language Matching:** Secondary languages (e.g., C#, Rust) are permitted only when Python is also listed as an accepted stack.
- **Weighted Alignment Score:** Ranks opportunities (0–100%) based on core ML/Audio competencies (PyTorch, Whisper, Librosa, Docker) and Summer 2027 keywords.

