
import uuid
from domain.value_objects.email_address import EmailAddress
from domain.value_objects.phone_number import PhoneNumber

class Recipient:
    def __init__(
            self, 
            name: str,
            metadata: dict,
            webhook_url: str | None = None,
            phone: PhoneNumber | None = None,
            email: EmailAddress | None = None, 
            id: uuid.UUID | None = None,
        ):
        self.id = id or uuid.uuid4()
        self.name = name
        self.email = email
        self.phone = phone
        self.webhook_url = webhook_url
        self.metadata = metadata

    def update(
        self, 
        name: str | None = None,
        metadata: dict | None = None,
        webhook_url: str | None = None,
        phone: PhoneNumber | None = None,
        email: EmailAddress | None = None, 
    ):
        self.name = name if name is not None else self.name
        self.email = email if email is not None else self.email
        self.phone = phone if phone is not None else self.phone
        self.webhook_url = webhook_url if webhook_url is not None else self.webhook_url
        self.metadata = metadata if metadata is not None else self.metadata

    def __eq__(self, other) -> bool:
        if not isinstance(other, Recipient):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)