from app.modules.notification.repositories import NotificationRepository
from core.services.BaseService import BaseService


class NotificationService(BaseService):
    def __init__(self):
        super().__init__(NotificationRepository())
