import os
import sys
from datetime import datetime
import pytz
import requests

# Set console output encoding to UTF-8 to prevent crashes when printing emojis on Windows terminals
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


# =====================================================================
# LEARNING NOTE: What are imports?
# Imports let us use code written by others.
# - 'os' helps python talk to your computer's operating system (like getting secrets).
# - 'requests' is a library used to fetch data from websites or web APIs.
# - 'datetime' and 'pytz' help us handle dates and times (like Swiss timezone).
# =====================================================================

# Get API credentials from environment variables (Secrets)
# When we run locally, we can set these. On GitHub, GitHub Actions will set them.
ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

# Target Swiss cities / cantons to filter by (excluding Zurich to focus on Geneva, Vaud, Fribourg)
TARGET_LOCATIONS = ["geneva", "genève", "vaud", "lausanne", "fribourg"]

# Target terms we want to query
SEARCH_QUERIES = [
    "FATCA",
    "CRS",
    "AI governance",
    "AI law",
    "AI banking",
    "Artificial Intelligence banking",
    "AI compliance"
]


def run_demo_mode():
    """
    If you don't have API keys yet, this function runs to show you what the
    output looks like. This is called 'Mocking' or 'Demo Mode' in coding!
    """
    print("\n⚠️ Running in DEMO MODE because Adzuna API keys are not set.")
    print("Sign up at https://developer.adzuna.com/ to get your real keys.\n")

    # Sample mock data mimicking what the Adzuna API returns
    mock_jobs = [
        {
            "title": "Compliance Officer - FATCA & CRS Specialist",
            "company": {"display_name": "Lombard Odier"},
            "location": {"display_name": "Geneva, Switzerland"},
            "description": "We are seeking a senior compliance professional specialized in FATCA and CRS reporting regulations for our private banking division in Geneva.",
            "redirect_url": "https://example.com/apply/1",
            "created": "2026-06-07T12:00:00Z"
        },
        {
            "title": "Legal Counsel - AI Governance & Tech Law",
            "company": {"display_name": "Deloitte Switzerland"},
            "location": {"display_name": "Zurich, Switzerland"},
            "description": "Join our regulatory and legal advisory team. You will advise major banking clients on AI governance frameworks, legal compliance, and EU AI Act implications.",
            "redirect_url": "https://example.com/apply/2",
            "created": "2026-06-07T14:30:00Z"
        },
        {
            "title": "AI Product Manager - Wealth Management",
            "company": {"display_name": "UBS"},
            "location": {"display_name": "Lausanne, Vaud"},
            "description": "Drive the integration of Generative AI tools in our wealth management services. Collaboration with compliance and risk teams on AI policy is required.",
            "redirect_url": "https://example.com/apply/3",
            "created": "2026-06-06T09:15:00Z"
        }
    ]
    write_markdown_report(mock_jobs)


def fetch_jobs_from_adzuna(query):
    """
    Fetches job listings from the Adzuna API for a specific search query.
    """
    # Adzuna API endpoint for Switzerland ('ch')
    url = f"https://api.adzuna.com/v1/api/jobs/ch/search/1"
    
    # URL parameters sent to the API
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": query,
        "results_per_page": 20  # Number of results per query page
    }

    headers = {
        "Accept": "application/json"
    }

    try:
        # Send a GET request to the Adzuna API
        response = requests.get(url, params=params, headers=headers)
        
        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])
        else:
            print(f"Error fetching '{query}': API returned status code {response.status_code}")
            print(f"Details: {response.text}")
            return []
    except Exception as e:
        print(f"An unexpected error occurred while fetching '{query}': {e}")
        return []


