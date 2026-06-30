"""Requirement type enumeration for type-safe JD requirement classification."""

from enum import Enum, unique


@unique
class RequirementType(Enum):
    """Classification of a requirement extracted from a Job Description."""

    REQUIRED = "required"
    PREFERRED = "preferred"
    NEGATIVE = "negative"
    EXPERIENCE = "experience"
    LOCATION = "location"
    WORK_MODE = "work_mode"
    PRODUCT = "product"
    LEADERSHIP = "leadership"
    EVALUATION = "evaluation"
    TECHNOLOGY = "technology"
