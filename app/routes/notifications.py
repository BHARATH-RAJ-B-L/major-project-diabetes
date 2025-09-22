# backend/app/routes/notifications.py
from fastapi import APIRouter, Depends
from ..auth import get_db, get_current_user
from sqlalchemy.orm import Session
from ..crud import get_unread_notifications, mark_notification_read
from ..schemas import NotificationOut
from typing import List

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/unread", response_model=List[NotificationOut], dependencies=[Depends(get_current_user)])
def unread(db: Session = Depends(get_db)):
    notifs = get_unread_notifications(db)
    return notifs

@router.post("/{notif_id}/mark-read", dependencies=[Depends(get_current_user)])
def mark_read(notif_id: int, db: Session = Depends(get_db)):
    notif = mark_notification_read(db, notif_id)
    return {"ok": True}
