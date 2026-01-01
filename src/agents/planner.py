from typing import List
from src.models.schemas import PresentationPlan, UserProvidedImage
from src.services.llm_service import LLMService

class PlannerAgent:
    def __init__(self):
        self.system_prompt = """
        
        You are a World-Class Presentation Architect.
        Your goal is to structure a presentation based on a user's vague request.Also use verified and detailed latest data in the presentation not vague lines.
        
        1. ANALYZE: Determine the tone, audience, and core message.
        2. DESIGN: Select a cohesive color palette (Hex codes) and font pairing that matches the tone.
        3. STRUCTURE: Create a slide-by-slide outline.
           - Ensure the flow is logical (Title -> Intro -> Details -> Conclusion).
           - Write detailed 'layout_notes' for the web designers who will code this later.
           - If the user provides images, assign them logicially. If not, write prompts to generate them.
          
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
    #og
