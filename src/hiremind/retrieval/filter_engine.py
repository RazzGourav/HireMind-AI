"""Filter Engine — Structured filtering for candidate profiles."""


from hiremind.domain.candidate import Candidate
from hiremind.domain.requirement import ParsedRequirements


class StructuredFilterEngine:
    """Filters candidate collections based on experience, work modes, notice periods, and relocation."""

    def filter_candidate(
        self,
        candidate: Candidate,
        requirements: ParsedRequirements | None = None,
        max_notice_days: int = 90,
        allowed_work_modes: list[str] | None = None,
        require_relocation_willingness: bool = False,
        mandatory_skills: list[str] | None = None,
    ) -> bool:
        """Check if candidate passes all active structured filters. Returns True if passed."""
        # 1. Experience years filter
        if requirements and requirements.experience:
            candidate_exp = candidate.profile.experience_years or 0.0
            min_exp = requirements.experience.min_years
            max_exp = requirements.experience.max_years

            # if min_exp is not None and candidate_exp < min_exp:
            #     return False
            # if max_exp is not None and candidate_exp > max_exp:
            #     return False

        # 2. Notice period filter
        # If candidate notice period exceeds limit, filter them out
        notice_period = getattr(candidate.signals, "notice_period_days", None)
        if notice_period is not None and notice_period > max_notice_days:
            return False

        # 3. Work mode filter
        if allowed_work_modes:
            mode = getattr(candidate.signals, "preferred_work_mode", None)
            if mode:
                mode_lower = mode.lower()
                allowed_lowered = [m.lower() for m in allowed_work_modes]
                # If remote is allowed and candidate prefers remote, they pass.
                # Otherwise, check if candidate's mode is directly allowed.
                if mode_lower not in allowed_lowered:
                    # If not directly allowed, check if they are willing to relocate if required onsite/hybrid
                    willing_to_relocate = getattr(candidate.signals, "willing_to_relocate", False)
                    if not willing_to_relocate:
                        return False

        # 4. Mandatory skills check
        if mandatory_skills:
            candidate_skills = {s.name.lower() for s in candidate.skills}
            # Also check candidate's normalised/explicit skills if available
            # Let's verify they have at least one of the mandatory skills
            has_mandatory = False
            for skill in mandatory_skills:
                if skill.lower() in candidate_skills:
                    has_mandatory = True
                    break
            if not has_mandatory:
                return False

        return True

    def apply_filters(
        self,
        candidates: list[Candidate],
        requirements: ParsedRequirements | None = None,
        max_notice_days: int = 90,
        allowed_work_modes: list[str] | None = None,
        require_relocation_willingness: bool = False,
        mandatory_skills: list[str] | None = None,
    ) -> list[Candidate]:
        """Apply filters to a list of candidates and return those that pass."""
        return [
            c
            for c in candidates
            if self.filter_candidate(
                c,
                requirements=requirements,
                max_notice_days=max_notice_days,
                allowed_work_modes=allowed_work_modes,
                require_relocation_willingness=require_relocation_willingness,
                mandatory_skills=mandatory_skills,
            )
        ]
