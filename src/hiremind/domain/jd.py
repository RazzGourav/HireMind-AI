from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class JobDescription:
    """A loaded and cleaned Job Description document.

    The raw_text preserves the original content for auditing.
    The cleaned_text is normalised for downstream parsing.
    """

    raw_text: str
    cleaned_text: str
    source_path: str | None = None
