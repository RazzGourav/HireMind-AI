"""Title & skill normalisation via static lookup + substring matching."""

# ──────────────────────────────────────────────────────────────────────────────
# Canonical title lookup table.
# Maps common title variations → a standardised canonical form.
# ──────────────────────────────────────────────────────────────────────────────
_TITLE_MAP: dict[str, str] = {
    # AI / ML
    "machine learning engineer": "AI_ENGINEER",
    "ml engineer": "AI_ENGINEER",
    "ai engineer": "AI_ENGINEER",
    "applied ai engineer": "AI_ENGINEER",
    "deep learning engineer": "AI_ENGINEER",
    "nlp engineer": "AI_ENGINEER",
    "computer vision engineer": "AI_ENGINEER",
    "ai/ml engineer": "AI_ENGINEER",
    # Data Science
    "data scientist": "DATA_SCIENTIST",
    "senior data scientist": "DATA_SCIENTIST",
    "lead data scientist": "DATA_SCIENTIST",
    "applied scientist": "DATA_SCIENTIST",
    "research scientist": "DATA_SCIENTIST",
    "ml scientist": "DATA_SCIENTIST",
    # Data Engineering
    "data engineer": "DATA_ENGINEER",
    "senior data engineer": "DATA_ENGINEER",
    "analytics engineer": "DATA_ENGINEER",
    "etl developer": "DATA_ENGINEER",
    "big data engineer": "DATA_ENGINEER",
    # Software / Backend
    "software engineer": "SOFTWARE_ENGINEER",
    "senior software engineer": "SOFTWARE_ENGINEER",
    "staff software engineer": "SOFTWARE_ENGINEER",
    "principal software engineer": "SOFTWARE_ENGINEER",
    "software developer": "SOFTWARE_ENGINEER",
    "sde": "SOFTWARE_ENGINEER",
    "sde-1": "SOFTWARE_ENGINEER",
    "sde-2": "SOFTWARE_ENGINEER",
    "sde-3": "SOFTWARE_ENGINEER",
    "backend engineer": "BACKEND_ENGINEER",
    "backend developer": "BACKEND_ENGINEER",
    "server engineer": "BACKEND_ENGINEER",
    # Frontend
    "frontend engineer": "FRONTEND_ENGINEER",
    "frontend developer": "FRONTEND_ENGINEER",
    "ui engineer": "FRONTEND_ENGINEER",
    "react developer": "FRONTEND_ENGINEER",
    # Fullstack
    "full stack engineer": "FULLSTACK_ENGINEER",
    "fullstack engineer": "FULLSTACK_ENGINEER",
    "full stack developer": "FULLSTACK_ENGINEER",
    "fullstack developer": "FULLSTACK_ENGINEER",
    # DevOps / Infra
    "devops engineer": "DEVOPS_ENGINEER",
    "site reliability engineer": "DEVOPS_ENGINEER",
    "sre": "DEVOPS_ENGINEER",
    "platform engineer": "DEVOPS_ENGINEER",
    "infrastructure engineer": "DEVOPS_ENGINEER",
    "cloud engineer": "DEVOPS_ENGINEER",
    # Management
    "engineering manager": "ENGINEERING_MANAGER",
    "technical lead": "TECH_LEAD",
    "tech lead": "TECH_LEAD",
    "team lead": "TECH_LEAD",
    "architect": "ARCHITECT",
    "solutions architect": "ARCHITECT",
    "principal architect": "ARCHITECT",
    "product manager": "PRODUCT_MANAGER",
    "program manager": "PROGRAM_MANAGER",
    "project manager": "PROJECT_MANAGER",
    # QA
    "qa engineer": "QA_ENGINEER",
    "test engineer": "QA_ENGINEER",
    "sdet": "QA_ENGINEER",
    "quality engineer": "QA_ENGINEER",
}

# Substring patterns for fallback matching (checked in order).
_SUBSTRING_RULES: list[tuple[str, str]] = [
    ("machine learning", "AI_ENGINEER"),
    ("deep learning", "AI_ENGINEER"),
    ("artificial intelligence", "AI_ENGINEER"),
    ("nlp", "AI_ENGINEER"),
    ("computer vision", "AI_ENGINEER"),
    ("data scien", "DATA_SCIENTIST"),
    ("data engineer", "DATA_ENGINEER"),
    ("data analyst", "DATA_ANALYST"),
    ("backend", "BACKEND_ENGINEER"),
    ("front end", "FRONTEND_ENGINEER"),
    ("frontend", "FRONTEND_ENGINEER"),
    ("full stack", "FULLSTACK_ENGINEER"),
    ("fullstack", "FULLSTACK_ENGINEER"),
    ("devops", "DEVOPS_ENGINEER"),
    ("sre", "DEVOPS_ENGINEER"),
    ("platform", "DEVOPS_ENGINEER"),
    ("software", "SOFTWARE_ENGINEER"),
    ("developer", "SOFTWARE_ENGINEER"),
    ("engineer", "SOFTWARE_ENGINEER"),
    ("architect", "ARCHITECT"),
    ("manager", "MANAGER"),
    ("lead", "TECH_LEAD"),
    ("director", "DIRECTOR"),
    ("vp", "VP"),
    ("analyst", "ANALYST"),
    ("consultant", "CONSULTANT"),
    ("intern", "INTERN"),
]


def normalize_title(title: str | None) -> str:
    """Normalise a job title to a canonical form.

    Uses exact lookup first, then substring matching.
    Returns 'UNKNOWN' if no match is found.
    """
    if not title:
        return "UNKNOWN"

    lowered = title.strip().lower()

    # Exact match.
    canonical = _TITLE_MAP.get(lowered)
    if canonical:
        return canonical

    # Substring fallback.
    for substring, canonical_name in _SUBSTRING_RULES:
        if substring in lowered:
            return canonical_name

    return "UNKNOWN"
