from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# --- NEW: Structure for the images you send in the CURL ---
class UserProvidedImage(BaseModel):
    url: str
    description: str

# --- Slide Specific Models ---
class SlidePlan(BaseModel):
    id: int
    type: Literal['title', 'agenda', 'content_text', 'content_image', 'content_data'] = Field(..., description="The functional type of the slide")
    title: str = Field(..., description="The main headline for this specific slide")
    content_points: List[str] = Field(..., description="Bullet points, stats, or text body")
    
    # Updated Image Fields
    image_action: Literal['use_provided', 'generate', 'none'] = Field(..., description="What to do about images")
    image_prompt: Optional[str] = Field(None, description="Detailed DALL-E prompt if 'generate' is selected")
    image_url: Optional[str] = Field(None, description="The specific URL selected from user provided images")
    
    layout_notes: str = Field(..., description="Specific instructions for the HTML layout (e.g., 'Split screen', 'Grid', 'Centered')")

# --- Master Plan Model ---
class PresentationPlan(BaseModel):
    topic: str
    target_audience: str
    visual_style: str = Field(..., description="Design keywords (e.g., 'Minimalist', 'Cyberpunk', 'Corporate')")
    color_palette_hex: List[str] = Field(..., description="List of 3-5 Hex codes")
    font_pairing: str = Field(..., description="Primary and Secondary fonts (e.g., 'Roboto / Open Sans')")
    slides: List[SlidePlan]