from collections import Counter
from collections.abc import Iterable
from statistics import mean

from hiremind.domain import Candidate


class StatisticsService:
    def compute(self, candidates: Iterable[Candidate]) -> dict[str, object]:
        candidate_list = list(candidates)
        experience_months = [
            candidate.profile.total_experience_months for candidate in candidate_list
        ]

        return {
            "total_candidates": len(candidate_list),
            "countries": self._countries(candidate_list),
            "experience_distribution": self._experience_distribution(experience_months),
            "skill_frequency": self._skill_frequency(candidate_list),
            "education_tier": self._education_tier(candidate_list),
            "notice_period": self._notice_period(candidate_list),
            "recruiter_response": self._recruiter_response(candidate_list),
            "open_to_work": self._open_to_work(candidate_list),
            "github_linked": self._github_linked(candidate_list),
            "average_experience_years": (
                round(mean(experience_months) / 12, 2) if experience_months else 0
            ),
        }

    @staticmethod
    def _countries(candidates: Iterable[Candidate]) -> dict[str, int]:
        counter = Counter(candidate.profile.country or "unknown" for candidate in candidates)
        return dict(counter.most_common())

    @staticmethod
    def _experience_distribution(experience_months: Iterable[int]) -> dict[str, int]:
        buckets = Counter({"0-1": 0, "1-3": 0, "3-5": 0, "5-10": 0, "10+": 0})
        for months in experience_months:
            years = months / 12
            if years < 1:
                buckets["0-1"] += 1
            elif years < 3:
                buckets["1-3"] += 1
            elif years < 5:
                buckets["3-5"] += 1
            elif years < 10:
                buckets["5-10"] += 1
            else:
                buckets["10+"] += 1
        return dict(buckets)

    @staticmethod
    def _skill_frequency(candidates: Iterable[Candidate]) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for candidate in candidates:
            counter.update(skill.name for skill in candidate.skills)
        return dict(counter.most_common())

    @staticmethod
    def _education_tier(candidates: Iterable[Candidate]) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for candidate in candidates:
            if not candidate.education:
                counter["unknown"] += 1
            for education in candidate.education:
                counter[education.tier or "unknown"] += 1
        return dict(counter.most_common())

    @staticmethod
    def _notice_period(candidates: Iterable[Candidate]) -> dict[str, int]:
        buckets = Counter(
            {"immediate": 0, "0-30": 0, "31-60": 0, "61-90": 0, "90+": 0, "unknown": 0}
        )
        for candidate in candidates:
            days = candidate.profile.notice_period_days
            if days is None:
                buckets["unknown"] += 1
            elif days == 0:
                buckets["immediate"] += 1
            elif days <= 30:
                buckets["0-30"] += 1
            elif days <= 60:
                buckets["31-60"] += 1
            elif days <= 90:
                buckets["61-90"] += 1
            else:
                buckets["90+"] += 1
        return dict(buckets)

    @staticmethod
    def _recruiter_response(candidates: Iterable[Candidate]) -> dict[str, int]:
        buckets = Counter({"high": 0, "medium": 0, "low": 0, "unknown": 0})
        for candidate in candidates:
            score = candidate.signals.recruiter_response_score
            if score is None:
                buckets["unknown"] += 1
            elif score >= 0.75:
                buckets["high"] += 1
            elif score >= 0.4:
                buckets["medium"] += 1
            else:
                buckets["low"] += 1
        return dict(buckets)

    @staticmethod
    def _open_to_work(candidates: Iterable[Candidate]) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for candidate in candidates:
            value = candidate.signals.open_to_work
            if value is None:
                value = candidate.profile.open_to_work
            counter[str(value).lower() if value is not None else "unknown"] += 1
        return dict(counter)

    @staticmethod
    def _github_linked(candidates: Iterable[Candidate]) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for candidate in candidates:
            value = candidate.signals.has_github
            counter[str(value).lower() if value is not None else "unknown"] += 1
        return dict(counter)
