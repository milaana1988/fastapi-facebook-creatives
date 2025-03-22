import json
from app.utils.vision import analyze_creative_features
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.models import Creative


def create_or_update_creatives_batch(db: Session, creatives_data: List[Dict[str, Any]]) -> List[Creative]:
    """
    Creates or updates a batch of creatives in the database.

    Filters the input data to include only creatives with a valid image URL.
    Checks for existing creatives in the database using their creative IDs,
    and updates them if they exist. If not, new creative entries are created.
    Commits changes to the database and refreshes the state of the updated and
    newly created creative objects.

    Args:
        db (Session): The database session used for querying and committing.
        creatives_data (List[Dict[str, Any]]): List of creatives data dictionaries
            containing details such as creative_id, metrics, campaign, image_url,
            labels, and image_hash.

    Returns:
        List[Creative]: A list of Creative objects that were updated or created.
    """

    filtered_data = [
        creative for creative in creatives_data
        if creative.get("creative_details", {}).get("image_url")
    ]

    creative_ids = [str(creative.get("creative_id"))
                    for creative in filtered_data if creative.get("creative_id")]

    existing_creatives = db.query(Creative).filter(
        Creative.creative_id.in_(creative_ids)).all()
    existing_map = {str(creative.creative_id)
                        : creative for creative in existing_creatives}

    new_creatives = []
    updated_creatives = []

    for creative in filtered_data:
        serialized_data = {
            "creative_id": creative.get("creative_id"),
            "performance_metrics": json.dumps(creative.get("metrics")) if creative.get("metrics") is not None else None,
            "relevant_metadata": json.dumps(creative.get("campaign")) if creative.get("campaign") is not None else None,
            "image_url": creative.get("creative_details", {}).get("image_url"),
            "labels": json.dumps(creative.get("labels")) if creative.get("labels") is not None else None,
            "image_hash": creative.get("image_hash"),
        }
        key = str(serialized_data["creative_id"])
        if key in existing_map:
            record = existing_map[key]
            record.performance_metrics = serialized_data["performance_metrics"]
            record.relevant_metadata = serialized_data["relevant_metadata"]
            record.image_url = serialized_data["image_url"]
            record.labels = serialized_data["labels"]
            record.image_hash = serialized_data["image_hash"]
            updated_creatives.append(record)
        else:
            new_obj = Creative(**serialized_data)
            new_creatives.append(new_obj)

    if new_creatives:
        db.add_all(new_creatives)

    db.commit()

    for creative in updated_creatives:
        db.refresh(creative)
    for creative in new_creatives:
        db.refresh(creative)

    return new_creatives + updated_creatives


def get_creatives_by_cursor(db: Session, cursor: Optional[int] = None, limit: int = 10):
    """
    Get a paginated list of ad creatives from the database.

    Args:
        db (Session): The database session to use for the query.
        cursor (int, optional): The ID of the last ad creative returned in the previous call, or None if this is the first call.
        limit (int, optional): The maximum number of ad creatives to return in this call. Defaults to 10.

    Returns:
        tuple: A tuple containing a list of ad creative objects, a boolean indicating whether there are more ad creatives available, and the ID of the last ad creative returned.
    """
    query = db.query(Creative).order_by(Creative.id.asc())
    if cursor:
        query = query.filter(Creative.id > cursor)

    items = query.limit(limit + 1).all()
    has_more = len(items) > limit
    next_cursor = items[limit].id if has_more else None

    return items[:limit], has_more, next_cursor


def update_creative_features(creative_id: int, db: Session):
    """
    Updates the labels of a creative in the database using Google Cloud Vision.

    Retrieves the creative from the database by its ID, and if it exists and has an image URL,
    calls the analyze_creative_features function to obtain labels for the image. The labels are
    then stored in the database by updating the creative's labels attribute.

    Args:
        creative_id (int): The ID of the creative to update.
        db (Session): The database session to use for querying and committing.
    """
    creative = db.query(Creative).filter(
        Creative.creative_id == creative_id).first()
    if creative and creative.image_url:
        try:
            labels = analyze_creative_features(creative.image_url)
            creative.labels = json.dumps(labels)
            db.commit()
        except Exception as e:
            print("Error in background feature extraction:", e)
