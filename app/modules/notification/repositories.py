from app.modules.notification.models import Notification
from core.repositories.BaseRepository import BaseRepository


class NotificationRepository(BaseRepository):
    def __init__(self):
        super().__init__(Notification)
