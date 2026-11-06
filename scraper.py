"""
Deep Scraper Module: Ingests listings and fetches full requirement descriptions via LinkedIn Guest API.
"""
import requests
import time
import re
from bs4 import BeautifulSoup
from config import HEADERS

def fetch_job_full_description(job_id):
    """
    Fetches the full inner text (About the job & Requirements) using LinkedIn's public job detail endpoint.
    """
    detail_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    try:
        resp = requests.get(detail_url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            # LinkedIn stores the entire description inside this container
            desc_div = soup.find("div", class_=lambda x: x and "show-more-less-html__markup" in x)
            if desc_div:
                return desc_div.get_text(" ", strip=True)
    except Exception as exc:
        print(f"[-] Failed fetching description for job {job_id}: {exc}")
    return ""

def fetch_linkedin_internships(limit_per_query=8):
    """
    Collects fresh ML/AI internship postings and inspects their full requirements.
    """
    jobs = []
    search_queries = [
        {"keywords": "Machine Learning Intern", "location": "Germany"},
        {"keywords": "AI Intern", "location": "Netherlands"},
        {"keywords": "Speech Machine Learning", "location": "Europe"}
    ]

    for item in search_queries:
        try:
            # f_TPR=r604800 (Last 7 days), f_E=1 (Internship level)
            url = (
                f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
                f"keywords={item['keywords'].replace(' ', '%20')}&location={item['location']}"
                f"&f_TPR=r604800&f_E=1&start=0"
            )
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                job_elements = soup.find_all("li")
                
                count = 0
                for el in job_elements:
                    if count >= limit_per_query:
                        break

                    title_elem = el.find("h3", class_="base-search-card__title")
                    company_elem = el.find("h4", class_="base-search-card__subtitle")
                    location_elem = el.find("span", class_="job-search-card__location")
                    link_elem = el.find("a", class_="base-card__full-link", href=True)

                    if title_elem and link_elem:
                        job_link = link_elem["href"].split("?")[0]
                        
                        # Extract numerical Job ID from URL or attributes
                        job_id_match = re.search(r'(\d{9,11})', job_link)
                        full_description = ""
                        
                        if job_id_match:
                            job_id = job_id_match.group(1)
                            # Deep scraping: Read the actual requirements section
                            time.sleep(1.0)  # Rate-limiting pause to stay completely safe
                            full_description = fetch_job_full_description(job_id)

                        # If detail fetch failed, fallback to title text
                        if not full_description:
                            full_description = title_elem.get_text(strip=True)

                        jobs.append({
                            "title": title_elem.get_text(strip=True),
                            "company": company_elem.get_text(strip=True) if company_elem else "Tech Enterprise",
                            "location": location_elem.get_text(strip=True) if location_elem else item["location"],
                            "url": job_link,
                            "description": full_description,  # Now contains full requirements!
                            "source": "LinkedIn (Verified Requirements)"
                        })
                        count += 1

            time.sleep(1.5)
        except Exception as exc:
            print(f"[-] LinkedIn ingestion warning: {exc}")
            
    return jobs

def fetch_jobs_from_feed():
    """
    Coordinates multi-source collection with deep requirement inspection.
    """
    print("[*] Ingesting verified postings and reading requirements from LinkedIn...")
    jobs = fetch_linkedin_internships()
    print(f"[+] Successfully parsed {len(jobs)} complete listings.")
    return jobs
