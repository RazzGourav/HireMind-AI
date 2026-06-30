"""JD Document Loader — supports .docx, .md, and .txt formats."""

from pathlib import Path

from hiremind.domain.jd import JobDescription
from hiremind.infrastructure.jd.cleaner import JDCleaner


class JDLoader:
    """Load a Job Description document from disk.

    Supported formats:
        - .docx (via python-docx)
        - .md   (plain text read)
        - .txt  (plain text read)

    The loader applies the cleaning pipeline automatically and returns
    a ``JobDescription`` domain object with both raw and cleaned text.
    """

    _SUPPORTED_EXTENSIONS = {".docx", ".md", ".txt"}

    def __init__(self, cleaner: JDCleaner | None = None) -> None:
        self._cleaner = cleaner or JDCleaner()

    def load(self, path: str | Path) -> JobDescription:
        """Load and clean a JD document.

        Args:
            path: Path to the JD file (.docx, .md, or .txt).

        Returns:
            A ``JobDescription`` with raw and cleaned text.

        Raises:
            FileNotFoundError: If the path does not exist.
            ValueError: If the file format is unsupported.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"JD file not found: {path}")

        ext = path.suffix.lower()
        if ext not in self._SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported JD format '{ext}'. "
                f"Supported: {', '.join(sorted(self._SUPPORTED_EXTENSIONS))}"
            )

        raw_text = self._read(path, ext)
        cleaned_text = self._cleaner.clean(raw_text)

        return JobDescription(
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            source_path=str(path),
        )

    def _read(self, path: Path, ext: str) -> str:
        """Dispatch to the appropriate reader based on file extension."""
        if ext == ".docx":
            return self._read_docx(path)
        return self._read_text(path)

    @staticmethod
    def _read_docx(path: Path) -> str:
        """Extract text from a Word document, preserving paragraph breaks."""
        from docx import Document

        doc = Document(str(path))
        paragraphs: list[str] = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)
        return "\n".join(paragraphs)

    @staticmethod
    def _read_text(path: Path) -> str:
        """Read a plain-text or markdown file."""
        return path.read_text(encoding="utf-8")
