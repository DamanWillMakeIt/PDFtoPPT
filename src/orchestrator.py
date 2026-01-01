import asyncio
import os
import uuid
from src.agents.planner import PlannerAgent
from src.agents.designer import DesignerAgent
from src.agents.judge import JudgeAgent
from src.services.browser_service import BrowserService
from src.services.ppt_service import PPTService
from src.services.image_service import ImageService
from src.models.schemas import UserProvidedImage

class Orchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.designer = DesignerAgent()
        self.judge = JudgeAgent()
        self.semaphore = asyncio.Semaphore(2)
        # TRACKER: Keep a list of every temporary file created
        self.temp_files = []

    def register_temp_file(self, path: str):
        """Adds a file to the death row (to be deleted later)."""
        if path and path not in self.temp_files:
            self.temp_files.append(path)

    async def process_slide(self, slide, plan) -> str:
        async with self.semaphore:
            print(f"🚀 Processing Slide {slide.id}: {slide.type}")
            
            image_task = None
            
            # CASE 1: GENERATE NEW IMAGE
            if slide.image_action == 'generate' and slide.image_prompt:
                # Add UUID to prevent collision
                local_image_filename = f"slide_{slide.id}_{uuid.uuid4().hex[:6]}.png"
                local_image_path = os.path.join("temp", local_image_filename)
                
                image_task = asyncio.create_task(
                    ImageService.generate_and_save_image(slide.image_prompt, local_image_path)
                )
                slide.image_prompt = f"./{local_image_filename}"
                self.register_temp_file(local_image_path) # Mark for cleanup
            
            # CASE 2: USE PROVIDED IMAGE
            elif slide.image_action == 'use_provided' and slide.image_url:
                print(f"   -- 📎 Using provided image: {slide.image_url[:30]}...")

            # CODE GENERATION
            code_task = asyncio.create_task(
                self.designer.generate_slide_variants(slide, plan)
            )

            if image_task:
                await image_task
            variants = await code_task

            # RENDER
            best_html = await self.judge.select_best_variant(variants, slide, plan)
            
            # Save HTML temporarily (Add UUID)
            html_filename = f"slide_{slide.id}_{uuid.uuid4().hex[:6]}.html"
            html_path = os.path.join("temp", html_filename)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(best_html)
            self.register_temp_file(html_path) # Mark for cleanup
            
            # Render final image (Add UUID)
            render_path = os.path.join("temp", f"slide_{slide.id}_final_{uuid.uuid4().hex[:6]}.png")
            print(f"   -- 📸 Rendering Slide {slide.id}...")
            
            # Note: BrowserService needs to handle the HTML file path correctly
            # Assuming it can load "file://{abs_path}" or just relative path if in same root
            await BrowserService.render_html_to_image(best_html, render_path)
            
            self.register_temp_file(render_path) # Mark for cleanup
            
            return render_path

    def cleanup_garbage(self):
        """Deletes all tracked temporary files."""
        print(f"🧹 Cleaning up {len(self.temp_files)} intermediate assets...")
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"⚠️ Failed to delete {file_path}: {e}")
        self.temp_files = []

    async def run_workflow(self, user_prompt: str, user_images: list = []) -> str:
        print("\n=== STEP 1: PLANNING ===")
        os.makedirs("temp", exist_ok=True)
        
        processed_images = []
        for img in user_images:
            if isinstance(img, dict):
                processed_images.append(UserProvidedImage(**img))
            else:
                processed_images.append(img)
                
        plan = await self.planner.create_plan(user_prompt, processed_images)
        print(f"📋 Plan created: {len(plan.slides)} slides. Style: {plan.visual_style}")
        
        print(f"\n=== STEP 2: CONCURRENT GENERATION ===")
        tasks = [self.process_slide(slide, plan) for slide in plan.slides]
        final_slide_images = await asyncio.gather(*tasks)
            
        print("\n=== STEP 3: COMPILING PPTX ===")
        # Use UUID for the PPT file too
        output_filename = f"presentation_{uuid.uuid4().hex}.pptx"
        output_path = os.path.join("temp", output_filename)
        
        PPTService.create_presentation(final_slide_images, output_path)
        
        # CLEANUP: Delete all pngs/htmls now
        self.cleanup_garbage()
        
        print(f"✅ DONE! Created {output_path}")
        return output_path