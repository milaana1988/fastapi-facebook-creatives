from app.schemas import PaginatedResponse, settings
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import creatives as crud_creatives
from app.utils.helper_functions import get_best_creatives


router = APIRouter()

ACCESS_TOKEN = settings.access_token
API_VERSION = settings.api_version
CLIENT_ID = settings.client_id
CLIENT_SECRET = settings.client_secret
FB_API_URL = settings.fb_api_url


@router.get("/fetch-fb-and-store-best-creatives")
def load_creatives_from_api(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Loads the best creatives from the external API, saves them to the database
    and schedules a background task to extract features from each creative's
    image. Returns a list of the saved creative IDs.
    """
    best_creatives = get_best_creatives()
    creatives_data = best_creatives.get("best_creatives", [])
    if not creatives_data:
        raise HTTPException(
            status_code=404, detail="No creatives data found in API response")
    saved_creatives = crud_creatives.create_or_update_creatives_batch(
        db, creatives_data)
    for saved_creative in saved_creatives:
        background_tasks.add_task(
            crud_creatives.update_creative_features, saved_creative.creative_id, db)
    return {"saved_creatives": [creative.creative_id for creative in saved_creatives]}


@router.get("/creatives", response_model=PaginatedResponse)
def get_creatives(cursor: int = None, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get a paginated list of ad creatives.

    Args:
        cursor (int, optional): The ID of the last ad creative returned in the previous call, or None if this is the first call.
        limit (int, optional): The maximum number of ad creatives to return in this call. Defaults to 10.
        db (Session, optional): The database session to use for the query. Defaults to a new session.

    Returns:
        PaginatedResponse: A dictionary with three keys: "creative_details" (a list of ad creative details), "has_more" (a boolean indicating whether there are more ad creatives available), and "next_cursor" (the ID of the last ad creative returned, or None if there are no more).
    """
    items, has_more, next_cursor = crud_creatives.get_creatives_by_cursor(
        db, cursor, limit)
    return {"creative_details": items, "has_more": has_more, "next_cursor": next_cursor}
