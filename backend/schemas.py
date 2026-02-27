from typing import List, Optional
from pydantic import BaseModel, field_validator
from builtins import ValueError
VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


class VoteBase(BaseModel):
    name: str
    day: List[str]
    note: Optional[str] = None

    @field_validator('name')
    @classmethod
    def clean_name(cls, value: str):
        stripped = value.strip()
        if not stripped:
            raise ValueError("Name cannot be empty or just spaces")
        return stripped 
        

    @field_validator('day')
    @classmethod
    def normalize_days(cls, value: List[str]):
        normalized_days = []
        for eachDay in value:
            day_clean = eachDay.strip().capitalize()
            if day_clean in VALID_DAYS:
                normalized_days.append(day_clean)
        if not normalized_days:
            raise ValueError("day is not a valid day")
        return normalized_days

# This is what the user sends (NO ID)  this is what the user gives
class VoteCreate(VoteBase):  # we need this only at add_vote function in main
    pass 

# This is what goes into votes.json (WITH ID) and this is what the system gives not the user
class Vote(VoteBase):
    id: int
    created_at: str = "unknown"  # punem unknow pt ca in cazul in care avem deja voturi si dor dupa am adaugat acest
                                 # var sa nu faca crash codul
    modified_at: Optional[str] = None
    is_active: bool = True

class SystemMetadata(BaseModel):
    last_id: int = 0
