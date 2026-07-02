"""Predefined 12-category skill taxonomy.

This module is the SINGLE SOURCE OF TRUTH for skill categories across the whole
system: admin role forms, LLM extraction prompts, the course catalog, and the
dashboard category breakdown. See DDD Section 2.
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, List


class SkillCategory(str, Enum):
    PROGRAMMING_LANGUAGES = "programming_languages"
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASES = "databases"
    DEVOPS = "devops"
    CLOUD = "cloud"
    ARCHITECTURE = "architecture"
    DATA_ENGINEERING = "data_engineering"
    DATA_SCIENCE = "data_science"
    QUALITY = "quality"
    SECURITY = "security"
    SOFT_SKILLS = "soft_skills"


CATEGORY_LABELS: Dict[SkillCategory, str] = {
    SkillCategory.PROGRAMMING_LANGUAGES: "Programming Languages",
    SkillCategory.FRONTEND: "Frontend Development",
    SkillCategory.BACKEND: "Backend Development",
    SkillCategory.DATABASES: "Databases",
    SkillCategory.DEVOPS: "DevOps & Infrastructure",
    SkillCategory.CLOUD: "Cloud Platforms",
    SkillCategory.ARCHITECTURE: "System Architecture",
    SkillCategory.DATA_ENGINEERING: "Data Engineering",
    SkillCategory.DATA_SCIENCE: "Data Science & ML",
    SkillCategory.QUALITY: "Quality & Testing",
    SkillCategory.SECURITY: "Security",
    SkillCategory.SOFT_SKILLS: "Soft Skills & Leadership",
}

# Short codes used in course_id: COURSE-{CATEGORY_CODE}-{LEVEL_CODE}-{SEQ}
CATEGORY_CODES: Dict[SkillCategory, str] = {
    SkillCategory.PROGRAMMING_LANGUAGES: "PL",
    SkillCategory.FRONTEND: "FE",
    SkillCategory.BACKEND: "BE",
    SkillCategory.DATABASES: "DB",
    SkillCategory.DEVOPS: "DO",
    SkillCategory.CLOUD: "CL",
    SkillCategory.ARCHITECTURE: "ARCH",
    SkillCategory.DATA_ENGINEERING: "DE",
    SkillCategory.DATA_SCIENCE: "DS",
    SkillCategory.QUALITY: "QA",
    SkillCategory.SECURITY: "SEC",
    SkillCategory.SOFT_SKILLS: "SOFT",
}

VALID_CATEGORIES: List[str] = [c.value for c in SkillCategory]


def category_choices() -> List[Dict[str, str]]:
    """Return category choices as [{key, label}, ...] for API / dropdowns."""
    return [{"key": c.value, "label": CATEGORY_LABELS[c]} for c in SkillCategory]


def is_valid_category(value: str) -> bool:
    return value in VALID_CATEGORIES
