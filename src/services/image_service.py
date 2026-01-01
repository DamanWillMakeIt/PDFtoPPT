import os
import base64
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ImageService:
    @staticmethod
    async def generate_and_save_image(prompt: str, save_path: str):
        try:
            print(f"   -- 🎨 Generating High-Grade Image via gpt-image-1: {save_path}...")

            # GPT-Image-1
            response = await client.images.generate(
                model="gpt-image-1",
                prompt=f"Professional VC pitch deck visual, hyper-realistic, dark mode: {prompt}",
                size="1024x1024",
                n=1
            )

            # Decode Base64 image data
            image_data = base64.b64decode(response.data[0].b64_json)
            with open(save_path, 'wb') as f:
                f.write(image_data)

            print(f"   -- ✅ GPT-Image-1 saved successfully.")
            return True

        except Exception as e:
            print(f"   -- ❌ Image Error: {e}")
            return False
