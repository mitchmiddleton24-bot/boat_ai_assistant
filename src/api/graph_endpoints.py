# src/api/graph_endpoints.py

from fastapi import APIRouter, HTTPException

from src.services.ms_graph_client import get_recent_emails

router = APIRouter(
    prefix="/graph",
    tags=["Microsoft Graph"],
)


@router.get("/sample-inbox")
def sample_inbox(top: int = 10):
    """
    Return a sample of recent emails from the configured mailbox.
    Uses application permissions and MS_* environment variables.
    """
    try:
        emails = get_recent_emails(top=top)
        return {
            "count": len(emails),
            "emails": emails,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
