from pydantic import BaseModel
from typing import List, Optional
import enum


class SectionType(enum.Enum):
    VERSE = "VERSE"
    CHORUS = "CHORUS"
    BRIDGE = "BRIDGE"
    OUTRO = "OUTRO"
    # PRE_CHORUS = "PRE_CHORUS"

class LyricsSection(BaseModel):
    section_type: SectionType 
    content: str

class SongStructure(BaseModel):
    title: str
    sections: List[LyricsSection]