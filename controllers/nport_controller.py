from fastapi import APIRouter, HTTPException

from services.nport_service import NportService
from schemas.nport_dto import NportResponseDTO


router = APIRouter()
nport_service = NportService()


@router.get("/{cik}", response_model=NportResponseDTO)
async def get_nport(cik: str):

    try:
        filing_data = await nport_service.get_latest_nport(cik)

        if filing_data is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NPORT_NOT_FOUND",
                    "message": f"No N-PORT filings were found for CIK {cik}."
                }
            )

        return filing_data

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "SEC_SERVICE_ERROR",
                "message": str(exc)
            }
        )