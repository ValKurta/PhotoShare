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


class SpecialEffectsEnum(str, Enum):
    # option1 = "adv_redeye"
    option2 = "anti_removal"
    option3 = "art:incognito"
    option15 = "cartoonify"


class ColorEffectEnum(str, Enum):
    # option1 = "auto_brightness"
    # option2 = "auto_color"
    # option3 = "auto_contrast"
    option4 = "assist_colorblind"
    option5 = "brightness"
    option6 = "brightness_hsb"
    option7 = "colorize"
    option8 = "contrast"
    option9 = "blue"
    option0 = "sepia"
    option1 = "sharpen"
    option2 = 'unsharp_mask'


class BackgroundEffect(str, Enum):
    option8 = "background_removal"
    option9 = "bgremoval"


class BlurEffect(str, Enum):
    option11 = "blur"
    option12 = "blur_faces"


class CameraEffect(str, Enum):
    option17 = "camera"


class PhotoEffectResponse(BaseModel):
    id: int
    description: Optional[str] | None
    url: Optional[str] | None
    transformed_url: Optional[str] | None

    class Config:
        from_attributes = True

