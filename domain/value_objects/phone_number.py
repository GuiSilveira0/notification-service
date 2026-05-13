from dataclasses import dataclass
import re

PHONE_REGEX = re.compile(r"^\+[1-9]\d{9,14}$")

@dataclass(frozen=True)
class PhoneNumber:
    value: str

    def __post_init__(self):
        if not PHONE_REGEX.match(self.value):
            raise ValueError(f"Telefone inválido: {self.value}")

    def __str__(self) -> str:
        return self.value
