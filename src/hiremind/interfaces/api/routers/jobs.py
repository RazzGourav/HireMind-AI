"""Job Description endpoints."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, UploadFile

from hiremind.interfaces.api.schemas.request import JDParsingResponse
from hiremind.services.jd_service import JDService

router = APIRouter(prefix="/api/v1/job", tags=["Job Description"])


@router.post("/parse", response_model=JDParsingResponse)
async def parse_job_description(file: UploadFile = File(...)):
    """Upload and parse a Job Description (DOCX/TXT/MD)."""

    # Save uploaded file temporarily
    suffix = Path(file.filename).suffix if file.filename else ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        service = JDService(
            jd_path=tmp_path,
            ontology_path=Path("configs/ontology.yaml"),
            artifacts_dir=Path("artifacts"),
        )
        result = service.process()

        # We don't save to JSON for the API since it's transient,
        # but we return the parsed lists.
        req_names = [r.name for r in result.requirements.required]
        pref_names = [r.name for r in result.requirements.preferred]
        neg_names = [r.name for r in result.requirements.negative]

        return JDParsingResponse(
            required_skills=req_names,
            preferred_skills=pref_names,
            negative_requirements=neg_names,
        )
    finally:
        # Cleanup
        if tmp_path.exists():
            tmp_path.unlink()
