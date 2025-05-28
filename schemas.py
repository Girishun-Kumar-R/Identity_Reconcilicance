from pydantic import BaseModel, model_validator
from typing import Optional, List

class IdentifyIn(BaseModel):
    email: Optional[str] = None
    phoneNumber: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_input(cls, values):
        if not values.get("email") and not values.get("phoneNumber"):
            raise ValueError("Either email or phoneNumber is required.")
        return values


class ContactOut(BaseModel):
    primaryContactId: int
    emails: List[str]
    phoneNumbers: List[str]
    secondaryContactIds: List[int]

class IdentifyOut(BaseModel):
    contact: ContactOut