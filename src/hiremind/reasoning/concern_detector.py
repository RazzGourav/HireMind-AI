"""Concern Detector — rule-based engine that identifies candidate red flags."""

from __future__ import annotations

from hiremind.domain.explanation import (
    AlignmentStatus,
    Concern,
    ConcernSeverity,
    RequirementAlignment,
)
from hiremind.reasoning.evidence_collector import CollectedEvidence


class ConcernDetector:
    """Detects risk signals and concerns in a candidate's profile."""

    def detect(
        self,
        evidence: CollectedEvidence,
        alignments: list[RequirementAlignment],
        max_notice_days: int = 90,
    ) -> list[Concern]:
        """Scan evidence and requirement alignments for concerns."""
        concerns: list[Concern] = []

        # 1. Missing mandatory skills
        required_alignments = [a for a in alignments if a.required]
        missing_required = [a for a in required_alignments if a.status == AlignmentStatus.MISSING]
        if missing_required:
            missing_ratio = (
                len(missing_required) / len(required_alignments) if required_alignments else 0
            )
            severity = (
                ConcernSeverity.HIGH
                if missing_ratio > 0.5
                else ConcernSeverity.MEDIUM if missing_ratio > 0.25 else ConcernSeverity.LOW
            )
            missing_names = ", ".join(a.requirement_name for a in missing_required[:5])
            concerns.append(
                Concern(
                    label="Missing Mandatory Skills",
                    severity=severity,
                    description=f"{len(missing_required)} of {len(required_alignments)} required skills are missing.",
                    evidence=f"Missing: {missing_names}{'...' if len(missing_required) > 5 else ''}",
                )
            )

        # 2. Long notice period
        if (
            evidence.notice_period_days is not None
            and evidence.notice_period_days > max_notice_days
        ):
            excess = evidence.notice_period_days - max_notice_days
            severity = ConcernSeverity.HIGH if excess > 30 else ConcernSeverity.MEDIUM
            concerns.append(
                Concern(
                    label="Extended Notice Period",
                    severity=severity,
                    description=f"Notice period ({evidence.notice_period_days} days) exceeds the {max_notice_days}-day limit.",
                    evidence=f"Excess: {excess} days over threshold.",
                )
            )

        # 3. Low GitHub activity
        if evidence.github_activity_score < 0.2 and not evidence.has_github:
            concerns.append(
                Concern(
                    label="No GitHub Presence",
                    severity=ConcernSeverity.LOW,
                    description="No GitHub profile or activity detected.",
                    evidence="GitHub activity score: 0%",
                )
            )
        elif evidence.github_activity_score < 0.2 and evidence.has_github:
            concerns.append(
                Concern(
                    label="Low GitHub Activity",
                    severity=ConcernSeverity.LOW,
                    description="GitHub profile exists but shows minimal activity.",
                    evidence=f"GitHub activity score: {evidence.github_activity_score:.0%}",
                )
            )

        # 4. Career inconsistency
        if evidence.consistency_score < 0.4:
            concerns.append(
                Concern(
                    label="Profile Inconsistency",
                    severity=ConcernSeverity.MEDIUM,
                    description="Profile data shows inconsistencies between stated skills and career history.",
                    evidence=f"Consistency score: {evidence.consistency_score:.0%}",
                )
            )

        # 5. Job hopping
        if evidence.average_tenure_months > 0 and evidence.average_tenure_months < 12:
            concerns.append(
                Concern(
                    label="Frequent Job Changes",
                    severity=ConcernSeverity.MEDIUM,
                    description="Average tenure below 12 months suggests potential retention risk.",
                    evidence=(
                        f"Average tenure: {evidence.average_tenure_months:.0f} months "
                        f"across {evidence.company_count} companies."
                    ),
                )
            )

        # 6. Keyword stuffing
        if len(evidence.skill_names) > 30:
            concerns.append(
                Concern(
                    label="Potential Keyword Stuffing",
                    severity=ConcernSeverity.LOW,
                    description=f"Profile lists {len(evidence.skill_names)} skills, which may indicate padding.",
                    evidence=f"Skill count: {len(evidence.skill_names)}",
                )
            )

        return concerns
