"""
Scraper Module: Aggregates B.Sc. AI/ML/Audio/Software internship postings from
LinkedIn (Germany & Netherlands), IAESTE SmartSimple, and ErasmusCareers.org.
"""
import os
import re
import time
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from config import HEADERS

load_dotenv()

# Titles rejected immediately before fetching full descriptions (saves requests & tokens)
PREFILTER_TITLE_BLOCKLIST = re.compile(
    r"\b(phd|doctorate|postdoc|afstudeerstage|afstudeeropdracht|graduation|thesis|master\s*thesis|stage|stagaire)\b",
    re.IGNORECASE,
)

EXCLUDED_LOCATIONS = ("france", "paris", "île-de-france", "lyon", "bordeaux", "toulouse", "annecy", "la ciotat")


def _get_headers(extra=None):
    headers = dict(HEADERS) if HEADERS else {}
    headers.setdefault(
        "User-Agent",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36",
    )
    headers.setdefault("Accept-Language", "en-US,en;q=0.9")
    if extra:
        headers.update(extra)
    return headers


def _fetch_linkedin_jobs(limit=45):
    """
    Fetches paginated internship and working-student postings across Germany
    and the Netherlands via LinkedIn's public guest endpoints (no cookie needed).
    """
    print("[*] Fetching from LinkedIn (Germany & Netherlands Internships)...")
    jobs = []
    seen_ids = set()

    # Targeted searches: Germany (Intern + Werkstudent) and Netherlands (Intern)
    search_plan = [
        ("Germany", "(Machine Learning OR AI OR Audio OR Speech) Intern", 2),
        ("Germany", "(Machine Learning OR AI OR Python) Werkstudent", 2),
        ("Netherlands", "(Machine Learning OR AI OR Audio OR Python) Intern", 2),
    ]

    for country, keywords, pages in search_plan:
        if len(jobs) >= limit:
            break

        query = quote_plus(keywords)
        location = quote_plus(country)

        for page in range(pages):
            if len(jobs) >= limit:
                break

            start = page * 10
            search_url = (
                "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
                f"?keywords={query}&location={location}&f_E=1&start={start}"
            )

            try:
                resp = requests.get(search_url, headers=_get_headers(), timeout=15)
                if resp.status_code != 200:
                    print(f"    [-] LinkedIn ({country}, page {page + 1}) returned HTTP {resp.status_code}.")
                    break

                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.find_all("li")
                if not cards:
                    break

                for card in cards:
                    if len(jobs) >= limit:
                        break

                    title_el = card.find("h3", class_="base-search-card__title")
                    company_el = card.find("h4", class_="base-search-card__subtitle")
                    loc_el = card.find("span", class_="job-search-card__location")
                    link_el = card.find("a", class_="base-card__full-link")

                    if not title_el or not link_el:
                        continue

                    title = title_el.get_text(strip=True)
                    company = company_el.get_text(strip=True) if company_el else "Unknown"
                    loc = loc_el.get_text(strip=True) if loc_el else country
                    job_url = link_el.get("href", "").split("?")[0]

                    # Skip France / excluded regions and obvious PhD/Thesis/Stage titles early
                    if any(ex in loc.lower() for ex in EXCLUDED_LOCATIONS):
                        continue
                    if PREFILTER_TITLE_BLOCKLIST.search(title):
                        continue

                    job_id_match = re.search(r"-(\d+)(?:/|$)", job_url)
                    job_id = job_id_match.group(1) if job_id_match else job_url
                    if job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)

                    # Pull full posting description directly without Selenium
                    description = ""
                    if job_id_match:
                        time.sleep(0.7)
                        detail_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
                        detail_resp = requests.get(detail_url, headers=_get_headers(), timeout=10)
                        if detail_resp.status_code == 200:
                            detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
                            desc_el = detail_soup.find("div", class_="show-more-less-html__markup")
                            if desc_el:
                                description = desc_el.get_text(separator=" ", strip=True)

                    jobs.append(
                        {
                            "title": title,
                            "company": company,
                            "location": loc,
                            "url": job_url,
                            "description": description or f"{title} at {company} ({loc})",
                            "source": f"LinkedIn ({country})",
                        }
                    )

                time.sleep(1.0)  # Respectful pause between search pages

            except Exception as exc:
                print(f"    [-] Warning: LinkedIn scrape failed for {country}: {exc}")
                break

    if not jobs:
        print("    [-] No active LinkedIn internship postings matched in Germany/Netherlands.")
    else:
        print(f"    [+] LinkedIn: {len(jobs)} pre-filtered postings collected (Germany & Netherlands).")

    return jobs


