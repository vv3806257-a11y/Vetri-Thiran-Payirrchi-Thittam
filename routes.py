from fastapi import APIRouter, HTTPException

from backend.schemas import DocumentRequest, DocumentResponse
from ai_core.gemini_generator import GeminiDocumentGenerator

router = APIRouter(tags=["documents"])


@router.post("/generate", response_model=DocumentResponse)
def generate_document(request: DocumentRequest):
    """Generate a legal document draft using Gemini or demo mode."""
    try:
        generator = GeminiDocumentGenerator()

        content, demo_mode = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
        )

        return DocumentResponse(
            document_type=request.document_type,
            content=content,
            demo_mode=demo_mode,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document generation failed: {exc}",
        ) from exc
