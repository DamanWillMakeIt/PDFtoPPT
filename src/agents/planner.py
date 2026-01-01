from typing import List
from src.models.schemas import PresentationPlan, UserProvidedImage
from src.services.llm_service import LLMService

class PlannerAgent:
    def __init__(self):
        self.system_prompt = """
        You are a World-Class Presentation Architect.
        Your goal is to structure a presentation based on a user's request.
        
        ### IMAGE LOGIC (CRITICAL):
        1. You will be provided a list of "AVAILABLE USER IMAGES" (URL + Description).
        2. For each slide, check if one of these images fits the content.
        3. IF A FIT IS FOUND:
           - Set 'image_action' to 'use_provided'.
           - Set 'image_url' to the exact URL from the list.
           - Set 'image_prompt' to empty or null.
        4. IF NO FIT IS FOUND:
           - Set 'image_action' to 'generate'.
           - Write a detailed 'image_prompt' for DALL-E.
        """

    async def create_plan(self, user_prompt: str, available_images: List[UserProvidedImage] = []) -> PresentationPlan:
        
        # Format the image list for the prompt
        img_list_str = "NO USER IMAGES PROVIDED"
        if available_images:
            img_list_str = "\n".join([f"- URL: {img.url} | DESC: {img.description}" for img in available_images])

        user_message = f"""
        USER REQUEST: "{user_prompt}"
        
        ### AVAILABLE USER IMAGES:
        {img_list_str}
        
        Please generate the full Presentation Plan structure.
        """

        print(f"--- 🧠 Planner: Analyzing request with {len(available_images)} provided images ---")
        
        plan = await LLMService.generate_json(
            prompt=user_message,
            system_prompt=self.system_prompt,
            response_model=PresentationPlan
        )
        
        return plan