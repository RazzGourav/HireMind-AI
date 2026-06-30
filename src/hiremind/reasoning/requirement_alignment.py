"""Requirement Alignment Engine — classifies JD requirements against candidate skills."""

from __future__ import annotations

from hiremind.domain.explanation import AlignmentStatus, RequirementAlignment
from hiremind.domain.requirement import ParsedRequirements
from hiremind.reasoning.evidence_collector import CollectedEvidence


class RequirementAlignmentEngine:
    """Classifies each JD requirement as MATCHED, PARTIAL, or MISSING."""

    def align(
        self,
        requirements: ParsedRequirements,
        evidence: CollectedEvidence,
    ) -> list[RequirementAlignment]:
        """Align all JD requirements against collected candidate evidence.

        Uses exact match, normalized-skill match, and substring matching.
        """
        # Build lookup sets for matching
        raw_lower = {s.lower() for s in evidence.skill_names}
        norm_lower = {s.lower() for s in evidence.normalized_skills}
        all_skills = raw_lower | norm_lower

        alignments: list[RequirementAlignment] = []

        for req in requirements.required:
            status, matched, ev = self._match_requirement(req.name, req.aliases, all_skills)
            alignments.append(
                RequirementAlignment(
                    requirement_id=req.id,
                    requirement_name=req.name,
                    required=True,
                    status=status,
                    matched_skill=matched,
                    evidence=ev,
                )
            )

        for req in requirements.preferred:
            status, matched, ev = self._match_requirement(req.name, req.aliases, all_skills)
            alignments.append(
                RequirementAlignment(
                    requirement_id=req.id,
                    requirement_name=req.name,
                    required=False,
                    status=status,
                    matched_skill=matched,
                    evidence=ev,
                )
            )

        return alignments

    def compute_alignment_ratio(self, alignments: list[RequirementAlignment]) -> float:
        """Compute ratio of matched + partial requirements vs total."""
        if not alignments:
            return 0.0
        matched = sum(
            (
                1.0
                if a.status == AlignmentStatus.MATCHED
                else 0.5 if a.status == AlignmentStatus.PARTIAL else 0.0
            )
            for a in alignments
        )
        return matched / len(alignments)

    def compute_required_alignment_ratio(self, alignments: list[RequirementAlignment]) -> float:
        """Compute alignment ratio for required-only requirements."""
        required = [a for a in alignments if a.required]
        if not required:
            return 1.0
        matched = sum(
            (
                1.0
                if a.status == AlignmentStatus.MATCHED
                else 0.5 if a.status == AlignmentStatus.PARTIAL else 0.0
            )
            for a in required
        )
        return matched / len(required)

    @staticmethod
    def _match_requirement(
        name: str,
        aliases: tuple[str, ...],
        candidate_skills: set[str],
    ) -> tuple[AlignmentStatus, str | None, str]:
        """Try to match a single requirement against the candidate's skill set."""
        name_lower = name.lower()

        # 1. Exact match
        if name_lower in candidate_skills:
            return (
                AlignmentStatus.MATCHED,
                name,
                f"Candidate has '{name}' matching this requirement.",
            )

        # 2. Alias match
        for alias in aliases:
            if alias.lower() in candidate_skills:
                return (
                    AlignmentStatus.MATCHED,
                    alias,
                    f"Candidate has '{alias}' which is an alias for '{name}'.",
                )

        # 3. Substring / partial match
        for skill in candidate_skills:
            if name_lower in skill or skill in name_lower:
                return (
                    AlignmentStatus.PARTIAL,
                    skill,
                    f"Candidate has '{skill}' which partially matches '{name}'.",
                )

        # 4. No match
        return (
            AlignmentStatus.MISSING,
            None,
            f"Candidate does not have '{name}' or any related skill.",
        )