def _fetch_smartsimple_jobs(limit=20):
    """
    Fetches internship offers from IAESTE SmartSimple using SMARTSIMPLE_COOKIE from .env.
    """
    print("[*] Fetching from IAESTE SmartSimple...")
    jobs = []
    cookie = os.getenv("SMARTSIMPLE_COOKIE", "").strip()
    base_url = os.getenv(
        "SMARTSIMPLE_URL",
        "https://iaeste.smartsimple.ie/iface/ex/ax_index.jsp?lang=1",
    ).strip()

    if not cookie:
        print("    [-] SMARTSIMPLE_COOKIE not set in .env; skipping IAESTE SmartSimple.")
        return jobs

    cookie_header = cookie if "=" in cookie else f"JSESSIONID={cookie}"

    try:
        headers = _get_headers({"Cookie": cookie_header, "Referer": "https://iaeste.smartsimple.ie/"})
        resp = requests.get(base_url, headers=headers, timeout=15, allow_redirects=True)

        if resp.status_code != 200:
            print(f"    [-] IAESTE SmartSimple returned HTTP {resp.status_code}.")
            return jobs

        soup = BeautifulSoup(resp.text, "html.parser")
        if soup.find("input", {"type": "password"}) is not None:
            print("    [-] SmartSimple session cookie is invalid or expired (redirected to login).")
            return jobs

        for row in soup.find_all("tr"):
            cells = [c.get_text(" ", strip=True) for c in row.find_all("td")]
            row_text = " ".join(cells).strip()
            if len(row_text) < 25:
                continue

            link_el = row.find("a", href=True)
            offer_url = urljoin(base_url, link_el["href"]) if link_el else base_url
            title = link_el.get_text(strip=True) if link_el and link_el.get_text(strip=True) else cells[0]

            if len(title) < 4:
                continue

            jobs.append(
                {
                    "title": title,
                    "company": cells[1] if len(cells) > 1 and cells[1] else "IAESTE Employer",
                    "location": cells[2] if len(cells) > 2 and cells[2] else "Europe",
                    "url": offer_url,
                    "description": row_text,
                    "source": "IAESTE SmartSimple",
                }
            )
            if len(jobs) >= limit:
                break

        if not jobs:
            print("    [-] No open offers parsed from SmartSimple (check SMARTSIMPLE_URL if offers live on a subpage).")
        else:
            print(f"    [+] IAESTE SmartSimple: {len(jobs)} postings collected.")

    except Exception as exc:
        print(f"    [-] Warning: IAESTE SmartSimple scrape failed: {exc}")

    return jobs


def _fetch_erasmuscareers_jobs(limit=15):
    """
    Fetches traineeship postings from ErasmusCareers.org (Software & Data focus).
    """
    print("[*] Fetching from ErasmusCareers.org...")
    jobs = []
    base_url = "https://www.erasmuscareers.org/traineeships"

    try:
        headers = _get_headers(
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": "https://www.erasmuscareers.org/",
                "Upgrade-Insecure-Requests": "1",
            }
        )
        resp = requests.get(base_url, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"    [-] ErasmusCareers.org blocked or unavailable (HTTP {resp.status_code}).")
            return jobs

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("div", class_="views-row") or soup.find_all("article")

        for card in cards[:limit]:
            title_el = card.find(["h2", "h3", "h4"])
            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            if PREFILTER_TITLE_BLOCKLIST.search(title):
                continue

            link_el = title_el.find("a", href=True) or card.find("a", href=True)
            href = link_el["href"] if link_el else ""
            full_url = urljoin("https://www.erasmuscareers.org", href) if href else base_url
            card_text = card.get_text(separator=" ", strip=True)

            if any(ex in card_text.lower() for ex in EXCLUDED_LOCATIONS):
                continue

            jobs.append(
                {
                    "title": title,
                    "company": "Erasmus+ Host",
                    "location": "Europe",
                    "url": full_url,
                    "description": card_text,
                    "source": "ErasmusCareers.org",
                }
            )

        if not jobs:
            print("    [-] No matching traineeship postings found on ErasmusCareers.org.")
        else:
            print(f"    [+] ErasmusCareers.org: {len(jobs)} postings collected.")

    except Exception as exc:
        print(f"    [-] Warning: ErasmusCareers.org scrape failed: {exc}")

    return jobs


def fetch_jobs_from_feed(limit=45):
    """
    Aggregates internship postings from LinkedIn (DE/NL), IAESTE SmartSimple,
    and ErasmusCareers.org into a single unified list.
    """
    all_jobs = []

    all_jobs.extend(_fetch_linkedin_jobs(limit=limit))
    time.sleep(1)
    all_jobs.extend(_fetch_smartsimple_jobs(limit=20))
    time.sleep(1)
    all_jobs.extend(_fetch_erasmuscareers_jobs(limit=15))

    if not all_jobs:
        print("\n[!] Status: No active internship postings were collected across configured sources today.")

    return all_jobs
