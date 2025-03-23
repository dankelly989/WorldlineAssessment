from pydantic import BaseModel, Field

from src.models.regex import EXPIRY_DATE, PAN

class Card(BaseModel):
    number: str = Field(pattern=PAN)
    expiry: str = Field(pattern=EXPIRY_DATE)
    name: str

    def to_dict(self):
        """Convert SQLAlchemy object to dictionary, including relationships."""
        # Use class_mapper to access columns and relationships
        data = {}
        for column in class_mapper(self.__class__).columns:
            value = getattr(self, column.key)
            data[column.key] = value
        return data
    