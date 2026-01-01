from typing import List, Dict
from src.models.schemas import PresentationPlan, UserProvidedImage, SlidePlan
from src.services.llm_service import LLMService

class PlannerAgent:
    def __init__(self):
        # We build the prompt dynamically in create_plan to include the image list cleanly
        pass

    async def create_plan(self, user_prompt: str, available_images: List[UserProvidedImage] = []) -> PresentationPlan:
        
        # --- 1. PRE-PROCESSING: Create an Asset Map ---
        # We hide the long URLs from the LLM to save tokens and focus.
        # We only show the LLM: "IMG_0: Description..."
        asset_map = {}
        img_context_str = "NO USER IMAGES PROVIDED."
        
        if available_images:
            lines = []
            for idx, img in enumerate(available_images):
                key = f"IMG_{idx}" # Simple token for the LLM
                asset_map[key] = img.url # Store real URL for later
                
                # Use provided description or a fallback
                desc = img.description if img.description else "User provided image"
                lines.append(f"- ID: {key} | Description: {desc}")
            
            img_context_str = "\n".join(lines)

        # --- 2. SYSTEM PROMPT ---
        system_prompt = """
        You are a World-Class Presentation Architect.
        
        TASK:
        Structure a presentation based EXACTLY on the USER REQUEST (Topic & Slide Count).
        
        ### IMAGE RULES (CRITICAL):
        1. You have a list of available assets with IDs (e.g., IMG_0, IMG_1).
        2. For each slide, check the available assets.
        3. IF A MATCH FOUND: 
           - Set 'image_action' to 'use_provided'.
           - Set 'image_url' to the ID string (e.g. "IMG_0").
        4. IF NO MATCH: 
           - Set 'image_action' to 'generate'.
           - Write a detailed 'image_prompt'.
        
        ### CONTENT RULES:
        1. Respect the requested slide count.
        2. Ensure the text content is deeply relevant to the USER REQUEST topic.
        """

        # --- 3. USER MESSAGE ---
        user_message = f"""
        USER REQUEST: "{user_prompt}"
        
        ### AVAILABLE ASSETS:
        {img_context_str}
        
        Generate the PresentationPlan JSON now.
        """

        print(f"--- 🧠 Planner: Analyzing request with {len(available_images)} images ---")
        
        # --- 4. CALL LLM ---
        plan: PresentationPlan = await LLMService.generate_json(
            prompt=user_message,
            system_prompt=system_prompt,
            response_model=PresentationPlan
        )
        
        # --- 5. POST-PROCESSING: Swap IDs back to URLs ---
        # This is the magic step. We replace "IMG_0" with the actual Cloudinary URL.
        print("   Mapping assigned images to slides...")
        for slide in plan.slides:
            # Check if the LLM assigned a provided image ID
            if slide.image_action == 'use_provided' and slide.image_url in asset_map:
                asset_id = slide.image_url
                real_url = asset_map[asset_id]
                
                # Swap it!
                slide.image_url = real_url
                print(f"   📎 Slide '{slide.title}' <== {asset_id} (Matched)")
            
            # Safety Check: If LLM tried to use provided but messed up the ID
            elif slide.image_action == 'use_provided':
                print(f"   ⚠️ Warning: LLM tried to use invalid ID '{slide.image_url}'. Reverting to generation.")
                slide.image_action = 'generate'
                slide.image_prompt = f"Image for slide about {slide.title}"
                slide.image_url = None

        return plan
