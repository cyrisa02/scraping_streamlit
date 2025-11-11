from pydantic import BaseModel

class VetementSki(BaseModel):
    modele: str
    description: str
    prix: str