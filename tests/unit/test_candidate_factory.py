from hiremind.services import CandidateFactory


def test_candidate_factory_builds_domain_candidate_from_json_aliases() -> None:
    candidate = CandidateFactory.from_raw(
        {
            "id": "CAND_123",
            "profile": {
                "current_title": "ML Engineer",
                "country": "India",
                "total_experience_months": 72,
            },
            "career": [{"company": "Acme", "title": "Engineer"}],
            "education": [{"institution": "IIT", "tier": "tier_1"}],
            "skills": [{"name": "Python", "duration_months": 60}],
            "redrob_signals": {
                "github_activity_score": 0.9,
                "has_github": True,
            },
        }
    )

    assert candidate.candidate_id == "CAND_123"
    assert candidate.profile.current_title == "ML Engineer"
    assert candidate.profile.experience_years == 6
    assert candidate.career_history[0].company == "Acme"
    assert candidate.skills[0].name == "Python"
    assert candidate.signals.github_activity_score == 0.9
