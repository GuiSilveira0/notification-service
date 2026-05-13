import uuid
from datetime import datetime
from domain.value_objects.channel import Channel

class Template:
    def __init__(
        self,
        name: str,
        channel: Channel,
        body_template: str,
        subject_template: str | None = None,
        id: uuid.UUID | None = None,
    ):
        self.id = id or uuid.uuid4()
        self.name = name
        self.channel = channel
        self.subject_template = subject_template
        self.body_template = body_template
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def update(
            self, 
            name: str, 
            body_template: str, 
            subject_template: str | None = None
        ):
        self.name = name
        self.body_template = body_template
        self.subject_template = subject_template
        self.updated_at = datetime.now()

    def __eq__(self, other) -> bool:
        if not isinstance(other, Template):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)