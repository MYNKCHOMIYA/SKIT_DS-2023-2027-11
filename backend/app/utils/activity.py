from sqlalchemy.orm import Session
from app.models.activity import ActivityLog


# Changed 'str' to 'str | None'
def log_system_activity(
    db: Session, user_id: str, action: str, entity_type: str | None = None
):
    """
    Silently records user actions in the database for security and auditing.
    """
    new_log = ActivityLog(user_id=user_id, action=action, entity_type=entity_type)
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log
