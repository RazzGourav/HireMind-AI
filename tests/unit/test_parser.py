"""Tests for the rule-based JD requirement parser."""

from hiremind.infrastructure.jd.parser import JDParser


def test_parse_required_skills() -> None:
    """Parser extracts skills from a 'must have' section."""
    text = "Must Have:\n" "- Python\n" "- Embeddings\n" "- Retrieval\n" "- Ranking\n"
    result = JDParser().parse(text)

    names = [r.name for r in result.required]
    assert "Python" in names
    assert "Embeddings" in names
    assert "Retrieval" in names
    assert "Ranking" in names
    assert all(r.required is True for r in result.required)


def test_parse_preferred_skills() -> None:
    """Parser extracts skills from a 'nice to have' section."""
    text = "Must Have:\n" "- Python\n" "\n" "Nice to Have:\n" "- LoRA\n" "- Distributed Systems\n"
    result = JDParser().parse(text)

    preferred_names = [r.name for r in result.preferred]
    assert "LoRA" in preferred_names
    assert "Distributed Systems" in preferred_names
    assert all(r.required is False for r in result.preferred)


def test_parse_negative_signals_from_section() -> None:
    """Parser extracts negatives from an explicit negative section."""
    text = (
        "Must Have:\n"
        "- Python\n"
        "\n"
        "Not Looking For:\n"
        "- Research Only\n"
        "- LangChain Only\n"
    )
    result = JDParser().parse(text)

    negative_names = [n.name for n in result.negative]
    assert "Research Only" in negative_names
    assert "LangChain Only" in negative_names


def test_parse_experience_range() -> None:
    """Parser extracts min/max years from a range pattern."""
    text = "We need someone with 5-9 years of experience in ML."
    result = JDParser().parse(text)

    assert result.experience.min_years == 5
    assert result.experience.max_years == 9


def test_parse_experience_minimum() -> None:
    """Parser extracts minimum years from explicit pattern."""
    text = "Minimum 3 years of experience required."
    result = JDParser().parse(text)

    assert result.experience.min_years == 3


def test_parse_experience_bare() -> None:
    """Parser extracts years from a bare 'X+ years' pattern."""
    text = "7+ years of experience in software engineering."
    result = JDParser().parse(text)

    assert result.experience.min_years == 7


def test_parse_empty_text() -> None:
    """Parser handles empty input gracefully."""
    result = JDParser().parse("")

    assert len(result.required) == 0
    assert len(result.preferred) == 0
    assert len(result.negative) == 0
    assert result.experience.min_years is None


def test_parse_no_sections() -> None:
    """Parser treats text without section headers as required by default."""
    text = "- Python\n- FAISS\n- Embeddings\n"
    result = JDParser().parse(text)

    # All items default to the 'required' section.
    names = [r.name for r in result.required]
    assert "Python" in names
    assert "FAISS" in names


def test_parse_deduplicates_items() -> None:
    """Parser deduplicates items within a section."""
    text = "Must Have:\n- Python\n- Python\n- Python\n"
    result = JDParser().parse(text)

    names = [r.name for r in result.required]
    assert names.count("Python") == 1


def test_parse_skips_long_sentences() -> None:
    """Parser skips items longer than 80 chars (likely full sentences, not skills)."""
    text = "Must Have:\n" "- Python\n" "- " + "a" * 100 + "\n"
    result = JDParser().parse(text)

    names = [r.name for r in result.required]
    assert "Python" in names
    assert len(names) == 1


def test_inline_negative_detection() -> None:
    """Parser detects inline negative signals like 'not just research'."""
    text = "We are not looking for pure research profiles."
    result = JDParser().parse(text)

    negative_names = [n.name for n in result.negative]
    assert any("research" in name.lower() for name in negative_names)
