# backend/app/crud.py
from sqlalchemy.orm import Session
from . import models
from passlib.hash import bcrypt
from datetime import datetime

def create_user(db: Session, username: str, email: str, password: str, is_admin: bool = False):
    pwd_hash = bcrypt.hash(password)
    user = models.User(username=username, email=email, password_hash=pwd_hash, is_admin=is_admin)
    db.add(user); db.commit(); db.refresh(user)
    return user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).get(user_id)

def verify_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not bcrypt.verify(password, user.password_hash):
        return None
    return user

def create_upload(db: Session, uploader_id: int, filename: str, original_name: str):
    upload = models.Upload(uploader_id=uploader_id, filename=filename, original_name=original_name, created_at=datetime.utcnow())
    db.add(upload); db.commit(); db.refresh(upload)
    return upload

def create_notification(db: Session, title: str, message: str, payload: dict = None):
    notif = models.Notification(title=title, message=message, payload=payload, is_read=False, created_at=datetime.utcnow())
    db.add(notif); db.commit(); db.refresh(notif)
    return notif

def get_unread_notifications(db: Session, limit: int = 50):
    return db.query(models.Notification).filter(models.Notification.is_read == False).order_by(models.Notification.created_at.desc()).limit(limit).all()

def mark_notification_read(db: Session, notif_id: int):
    notif = db.query(models.Notification).get(notif_id)
    if notif:
        notif.is_read = True
        db.commit()
        db.refresh(notif)
    return notif
