import asyncio
from typing import List
from src.models.schemas import SlidePlan, PresentationPlan
from src.services.llm_service import LLMService

class DesignerAgent:
    def __init__(self):
        self.base_system_prompt = """
        You are an expert Frontend Developer specializing in High-Impact Slides.
        Your task is to write a single HTML file containing the slide.
        
        RULES:
        1. Use the provided Color Palette and Fonts STRICTLY.
        2. The output must be pure HTML/CSS (in <style> tags). No external CSS files.
        3. Make it RESPONSIVE (16:9 aspect ratio).
        4. Use modern CSS (Flexbox/Grid, gradients, box-shadows).
        5. Return ONLY the HTML code. No markdown backticks.
        6. IMPORTANT: If an image path/url is provided, you MUST use it.
        """

    async def _generate_single_variant(self, slide: SlidePlan, master_plan: PresentationPlan, variant_id: int) -> str:
        """
        Worker function to generate 1 HTML variant.
        """
        
        image_instruction = ""
        
        # CASE A: Local Generated Image
        if slide.image_prompt and slide.image_prompt.startswith("./"):
            image_instruction = f"""
            IMAGE ASSETS:
            - Use the local background image: "{slide.image_prompt}"
            - Example: <div style="background-image: url('{slide.image_prompt}')">
            """
            
        # CASE B: User Provided URL
        elif slide.image_action == 'use_provided' and slide.image_url:
            image_instruction = f"""
            IMAGE ASSETS:
            - Use this specific external image URL: "{slide.image_url}"
            - IMPORTANT: You must use this exact URL in an <img> tag or background-image.
            - Ensure object-fit is handled gracefully.
            """
            
        # CASE C: Placeholder/Generation
        elif slide.image_action == 'generate':
             image_instruction = "Design this slide knowing a high-quality background image will be placed behind the text."

        prompt = f"""
        Create HTML for Slide ID: {slide.id} ({slide.type})
        
        CONTENT:
        Title: {slide.title}
        Points: {slide.content_points}
        
        {image_instruction}
        
        DESIGN SPECS:
        Style: {master_plan.visual_style}
        Colors: {master_plan.color_palette_hex}
        Fonts: {master_plan.font_pairing}
        Layout Instruction: {slide.layout_notes}
        
        Make this Variant #{variant_id} unique and creative.
        """
        
        # Call Claude (via generate_code)
        html_code = await LLMService.generate_code(prompt, self.base_system_prompt)
        
        # Cleanup
        clean_code = html_code.replace("```html", "").replace("```", "").strip()
        return clean_code

    async def generate_slide_variants(self, slide: SlidePlan, master_plan: PresentationPlan) -> List[str]:
        print(f"--- 🎨 Designer: Spawning 3 workers for Slide {slide.id} ---")
        
        tasks = [
            self._generate_single_variant(slide, master_plan, 1),
            self._generate_single_variant(slide, master_plan, 2),
            self._generate_single_variant(slide, master_plan, 3)
        ]
        
        results = await asyncio.gather(*tasks)
        return results