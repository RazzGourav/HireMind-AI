"""Tests for JD document loader."""

from pathlib import Path

import pytest

from hiremind.infrastructure.jd.loader import JDLoader


def test_load_txt_file(tmp_path: Path) -> None:
    """Loader reads .txt files and returns a JobDescription."""
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("Must Have:\n- Python\n- Embeddings\n", encoding="utf-8")

    jd = JDLoader().load(jd_file)

    assert jd.raw_text == "Must Have:\n- Python\n- Embeddings\n"
    assert jd.source_path == str(jd_file)
    assert len(jd.cleaned_text) > 0


def test_load_md_file(tmp_path: Path) -> None:
    """Loader reads .md files and returns a JobDescription."""
    jd_file = tmp_path / "jd.md"
    jd_file.write_text("# Requirements\n\n- FAISS\n- LoRA\n", encoding="utf-8")

    jd = JDLoader().load(jd_file)

    assert "FAISS" in jd.raw_text
    assert jd.source_path == str(jd_file)


def test_load_missing_file_raises(tmp_path: Path) -> None:
    """Loader raises FileNotFoundError for missing files."""
    with pytest.raises(FileNotFoundError, match="JD file not found"):
        JDLoader().load(tmp_path / "nonexistent.txt")


def test_load_unsupported_format_raises(tmp_path: Path) -> None:
    """Loader raises ValueError for unsupported file extensions."""
    jd_file = tmp_path / "jd.pdf"
    jd_file.write_text("content", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported JD format"):
        JDLoader().load(jd_file)


def test_cleaning_is_applied(tmp_path: Path) -> None:
    """Loader applies the cleaning pipeline to the raw text."""
    jd_file = tmp_path / "jd.txt"
    # Multiple spaces and bullet characters.
    jd_file.write_text("•  Python   experience\n•  FAISS   knowledge\n", encoding="utf-8")

    jd = JDLoader().load(jd_file)

    # Multiple spaces should be collapsed.
    assert "  " not in jd.cleaned_text
    # Protected terms should be preserved.
    assert "Python" in jd.cleaned_text
    assert "FAISS" in jd.cleaned_text


def test_cleaned_text_preserves_protected_terms(tmp_path: Path) -> None:
    """Protected terms like FAISS, LoRA, BGE retain their casing."""
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("Experience with FAISS and LoRA and BGE models", encoding="utf-8")

    jd = JDLoader().load(jd_file)

    assert "FAISS" in jd.cleaned_text
    assert "LoRA" in jd.cleaned_text
    assert "BGE" in jd.cleaned_text
