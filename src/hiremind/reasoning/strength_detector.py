"""Strength Detector — rule-based engine that identifies candidate strengths."""

from __future__ import annotations

from hiremind.domain.explanation import Strength
from hiremind.reasoning.evidence_collector import CollectedEvidence


class StrengthDetector:
    """Detects positive signals in a candidate's profile."""

    def detect(self, evidence: CollectedEvidence) -> list[Strength]:
        """Scan collected evidence for notable strengths."""
        strengths: list[Strength] = []

        # 1. Production AI experience
        if evidence.production_score > 0.6:
            strengths.append(
                Strength(
                    label="Production AI Experience",
                    description="Demonstrated experience deploying AI/ML systems in production environments.",
                    evidence=f"Production score: {evidence.production_score:.0%}",
                )
            )

        # 2. Strong programming skills
        if evidence.programming_skill_count >= 3:
            strengths.append(
                Strength(
                    label="Strong Programming Foundation",
                    description="Proficient across multiple programming languages and frameworks.",
                    evidence=f"{evidence.programming_skill_count} programming skills identified.",
                )
            )

        # 3. Retrieval / search systems expertise
        if evidence.retrieval_depth >= 2:
            strengths.append(
                Strength(
                    label="Retrieval Systems Expertise",
                    description="Deep knowledge of information retrieval, vector search, or RAG architectures.",
                    evidence=f"Retrieval depth score: {evidence.retrieval_depth:.1f}",
                )
            )

        # 4. Leadership indicators
        if evidence.leadership_score > 0.5:
            strengths.append(
                Strength(
                    label="Leadership Capability",
                    description="Shows evidence of team leadership, mentorship, or managerial responsibilities.",
                    evidence=f"Leadership score: {evidence.leadership_score:.0%}",
                )
            )

        # 5. Career stability
        if evidence.career_stability > 0.7 and evidence.average_tenure_months > 24:
            strengths.append(
                Strength(
                    label="Stable Career Trajectory",
                    description="Consistent career progression with strong tenure at employers.",
                    evidence=(
                        f"Career stability: {evidence.career_stability:.0%}, "
                        f"average tenure: {evidence.average_tenure_months:.0f} months."
                    ),
                )
            )

        # 6. High recruiter engagement
        if evidence.recruiter_response_score > 0.7:
            strengths.append(
                Strength(
                    label="High Recruiter Engagement",
                    description="Active engagement with recruiters indicating strong hiring intent.",
                    evidence=f"Recruiter response score: {evidence.recruiter_response_score:.0%}",
                )
            )

        # 7. Deep domain expertise
        if evidence.domain_breadth >= 2:
            strengths.append(
                Strength(
                    label="Cross-Domain Expertise",
                    description="Experience spanning multiple industry verticals.",
                    evidence=f"Domain breadth: {evidence.domain_breadth:.1f} domains.",
                )
            )

        # 8. Strong GitHub presence
        if evidence.github_activity_score > 0.6:
            strengths.append(
                Strength(
                    label="Active Open Source Contributor",
                    description="Strong GitHub activity demonstrating continuous technical engagement.",
                    evidence=f"GitHub activity score: {evidence.github_activity_score:.0%}",
                )
            )

        # 9. Growth trajectory
        if evidence.growth_score > 0.6:
            strengths.append(
                Strength(
                    label="Strong Growth Trajectory",
                    description="Demonstrates consistent upward career and skill growth.",
                    evidence=f"Growth score: {evidence.growth_score:.0%}",
                )
            )

        # 10. Deep experience
        if evidence.total_experience_months >= 96:
            strengths.append(
                Strength(
                    label="Extensive Industry Experience",
                    description=f"{evidence.total_experience_months // 12}+ years of professional experience.",
                    evidence=f"Total experience: {evidence.total_experience_months} months.",
                )
            )

        return strengths
