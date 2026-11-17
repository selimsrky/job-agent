"""
Scraper Module: Gathers postings using a hybrid approach.
Integrates authenticated LinkedIn scraping via Playwright.
"""
import requests
import time
import os
import json
from dotenv import load_dotenv
from config import HEADERS
from playwright.sync_api import sync_playwright

load_dotenv()

def fetch_jobs_from_feed(limit=30):
    jobs = []
    
    # 1. Remotive & Arbeitnow (Fast open APIs via standard requests)
    try:
        resp = requests.get("https://remotive.com/api/remote-jobs?category=software-dev&limit=10", headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            for item in resp.json().get("jobs", []):
                jobs.append({
                    "title": item.get("title", ""), "company": item.get("company_name", ""),
                    "location": item.get("candidate_required_location", ""), "url": item.get("url", "#"),
                    "description": item.get("description", ""), "source": "Remotive"
                })
    except:
        pass

    try:
        resp = requests.get("https://www.arbeitnow.com/api/job-board-api", headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            for item in resp.json().get("data", [])[:10]:
                jobs.append({
                    "title": item.get("title", ""), "company": item.get("company_name", ""),
                    "location": item.get("location", ""), "url": item.get("url", "#"),
                    "description": item.get("description", ""), "source": "Arbeitnow"
                })
    except:
        pass

    # =======================================================
    # PLAYWRIGHT (LINKEDIN INFILTRATION)
    # =======================================================
    linkedin_cookie = os.getenv("LINKEDIN_SESSION_COOKIE")
    
    if linkedin_cookie:
        print("[*] Firing up Playwright for authenticated LinkedIn scraping...")
        try:
            with sync_playwright() as p:
                # headless=True runs the browser silently in the background
                browser = p.chromium.launch(headless=True) 
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    viewport={'width': 1280, 'height': 720}
                )
                
                # Inject the session cookie to bypass login and Cloudflare
                context.add_cookies([{
                    "name": "li_at",
                    "value": linkedin_cookie,
                    "domain": ".linkedin.com",
                    "path": "/"
                }])
                
                page = context.new_page()
                
                # Search query: Machine Learning Intern in Europe (Past month)
                search_url = "https://www.linkedin.com/jobs/search/?keywords=Machine%20Learning%20Intern&location=Europe&f_TPR=r2592000"
                print("    -> Navigating to LinkedIn Jobs directory...")
                page.goto(search_url, wait_until="domcontentloaded")
                time.sleep(4) # Allow DOM elements to fully render
                
                print("    -> Extracting job cards from the feed...")
                # Locate job cards based on LinkedIn's current HTML structure
                job_cards = page.locator(".job-card-container").all()[:10] 
                
                for card in job_cards:
                    try:
                        # Click the card to load the full description in the right-side panel
                        card.click()
                        time.sleep(2)
                        
                        title = card.locator(".job-card-list__title").inner_text(timeout=2000)
                        company = card.locator(".job-card-container__primary-description").inner_text(timeout=2000)
                        
                        # Extract the full job description from the right panel for ML skill matching
                        desc_box = page.locator("#job-details")
                        description = desc_box.inner_text(timeout=2000) if desc_box.count() > 0 else ""
                        
                        jobs.append({
                            "title": title.strip(),
                            "company": company.strip(),
                            "location": "Europe (LinkedIn)",
                            "url": search_url,
                            "description": description.strip(),
                            "source": "LinkedIn"
                        })
                    except Exception as e:
                        # Skip minor extraction errors and proceed to the next card silently
                        continue 
                
                print(f"    [+] LinkedIn extraction complete. Grabbed target postings.")
                browser.close()
        except Exception as e:
            print(f"[-] Playwright LinkedIn error: {e}")
    else:
        print("[-] Notice: LINKEDIN_SESSION_COOKIE not found in .env, skipping LinkedIn.")

    return jobs
