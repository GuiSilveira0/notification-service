from enum import Enum

class Status(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"

    def can_transition_to(self, new_status: "Status") -> bool:
        allowed = {
            Status.PENDING: [Status.QUEUED, Status.CANCELLED],
            Status.QUEUED: [Status.PROCESSING, Status.CANCELLED],
            Status.PROCESSING: [Status.SENT, Status.FAILED],
            Status.FAILED: [Status.QUEUED],
        }
        return new_status in allowed.get(self, [])