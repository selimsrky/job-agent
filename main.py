"""
Main Execution Script: Coordinates scraping, matching, and HTML dashboard rendering.
"""
import webbrowser
import os
from scraper import fetch_jobs_from_feed
from matcher import evaluate_job

def generate_html_report(evaluated_jobs, filename="report.html"):
    """
    Builds a clean, dark-themed HTML report displaying matched positions.
    """
    cards_html = ""
    for job in evaluated_jobs:
        matched_tags = "".join([f'<span class="badge match">{s}</span>' for s in job["matched_skills"]])
        missing_tags = "".join([f'<span class="badge miss">{s}</span>' for s in job["missing_skills"]])
        
        cards_html += f"""
        <div class="card">
            <div class="header">
                <div>
                    <h2 class="job-title">{job['title']}</h2>
                    <div class="company-info">{job['company']} • <span class="location">{job['location']}</span></div>
                </div>
                <div class="score-badge">%{job['score']} Match</div>
            </div>
            
            <div class="skill-row"><span class="label">Matched Competencies:</span> {matched_tags if matched_tags else '<span>General Domain Fit</span>'}</div>
            <div class="skill-row"><span class="label">Growth Areas:</span> {missing_tags}</div>

            <div class="footer">
                <span class="source-tag">Source: {job['source']}</span>
                <a href="{job['url']}" target="_blank" class="apply-btn">View & Apply ↗</a>
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Career Agent • Opportunity Feed</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b1120; color: #f1f5f9; margin: 0; padding: 30px 15px; }}
        .container {{ max-width: 820px; margin: auto; }}
        h1 {{ font-size: 22px; margin: 0 0 4px 0; color: #38bdf8; font-weight: 700; }}
        p.subtitle {{ color: #94a3b8; margin: 0 0 20px 0; font-size: 13px; }}
        .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; }}
        .header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }}
        .job-title {{ font-size: 16px; margin: 0 0 2px 0; color: #ffffff; font-weight: 600; }}
        .company-info {{ font-size: 13px; color: #94a3b8; }}
        .location {{ color: #38bdf8; }}
        .score-badge {{ background: #0284c7; color: #ffffff; font-weight: 700; padding: 3px 10px; border-radius: 12px; font-size: 12px; white-space: nowrap; }}
        .skill-row {{ font-size: 12px; margin-top: 6px; display: flex; flex-wrap: wrap; align-items: center; gap: 4px; }}
        .skill-row .label {{ color: #64748b; font-weight: 600; margin-right: 4px; }}
        .badge {{ font-size: 11px; padding: 2px 6px; border-radius: 4px; }}
        .badge.match {{ background: #083344; color: #67e8f9; border: 1px solid #0891b2; }}
        .badge.miss {{ background: #3b0717; color: #fda4af; border: 1px solid #9f1239; }}
        .footer {{ display: flex; justify-content: space-between; align-items: center; margin-top: 10px; padding-top: 8px; border-top: 1px solid #334155; font-size: 11px; }}
        .source-tag {{ color: #64748b; }}
        .apply-btn {{ background: #38bdf8; color: #0f172a; text-decoration: none; font-weight: 700; padding: 5px 12px; border-radius: 6px; font-size: 12px; transition: background 0.2s; }}
        .apply-btn:hover {{ background: #7dd3fc; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Career Agent: Curated Opportunities</h1>
        <p class="subtitle">Filtered strictly for Summer 2027 Internships (Graduation/Thesis projects and Spring off-cycles excluded)</p>
        {cards_html if cards_html else '<p style="color:#ef4444;">No postings met the criteria. All graduation projects and off-cycle listings were filtered out.</p>'}
    </div>
</body>
</html>"""

    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)
    print(f"\n[+] Report generated successfully: {filename}")

def main():
    print("=" * 60)
    print("   AI CAREER AGENT: Ingesting & Evaluating Roles...")
    print("=" * 60)

    raw_jobs = fetch_jobs_from_feed()
    print(f"[+] Total raw opportunities collected: {len(raw_jobs)}")

    evaluated_jobs = []
    for job in raw_jobs:
        evaluated = evaluate_job(job)
        if evaluated:
            evaluated_jobs.append(evaluated)

    evaluated_jobs.sort(key=lambda x: x["score"], reverse=True)
    top_jobs = evaluated_jobs[:15]

    print(f"[+] Verified Summer 2027 positions identified: {len(top_jobs)}\n")
    for idx, item in enumerate(top_jobs, 1):
        print(f" {idx}. [{item['score']}%] {item['title']} @ {item['company']} ({item['location']})")

    generate_html_report(top_jobs)
    webbrowser.open("file://" + os.path.realpath("report.html"))

if __name__ == "__main__":
    main()