def fetch_jobs_from_google_organic(query):
    """
    Fetches job listings from Google Search via SerpApi (organic search),
    which is cloud-friendly and works perfectly in Europe/Switzerland.
    """
    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "hl": "en",
        "gl": "ch"  # Switzerland
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            raw_results = data.get("organic_results", [])
            
            normalized_jobs = []
            for item in raw_results:
                title = item.get("title", "Untitled Job")
                link = item.get("link", "#")
                snippet = item.get("snippet", "No description available.")
                
                # Exclude generic search engine listing pages (e.g., search landing pages)
                if any(x in link.lower() for x in ["/vacancies/?", "q-fatca", "/search/?", "jobs-fatca", "/jobs/search"]):
                    continue

                # Clean up the title and extract company name where possible
                company_name = "Unknown Company"
                job_title = title
                
                if " hiring " in title:
                    parts = title.split(" hiring ")
                    company_name = parts[0].strip()
                    job_title = parts[1].strip()
                elif " at " in title:
                    parts = title.split(" at ")
                    job_title = parts[0].strip()
                    company_name = parts[1].strip()
                elif " - " in title:
                    parts = title.split(" - ")
                    job_title = parts[0].strip()
                    company_name = parts[1].strip() if len(parts) > 1 else "Unknown Company"

                company_name = company_name.replace("...", "").strip()
                job_title = job_title.replace("...", "").strip()

                normalized_jobs.append({
                    "id": link,
                    "title": job_title,
                    "company": {"display_name": company_name},
                    "location": {"display_name": "Geneva / Vaud / Fribourg (Google Search)"},
                    "description": snippet,
                    "redirect_url": link
                })
            return normalized_jobs
        else:
            print(f"Error fetching '{query}' from Google Search: API returned status code {response.status_code}")
            return []
    except Exception as e:
        print(f"An unexpected error occurred while fetching '{query}' from Google Search: {e}")
        return []


def is_target_job(job):
    """
    Filters jobs based on our target locations and relevant keywords.
    """
    # 1. Location check
    # We combine the job's display location and area list into a single lowercase string
    location_info = ""
    if "location" in job:
        location_info += job["location"].get("display_name", "").lower()
        if "area" in job["location"]:
            location_info += " " + " ".join(job["location"]["area"]).lower()
            
    # Check if any of our target cities (e.g. Geneva, Zurich) are in the location info
    has_target_location = any(loc in location_info for loc in TARGET_LOCATIONS)
    if not has_target_location:
        return False

    # 2. Company or Description Check
    # We want to make sure it's related to compliance/tax (FATCA, CRS) OR AI jobs specifically related to legal, law, or tax.
    title = job.get("title", "").lower()
    description = job.get("description", "").lower()
    company = job.get("company", {}).get("display_name", "").lower()
    
    combined_text = f"{title} {description} {company}"
    
    # Check if the job matches FATCA or CRS (tax compliance, so by definition legal/tax)
    is_tax_compliance = "fatca" in combined_text or "crs" in combined_text
    
    # Check if the job matches AI keywords
    is_ai_job = any(kw in combined_text for kw in ["ai ", "artificial intelligence", "intelligence artificielle", "generative ai", "genai", "llm"])
    
    # For AI jobs, they must also be related to legal, law, compliance, or tax
    legal_tax_keywords = [
        "legal", "law", "tax", "compliance", "governance", "regulatory", "droit", 
        "fiscalité", "juridique", "impôt", "ethics", "éthique", "policy", "reglementation"
    ]
    is_legal_or_tax_ai = is_ai_job and any(keyword in combined_text for keyword in legal_tax_keywords)
    
    # The job is valid if it is either a tax compliance job OR a legal/tax-related AI job
    if not (is_tax_compliance or is_legal_or_tax_ai):
        return False

    # Exclusion check: avoid Swiss Red Cross ("CRS" / Croix-Rouge Suisse) healthcare false positives
    exclusion_keywords = [
        "santé", "ems", "soins", "infirmier", "infirmière", "medical", "médical",
        "health", "auxiliaire de santé", "croix-rouge", "clinique", "care assistant",
        "nurse", "patient", "médecin", "hospitalier", "dentaire", "thérapeute",
        "soignant", "soignante", "aide soignant", "aide-soignant", "aide"
    ]
    if any(ex in combined_text for ex in exclusion_keywords):
        return False

    return True


