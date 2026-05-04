# uv add transformers torch sentence-transformers wtpsplit
"""
NLP Service — REAL MODELS

Integration 1: Sentiment via HuggingFace "farahat0/hr-sentiment-model"
Integration 2: Skills extraction via SentenceTransformer + wtpsplit (from v1_optimized.py)
"""

import os
import re
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_HF_TOKEN = os.environ.get("HF_TOKEN", None)

# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 1 — Sentiment pipeline (loaded once at module level)
# ═══════════════════════════════════════════════════════════════════════════════

from transformers import pipeline as hf_pipeline

_sentiment_pipeline = hf_pipeline(
    "text-classification",
    model="farahat0/hr-sentiment-model",
    device=-1,
    token=_HF_TOKEN,
)


def _preprocess_hr(text: str) -> str:
    text = str(text).strip()
    text = re.sub(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", "[DATE]", text)
    text = re.sub(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", "[EMPLOYEE]", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 2 — Skills extraction models & data (loaded once at module level)
# ═══════════════════════════════════════════════════════════════════════════════

from sentence_transformers import SentenceTransformer, util
from wtpsplit import SaT

_embedding_model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1")
_sat = SaT("sat-12l")

# ── SKILL_ALIASES dictionary ──────────────────────────────────────────────────

SKILL_ALIASES = {
    # ── LEADERSHIP ──────────────────────────────────────────────
    "leadership": [
        "leadership",
        "leads the team",
        "mentors others",
        "guides colleagues",
        "takes charge",
        "inspires others",
        "sets direction",
        "drives the team",
        "takes ownership",
    ],
    "mentoring": [
        "mentoring",
        "coaches others",
        "develops team members",
        "supports junior staff",
        "guides new hires",
        "teaches colleagues",
    ],
    "delegation": [
        "delegation",
        "assigns tasks effectively",
        "distributes work",
        "trusts team with responsibilities",
        "empowers others",
    ],
    "decision making": [
        "decision making",
        "makes sound decisions",
        "decides confidently",
        "exercises good judgment",
        "thinks before acting",
        "evaluates options",
    ],
    "accountability": [
        "accountability",
        "takes responsibility",
        "owns mistakes",
        "follows through",
        "delivers on commitments",
        "reliable",
    ],
    "initiative": [
        "initiative",
        "proactive",
        "self-starter",
        "acts without being told",
        "takes the lead",
        "goes beyond expectations",
        "drives change",
    ],
    # ── COMMUNICATION ────────────────────────────────────────────
    "communication": [
        "communication",
        "articulates clearly",
        "expresses ideas well",
        "conveys information",
        "speaks confidently",
        "writes clearly",
    ],
    "availability": [
        "availability",
        "always available",
        "reachable when needed",
        "present when needed",
        "responsive to team",
    ],
    "active listening": [
        "active listening",
        "listens carefully",
        "pays attention",
        "understands others",
        "hears feedback well",
        "attentive in meetings",
    ],
    "presentation": [
        "presentation",
        "presents well",
        "delivers engaging talks",
        "public speaking",
        "explains to stakeholders",
        "clear in meetings",
    ],
    "written communication": [
        "written communication",
        "writes well",
        "clear emails",
        "good documentation",
        "professional writing",
        "concise reports",
    ],
    "giving feedback": [
        "giving feedback",
        "provides constructive criticism",
        "coaches through feedback",
        "shares observations openly",
    ],
    "receiving feedback": [
        "receiving feedback",
        "accepts criticism well",
        "open to feedback",
        "responds positively to critique",
        "non-defensive",
    ],
    # ── COLLABORATION ─────────────────────────────────────────────
    "teamwork": [
        "teamwork",
        "works well with others",
        "collaborative",
        "team player",
        "supports colleagues",
        "contributes to the team",
    ],
    "conflict resolution": [
        "conflict resolution",
        "resolves disagreements",
        "handles disputes",
        "mediates between parties",
        "de-escalates tension",
        "manages friction",
    ],
    "cross-functional collaboration": [
        "cross-functional collaboration",
        "works across teams",
        "partners with other departments",
        "coordinates with stakeholders",
    ],
    "empathy": [
        "empathy",
        "understands others feelings",
        "emotionally aware",
        "considers team morale",
        "compassionate",
        "supportive of peers",
    ],
    "relationship building": [
        "relationship building",
        "builds rapport",
        "earns trust",
        "maintains strong working relationships",
        "connects with colleagues",
    ],
    # ── DELIVERY & EXECUTION ──────────────────────────────────────
    "time management": [
        "time management",
        "meets deadlines",
        "delivers on time",
        "manages priorities",
        "punctual",
        "organized",
        "respects timelines",
    ],
    "productivity": [
        "productivity",
        "gets things done",
        "high output",
        "efficient worker",
        "delivers consistently",
        "results-oriented",
    ],
    "attention to detail": [
        "attention to detail",
        "thorough",
        "catches errors",
        "meticulous",
        "accurate work",
        "quality conscious",
        "precise",
    ],
    "goal achievement": [
        "goal achievement",
        "meets targets",
        "achieves objectives",
        "hits KPIs",
        "delivers results",
        "exceeds expectations",
    ],
    "project management": [
        "project management",
        "manages projects well",
        "coordinates deliverables",
        "tracks milestones",
        "keeps projects on track",
        "plans effectively",
    ],
    "prioritization": [
        "prioritization",
        "focuses on what matters",
        "manages workload",
        "handles multiple tasks",
        "knows what to tackle first",
    ],
    # ── THINKING & PROBLEM SOLVING ────────────────────────────────
    "problem solving": [
        "problem solving",
        "finds solutions",
        "resolves issues",
        "tackles challenges",
        "troubleshoots effectively",
        "overcomes obstacles",
    ],
    "critical thinking": [
        "critical thinking",
        "analytical",
        "thinks deeply",
        "questions assumptions",
        "evaluates situations carefully",
        "logical",
    ],
    "strategic thinking": [
        "strategic thinking",
        "sees the big picture",
        "thinks long term",
        "aligns work with strategy",
        "forward thinking",
        "visionary",
    ],
    "creativity": [
        "creativity",
        "innovative",
        "thinks outside the box",
        "brings new ideas",
        "creative solutions",
        "imaginative approach",
    ],
    "data-driven thinking": [
        "data-driven thinking",
        "uses data to decide",
        "evidence-based",
        "relies on metrics",
        "analytical approach",
        "backs decisions with data",
    ],
    # ── ADAPTABILITY & GROWTH ─────────────────────────────────────
    "adaptability": [
        "adaptability",
        "adapts to change",
        "flexible",
        "handles uncertainty",
        "adjusts quickly",
        "embraces new challenges",
    ],
    "learning agility": [
        "learning agility",
        "learns quickly",
        "picks up new skills fast",
        "eager to learn",
        "grows continuously",
        "develops new knowledge",
    ],
    "resilience": [
        "resilience",
        "bounces back",
        "handles pressure well",
        "stays calm under stress",
        "perseveres",
        "does not give up easily",
    ],
    "growth mindset": [
        "growth mindset",
        "seeks improvement",
        "open to learning",
        "embraces challenges",
        "treats failure as learning",
        "self-improving",
    ],
    # ── PROFESSIONALISM ───────────────────────────────────────────
    "work ethic": [
        "work ethic",
        "hardworking",
        "dedicated",
        "committed",
        "puts in effort",
        "goes the extra mile",
        "diligent",
        "working hard",
        "completes tasks",
        "gets the job done",
        "puts in the work",
        "great effort",
    ],
    "integrity": [
        "integrity",
        "honest",
        "trustworthy",
        "ethical",
        "acts with principles",
        "transparent",
        "does the right thing",
    ],
    "professionalism": [
        "professionalism",
        "conducts himself professionally",
        "conducts herself professionally",
        "represents the company well",
        "appropriate workplace behavior",
        "maintains standards",
    ],
    "punctuality": [
        "punctuality",
        "always on time",
        "never late",
        "respects others time",
        "arrives prepared",
        "timely",
    ],
    # ── TECHNICAL & DOMAIN ────────────────────────────────────────
    "technical skills": [
        "technical skills",
        "technically strong",
        "domain expertise",
        "deep knowledge",
        "subject matter expert",
        "skilled in tools",
    ],
    "digital literacy": [
        "digital literacy",
        "comfortable with technology",
        "uses software effectively",
        "tech savvy",
        "adapts to new tools",
    ],
    "knowledge sharing": [
        "knowledge sharing",
        "shares expertise",
        "documents learnings",
        "teaches the team",
        "spreads best practices",
        "contributes to wikis",
    ],
}

# ── Pre-compute alias embeddings (once at module level) ───────────────────────

_alias_texts = [alias for skill, aliases in SKILL_ALIASES.items() for alias in aliases]
_alias_to_skill = [
    skill for skill, aliases in SKILL_ALIASES.items() for alias in aliases
]
_alias_embeddings = _embedding_model.encode(_alias_texts, convert_to_tensor=True)

# ── Negation & Degradation patterns ───────────────────────────────────────────

NEGATION_PATTERNS = [
    # Core negations
    r"\blacks?\b",
    r"\bwithout\b",
    r"\bnever\b",
    r"\bpoor\b",
    r"\bweak\b",
    r"\bweakness\b",
    r"\bstruggles?\s+(with|to)\b",
    r"\bneeds?\s+to\s+improve\b",
    r"\bfails?\s+to\b",
    r"\bfailed\s+to\b",
    r"\bunable\s+to\b",
    r"\bdifficulty\s+(with)?\b",
    r"\bhas\s+difficulty\b",
    # Task/behavioral negations
    r"\bneglected\b",
    r"\bignored\b",
    r"\bmissed\b",
    r"\bskipped\b",
    r"\bavoided\b",
    r"\brefused\s+to\b",
    # Availability
    r"\bnot\s+available\b",
    r"\bunavailable\b",
    r"\balways\s+busy\b",
    r"\bnever\s+available\b",
    # Standard negations
    r"\bnot\s+able\s+to\b",
    r"\bwas\s+not\s+able\b",
    r"\bdidn'?t\b",
    r"\bdid\s+not\b",
    r"\bdoesn'?t\b",
    r"\bdoes\s+not\b",
    r"\bcan'?t\b",
    r"\bcannot\b",
    r"\bwon'?t\b",
    r"\bhard\s+to\b",
    r"\bdifficult\s+to\b",
    # Feedback/report negations
    r"\bnot\s+enough\b",
    r"\bcomplaints?\s+about\b",
    r"\bnegative\s+feedback\b",
    r"\braised\s+concerns?\b",
    r"\bhad\s+no\s+idea\b",
    r"\bno\s+idea\b",
    r"\bno\s+visibility\b",
    r"\bno\s+clue\b",
    r"\bwasn'?t\s+informed\b",
    r"\bnot\s+informed\b",
]

DEGRADATION_PATTERNS = [
    r"\btoo\s+slow\b",
    r"\btoo\s+long\b",
    r"\btook\s+too\s+long\b",
    r"\btakes?\s+too\s+long\b",
    r"\bvery\s+slow\b",
    r"\bspeed\s+(is|was|has)\s+(low|slow|poor|declining)\b",
    r"\bbecame?\s+low(er|ered)?\b",
    r"\bdeclin(ed|ing)\b",
    r"\bwors(e|ened)\b",
    r"\bbelow\s+(target|expectations?|average|standard)\b",
    r"\bmissed\s+(the\s+)?deadline\b",
    r"\boverdue\b",
    r"\bdelayed\b",
    r"\bnot\s+(fast|quick|efficient)\s+enough\b",
    r"\bslow\s+(pace|progress|performance|delivery)\b",
    r"\binsufficient\b",
    r"\binadequate\b",
    r"\broom\s+for\s+improvement\b",
    r"\bneeds?\s+improvement\b",
    r"\bunderperform(ing|ed|s)?\b",
    r"\bnot\s+meeting\s+(targets?|goals?|expectations?)\b",
    r"\bfell\s+short\b",
]

_NEG_RE = [re.compile(p, re.IGNORECASE) for p in NEGATION_PATTERNS]
_DEG_RE = [re.compile(p, re.IGNORECASE) for p in DEGRADATION_PATTERNS]

# ── Contrast markers for clause splitting ─────────────────────────────────────

_CONTRAST_MARKERS = r"\b(but|however|although|though|yet|despite|nevertheless|that said|the problem is|on the other hand|unfortunately)\b"

# ── Skill extraction constants ────────────────────────────────────────────────

_SIMILARITY_THRESHOLD = 0.58
_PREFIX = "Represent this sentence for searching relevant passages: "


# ═══════════════════════════════════════════════════════════════════════════════
# Private helper functions (ported from v1_optimized.py)
# ═══════════════════════════════════════════════════════════════════════════════


def _sentence_is_negative(sentence: str) -> bool:
    """
    Returns True if the sentence contains any direct negation
    or degradation signal — meaning it describes a WEAKNESS/GAP.
    """
    s = sentence.lower()
    for pattern in _NEG_RE:
        if pattern.search(s):
            return True
    for pattern in _DEG_RE:
        if pattern.search(s):
            return True
    return False


def _split_with_polarity(text: str) -> list:
    """
    Split text into clauses, each tagged with polarity:
      - 'positive' : clause appears before any contrast marker
      - 'contrast' : clause appears after a contrast marker (treated as negative context)
      - 'negative' : clause contains a direct negation or degradation signal
    Returns: list of dicts {text: str, polarity: str}
    """
    units = []

    # Split by contrast markers
    parts = re.split(_CONTRAST_MARKERS, text, flags=re.IGNORECASE)

    after_contrast = False
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Check if this part is a marker token
        if re.fullmatch(_CONTRAST_MARKERS, part, flags=re.IGNORECASE):
            after_contrast = True
            continue
        if len(part) < 5:
            continue

        # Determine polarity
        if _sentence_is_negative(part):
            polarity = "negative"
        elif after_contrast:
            polarity = "contrast"
        else:
            polarity = "positive"

        units.append({"text": part, "polarity": polarity})

    # Also add the full sentence as an additional unit
    full_polarity = "negative" if _sentence_is_negative(text) else "positive"
    units.append({"text": text.strip(), "polarity": full_polarity})

    # Comma splits (but only if they're long enough to be meaningful)
    for part in text.split(","):
        part = part.strip()
        if len(part) > 15:
            pol = "negative" if _sentence_is_negative(part) else "positive"
            units.append({"text": part, "polarity": pol})

    # Deduplicate by text
    seen = set()
    result = []
    for u in units:
        if u["text"].lower() not in seen:
            seen.add(u["text"].lower())
            result.append(u)

    return result


def _split_into_clauses(text: str) -> list:
    """
    Top-level splitter. Returns list of {text, polarity} dicts.
    """
    if not text:
        return []
    text = text[0].upper() + text[1:]

    # First: sentence-level split via SaT
    segments = _sat.split(text, threshold=0.0005)
    sentences = []
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        if sentences and (seg[0].islower() or len(seg.split()) < 2):
            sentences[-1] = sentences[-1] + " " + seg
        else:
            sentences.append(seg)

    # Then: expand each sentence into polarity-tagged clauses
    all_units = []
    for sentence in sentences:
        if len(sentence) > 8:
            all_units.extend(_split_with_polarity(sentence))

    # Deduplicate
    seen = set()
    result = []
    for u in all_units:
        if u["text"].lower() not in seen:
            seen.add(u["text"].lower())
            result.append(u)

    return result


def _score_clauses(clauses: list) -> dict:
    """
    Internal: embed each clause and get top skill matches.
    Returns dict: skill -> {score, polarity}
    """
    skill_hits = {}

    for clause in clauses:
        text = clause["text"]
        polarity = clause["polarity"]

        prefixed = f"{_PREFIX}{text}"
        emb = _embedding_model.encode(prefixed, convert_to_tensor=True)
        scores = util.cos_sim(emb, _alias_embeddings)[0]

        for i, score in enumerate(scores):
            score_val = float(score)
            if score_val < _SIMILARITY_THRESHOLD:
                continue

            skill = _alias_to_skill[i]

            # Update if this is the best score for this skill under this polarity
            if skill not in skill_hits or score_val > skill_hits[skill]["score"]:
                skill_hits[skill] = {"score": round(score_val, 2), "polarity": polarity}
            elif skill in skill_hits:
                # If same score but different polarity — prefer the negative signal
                if (
                    polarity in ("negative", "contrast")
                    and skill_hits[skill]["polarity"] == "positive"
                ):
                    skill_hits[skill]["polarity"] = polarity

    return skill_hits


def _extract_skill_gaps(review_text: str) -> list:
    """
    Returns skills that are clearly MISSING or WEAK (negative/contrast polarity).
    """
    clauses = _split_into_clauses(review_text)
    skill_hits = _score_clauses(clauses)

    gaps = {
        skill: info["score"]
        for skill, info in skill_hits.items()
        if info["polarity"] in ("negative", "contrast")
    }

    return sorted(
        [{"skill": s, "confidence": sc} for s, sc in gaps.items()],
        key=lambda x: x["confidence"],
        reverse=True,
    )


def _extract_skills(review_text: str) -> list:
    """
    Returns skills that are clearly PRESENT (positive polarity only).
    Excludes any skill that also appears as a gap.
    """
    clauses = _split_into_clauses(review_text)
    skill_hits = _score_clauses(clauses)

    found = {
        skill: info["score"]
        for skill, info in skill_hits.items()
        if info["polarity"] == "positive"
    }

    # Remove any skill that also appears as a gap
    gaps = {g["skill"] for g in _extract_skill_gaps(review_text)}
    found = {k: v for k, v in found.items() if k not in gaps}

    return sorted(
        [{"skill": s, "confidence": sc} for s, sc in found.items()],
        key=lambda x: x["confidence"],
        reverse=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Recommendation generator via Gemini
# ═══════════════════════════════════════════════════════════════════════════════

from google import genai


def generate_recommendations(skills_found: list[str], skill_gaps: list[str], review_text: str) -> str:
    """Generate recommendations using Gemini 3 Flash Preview."""
    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

        skills_found_str = ", ".join(skills_found) if skills_found else "None"
        skills_gap_str = ", ".join(skill_gaps) if skill_gaps else "None"

        input_text = f"""
You are an expert HR Development Coach. Your task is to provide direct, actionable, and specific development recommendations for an employee based on their current profile.

Do not include any introductory pleasantries, explanations of your logic, or concluding remarks. Output strictly a bulleted list of direct recommendations with key words and be less wordy. 

if there are no skill gaps, provide a simple recommendations paragraph for further growth and development.
. for skills found and skill gaps refer to the: {review_text} .to give specific recommendations context in bullet points.
DATA INPUTS:
- Current Skills: {skills_found_str}
- Identified Skill Gaps: {skills_gap_str}

RECOMMENDATIONS:"
"""
        response = client.models.generate_content(
            model="gemini-3-flash-preview", contents=input_text
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Generate recommendations failed: {e}")
        return "Failed to generate recommendations."


# ═══════════════════════════════════════════════════════════════════════════════
# Main entry point (signature unchanged)
# ═══════════════════════════════════════════════════════════════════════════════


def full_analysis(text: str, behavioral_rating: int, performance_rating: int) -> dict:
    """
    Run all NLP tasks on the given review text.
    Returns a dict with sentiment, skills_found, skill_gaps, behavioral_rating,
    performance_rating, and recommendations.
    """
    # ── Integration 1: Real sentiment model ──
    try:
        _processed = _preprocess_hr(text)
        _result = _sentiment_pipeline(_processed)[0]
        sentiment = {
            "label": _result["label"],
            "confidence": round(_result["score"], 4),
        }
    except Exception as e:
        logger.error(f"Sentiment model failed: {e}")
        sentiment = {"label": "neutral", "confidence": 0.0}

    # ── Integration 2: Real skills extraction ──
    try:
        _raw_skills = _extract_skills(text)
        _raw_gaps = _extract_skill_gaps(text)
        skills_found = [s["skill"] for s in _raw_skills]
        skill_gaps = [g["skill"] for g in _raw_gaps]
    except Exception as e:
        logger.error(f"Skills extraction failed: {e}")
        skills_found = []
        skill_gaps = []

    # ── Updated Recommendation ──
    recommendations = generate_recommendations(skills_found, skill_gaps,text)
    
    return {
        "sentiment": sentiment,
        "skills_found": skills_found,
        "skill_gaps": skill_gaps,
        "behavioral_rating": behavioral_rating,
        "performance_rating": performance_rating,
        "recommendations": recommendations,
    }
