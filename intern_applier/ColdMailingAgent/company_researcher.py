"""
company_researcher.py — Deep Intelligence & Hook Generator for Companies.

Extracts structured insights about the company (domain, core product, data/engineering
initiatives) and crafts a genuine connection hook for human-like cold outreach.
"""

import json
import os
import time
from pathlib import Path
from google import genai
import config

_CACHE = {}


def _load_cache():
    global _CACHE
    cache_path = Path(config.RESEARCH_CACHE_FILE)
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                _CACHE = json.load(f)
        except Exception:
            _CACHE = {}


def _save_cache():
    try:
        os.makedirs(os.path.dirname(config.RESEARCH_CACHE_FILE), exist_ok=True)
        with open(config.RESEARCH_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_CACHE, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Failed to save company research cache: {e}")


def research_company(company_name: str, designation: str = "") -> dict:
    """
    Research a target company using Gemini with persistent caching.

    Returns:
        {
            "company": str,
            "domain": str,              # e.g. "Fintech & Payments", "Quick Commerce & Logistics"
            "core_product": str,        # 1-sentence summary of what they build
            "engineering_focus": str,   # specific data/ML/engineering focus areas
            "relevant_projects": list,  # which of candidate's projects fit best
            "personal_hook": str,       # 1-2 sentence human-sounding reason for outreach
        }
    """
    _load_cache()
    norm_name = company_name.strip().lower()
    
    if norm_name in _CACHE:
        return _CACHE[norm_name]

    if not config.GEMINI_API_KEY:
        # Fallback if no API key
        fallback = {
            "company": company_name,
            "domain": "Technology & Software",
            "core_product": f"High-scale products and digital platforms at {company_name}",
            "engineering_focus": "Full-stack web engineering, scalable backend APIs, and responsive architectures",
            "relevant_projects": ["CareConnect (Healthcare Platform & MERN Stack)", "CineVerse (Movie Discovery & API Integration)"],
            "personal_hook": f"I've been closely following what {company_name} is building in this space and love the technical challenge.",
        }
        return fallback

    client = genai.Client(api_key=config.GEMINI_API_KEY)

    prompt = f"""
You are a career intelligence researcher assisting {config.YOUR_YEAR_AND_DEGREE} ({config.YOUR_NAME}) in finding meaningful technical connections for a cold outreach email seeking a {config.YOUR_TARGET_ROLE} role.

Candidate Background:
- 2nd-year B.Tech (ECE) undergraduate at IIT Kharagpur (CGPA 8.24)
- Real Project 1: CareConnect (Full-stack MERN healthcare appointment platform with RBAC, 25+ RESTful APIs, JWT auth, Razorpay payments)
- Real Project 2: CineVerse (Full-stack MERN movie discovery platform, 5+ TMDB endpoints, Appwrite debounced search analytics, infinite scroll)
- Real Project 3: NoteVault (Secure notes management with JWT, bcrypt, Express Router, MongoDB/Mongoose schemas)
- Real Project 4: PathPilot (Interactive pathfinding visualizer with BFS, DFS, Dijkstra, recursive division maze generation)
- Strong skills: JavaScript, TypeScript, React.js, Node.js, Express.js, MongoDB, C++, Data Structures & Algorithms, Competitive Programming (Codeforces Pupil, 300+ LeetCode)

Target Company: {company_name}
Target Recruiter/POC Designation: {designation}

Task:
Analyze this company and return ONLY a valid JSON object with:
1. "domain": Primary industry/technical domain (e.g. "Fintech & Payments", "Quick Commerce & Supply Chain", "CleanTech / EV", "HealthTech", "AI & DevTools", "E-commerce", "SaaS & Enterprise")
2. "core_product": Brief 1-sentence factual description of what {company_name} builds/does.
3. "engineering_focus": 1-sentence describing their core software, web, or backend engineering challenges (e.g., "high-concurrency payment processing and user auth", "scalable web applications and responsive customer portals", "API integrations and real-time data synchronization").
4. "best_matched_project": Either "CareConnect (Healthcare Platform & MERN Stack)" or "CineVerse (Movie Discovery & API Integration)" or "PathPilot (Pathfinding Visualizer & Algorithms)" or "NoteVault (Secure Authentication & APIs)" based on what is most relevant to {company_name}.
5. "personal_hook": A natural, conversational, 1-sentence reason why a student working on full-stack engineering and software development is excited about {company_name}'s specific product/challenge (NO robotic buzzwords like 'synergy', 'testament', 'cutting-edge').

Return ONLY the JSON object.
"""

    raw = ""
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt
            )
            raw = response.text.strip()
            break
        except Exception as e:
            print(f"Warning: API attempt {attempt + 1}/3 failed for {company_name}: {e}")
            time.sleep(5.0 * (attempt + 1))

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        data = json.loads(raw.strip())
    except Exception:
        data = {
            "domain": "Technology & Software",
            "core_product": f"Core platforms and products at {company_name}",
            "engineering_focus": "Full-stack engineering, scalable APIs, and responsive architectures",
            "best_matched_project": "CareConnect (Healthcare Platform & MERN Stack)",
            "personal_hook": f"I really admire how {company_name} is solving complex technical challenges in this space.",
        }

    result = {
        "company": company_name,
        "domain": data.get("domain", "Technology"),
        "core_product": data.get("core_product", ""),
        "engineering_focus": data.get("engineering_focus", ""),
        "best_matched_project": data.get("best_matched_project", "CareConnect (Healthcare Platform & MERN Stack)"),
        "personal_hook": data.get("personal_hook", ""),
    }

    _CACHE[norm_name] = result
    _save_cache()
    return result
