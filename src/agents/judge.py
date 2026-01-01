from typing import List
from src.models.schemas import SlidePlan, PresentationPlan
from src.services.llm_service import LLMService

class JudgeAgent:
    def __init__(self):
        self.system_prompt = """
        You are a Senior UI/UX Designer and Code Quality QA.
        You will receive 3 HTML variants for a presentation slide.
        
        Your task:
        1. Check for CSS/HTML errors (broken tags, missing styles).
        2. Evaluate design quality (Does it match the requested style?).
        3. Check legibility (Contrast, font sizes).
        
        Return ONLY the integer index (0, 1, or 2) of the best variant. 
        Do not add any explanation. Just the number.
        """

    async def select_best_variant(self, variants: List[str], slide: SlidePlan, master_plan: PresentationPlan) -> str:
        """
        Sends the 3 variants to the LLM and asks it to pick the winner.
        """
        # Prepare the context for the Judge
        prompt = f"""
        SLIDE CONTEXT: {slide.title} ({slide.type})
        STYLE GOAL: {master_plan.visual_style}
        
        --- VARIANT 0 ---
        {variants[0][:1000]}... (truncated for brevity)
        
        --- VARIANT 1 ---
        {variants[1][:1000]}...
        
        --- VARIANT 2 ---
        {variants[2][:1000]}...
        
        Which variant is the best code? Return 0, 1, or 2.
        """
        
        print(f"--- ⚖️ Judge: Reviewing 3 variants for Slide {slide.id}... ---")
        
        try:
            # We treat this as a text generation task expecting a single digit
            response = await LLMService.generate_text(prompt, self.system_prompt)
            best_index = int(response.strip())
            
            # Safety check
            if best_index not in [0, 1, 2]:
                raise ValueError("Judge returned invalid index")
                
            print(f"   -- 🏆 Judge selected Variant {best_index}")
            return variants[best_index]
            
        except Exception as e:
            print(f"   -- ⚠️ Judge failed ({e}), defaulting to Variant 0")
            return variants[0]