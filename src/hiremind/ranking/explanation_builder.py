"""Explanation Builder — constructs human-readable score explanations for each candidate."""



class ExplanationBuilder:
    """Generates natural language and structured explanations for candidate scores."""

    def build_explanation(self, candidate_id: str, components: dict[str, float]) -> str:
        """Generate human-readable text explanation based on the fused subscores."""
        tech = components.get("technical_score", 0.0)
        career = components.get("career_score", 0.0)
        behavior = components.get("behavior_score", 0.0)
        knowledge = components.get("knowledge_score", 0.0)
        penalty = components.get("risk_penalty", 0.0)
        final = components.get("final_score", 0.0)

        # Build list of key strengths
        strengths = []
        if tech >= 0.7:
            strengths.append("Strong technical skill alignment and production experience.")
        if career >= 0.7:
            strengths.append("High career stability, long tenure, and steady progression.")
        if behavior >= 0.7:
            strengths.append("Excellent behavioral activity signals and profile completeness.")
        if knowledge >= 0.7:
            strengths.append(
                "Exceptional technology depth and domain expertise within the knowledge graph."
            )

        if not strengths:
            strengths.append(
                "Balanced profile across technical, career, and behavioral dimensions."
            )

        # Build list of concerns
        concerns = []
        if penalty > 0.0:
            if penalty >= 0.2:
                concerns.append(
                    f"Significant risk penalty (-{penalty*100:.0f}%) applied due to profile inconsistencies or notice period limits."
                )
            else:
                concerns.append(f"Minor risk penalty (-{penalty*100:.0f}%) applied.")

        # Suitability summary
        if final >= 80.0:
            suitability = (
                "highly recommended candidate with exceptional skills and stable career history."
            )
        elif final >= 60.0:
            suitability = "solid candidate matching key requirements with good growth potential."
        else:
            suitability = "candidate with partial requirement coverage or profile risks."

        explanation = (
            f"Candidate {candidate_id} is a {suitability}\n"
            f"Key Strengths: {' '.join(strengths)}\n"
            f"Subscores: Technical: {tech*100:.1f}%, Career: {career*100:.1f}%, Behavior: {behavior*100:.1f}%, Knowledge: {knowledge*100:.1f}%\n"
        )
        if concerns:
            explanation += f"Concerns: {' '.join(concerns)}\n"

        return explanation
