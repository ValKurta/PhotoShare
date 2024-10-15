from pydantic import BaseModel
from typing import Optional
from enum import Enum
from cloudinary import CloudinaryImage



class CropEnum(str, Enum):
    option1 = "fill"
    option2 = "lfill"
    option3 = "fill_pad"
    option4 = "crop"
    option5 = "thumb"
    option6 = "auto"
    option7 = "scale"
    option8 = "fit"
    option9 = "lfit"
    option10 = "mfit"
    option11 = "pad"
    option12 = "lpad"
    option13 = "mpad"


class GravityEnum(str, Enum):
    option0 = None
    option1 = "north"
    option2 = "south"
    option3 = "west"
    option4 = "east"
    option5 = "center"
    option6 = "north_west"
    option7 = "north_east"
    option8 = "south_west"
    option9 = "south_east"
    option10 = "auto"
    option11 = "auto:face"
    option12 = "auto:faces"
    option13 = "auto:body"
    option14 = "auto:ocr_text"
    option15 = "face"
    option16 = "faces"


class PhotoEffectResponse(BaseModel):
    id: int
    description: Optional[str] | None
    url: Optional[str] | None
    transformed_url: Optional[str] | None

    class Config:
        from_attributes = True

