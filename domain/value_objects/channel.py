from enum import Enum

class Channel(Enum):
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"