def write_markdown_report(jobs):
    """
    Takes a list of jobs, formats them beautifully in Markdown, and writes it to a file.
    """
    # Get the current time in Switzerland
    swiss_tz = pytz.timezone("Europe/Zurich")
    now_swiss = datetime.now(swiss_tz).strftime("%Y-%m-%d %H:%M:%S")

    # Start constructing the markdown content
    markdown = []
    markdown.append("# 🇨🇭 Swiss Regulatory & AI Jobs Report")
    markdown.append(f"Last updated: `{now_swiss} (Geneva Time)`\n")
    
    if not jobs:
        markdown.append("No active job postings found matching the criteria today.")
    else:
        markdown.append(f"Found **{len(jobs)}** relevant job postings in Geneva, Vaud, and Fribourg.\n")
        markdown.append("---")
        
        for idx, job in enumerate(jobs, 1):
            title = job.get("title", "Untitled Job")
            company = job.get("company", {}).get("display_name", "Unknown Company")
            location = job.get("location", {}).get("display_name", "Switzerland")
            description = job.get("description", "No description available.")
            link = job.get("redirect_url", "#")
            
            # Clean description of HTML tags if any
            clean_desc = description.replace("<b>", "").replace("</b>", "").replace("<strong >", "").replace("</strong>", "")
            
            markdown.append(f"### {idx}. {title}")
            markdown.append(f"**🏢 Company:** {company} | **📍 Location:** {location}")
            markdown.append(f"**📝 Description:** {clean_desc}")
            markdown.append(f"[🔗 View & Apply here]({link})")
            markdown.append("\n---")
            
    report_content = "\n".join(markdown)
    
    # Save the report to a markdown file
    output_filename = "jobs_report.md"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"✅ Successfully wrote report with {len(jobs)} jobs to {output_filename}!")


def main():
    has_adzuna = ADZUNA_APP_ID and ADZUNA_APP_KEY
    has_serpapi = SERPAPI_KEY

    # If the user hasn't set any credentials, run the script in Demo Mode
    if not has_adzuna and not has_serpapi:
        run_demo_mode()
        sys.exit(0)

    all_jobs = []
    seen_job_ids = set()
    seen_titles_companies = set()

    # 1. Search Adzuna if keys are available
    if has_adzuna:
        print("🚀 Starting job search on Adzuna Switzerland...")
        for query in SEARCH_QUERIES:
            print(f"Adzuna: Searching for '{query}'...")
            results = fetch_jobs_from_adzuna(query)
            
            for job in results:
                job_id = job.get("id")
                title = job.get("title", "").lower().strip()
                company = job.get("company", {}).get("display_name", "").lower().strip()
                dedup_key = (title, company)
                
                if job_id not in seen_job_ids and dedup_key not in seen_titles_companies:
                    seen_job_ids.add(job_id)
                    seen_titles_companies.add(dedup_key)
                    if is_target_job(job):
                        all_jobs.append(job)

    # 2. Search Google Search via SerpApi if key is available
    if has_serpapi:
        print("🚀 Starting job search on Google Search (SerpApi)...")
        # Query specifically targeted site indexes for compliance/AI jobs in the regions
        google_queries = [
            "FATCA OR CRS (Geneva OR Vaud OR Fribourg) (site:linkedin.com/jobs/view/ OR site:jobs.ch/en/vacancies/detail/ OR site:careers.pictet.com OR site:careers.lombardodier.com OR site:jobs.ubs.com OR site:pwc.ch OR site:deloitte.ch)",
            "AI (legal OR compliance OR law OR tax) (Geneva OR Vaud OR Fribourg) (site:linkedin.com/jobs/view/ OR site:jobs.ch/en/vacancies/detail/ OR site:careers.pictet.com OR site:careers.lombardodier.com OR site:jobs.ubs.com OR site:pwc.ch OR site:deloitte.ch)"
        ]
        for query in google_queries:
            print(f"Google Search: Searching for '{query}'...")
            results = fetch_jobs_from_google_organic(query)
            
            for job in results:
                job_id = job.get("id")
                title = job.get("title", "").lower().strip()
                company = job.get("company", {}).get("display_name", "").lower().strip()
                dedup_key = (title, company)
                
                if job_id not in seen_job_ids and dedup_key not in seen_titles_companies:
                    seen_job_ids.add(job_id)
                    seen_titles_companies.add(dedup_key)
                    if is_target_job(job):
                        all_jobs.append(job)

    # Sort jobs by company name
    all_jobs.sort(key=lambda x: x.get("company", {}).get("display_name", "").lower())
    
    # Generate the report
    write_markdown_report(all_jobs)


if __name__ == "__main__":
    main()
