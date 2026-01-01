import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
import google.generativeai as genai

load_dotenv()

# =========================
# OpenAI (ASYNC – stable)
# =========================
openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# =========================
# Gemini (SYNC – REQUIRED)
# =========================
genai.configure(
    api_key=os.getenv("GOOGLE_API_KEY")
)


class LLMService:
    """
    LLM Routing Layer

    - JSON / Judging → GPT-4o (Async)
    - Creative Code / CSS → Gemini 3 Pro Preview (Sync)
    - Fallback → GPT-4o
    """

    # -------------------------
    # JSON (Structured Output)
    # -------------------------
    @staticmethod
    async def generate_json(prompt: str, system_prompt: str, response_model):
        try:
            completion = await openai_client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                response_format=response_model,
            )
            return completion.choices[0].message.parsed

        except Exception as e:
            print(f"❌ Error in JSON generation: {e}")
            return None

    # -------------------------
    # Code / Design Generation
    # -------------------------
    @staticmethod
    async def generate_code(prompt: str, system_prompt: str) -> str:
        """
        Gemini is SYNC.
        We run it inside a thread so FastAPI stays async-safe.
        """

        loop = asyncio.get_running_loop()

        # ---- Gemini 3 Pro Preview (highest quality) ----
        try:
            return await loop.run_in_executor(
                None,
                LLMService._gemini_generate,
                "gemini-3-pro-preview",
                prompt,
                system_prompt,
            )

        except Exception as e:
            print(f"⚠️ Gemini 3 Pro Preview failed: {e}. Trying Gemini Flash...")

            # ---- Gemini Flash ----
            try:
                return await loop.run_in_executor(
                    None,
                    LLMService._gemini_generate,
                    "gemini-2.5-flash",
                    prompt,
                    system_prompt,
                )

            except Exception as e2:
                print(f"⚠️ Gemini Flash failed: {e2}. Falling back to GPT-4o...")
                return await LLMService.generate_text(prompt, system_prompt)

    # -------------------------
    # Gemini (SYNC CORE)
    # -------------------------
    @staticmethod
    def _gemini_generate(model_name: str, prompt: str, system_prompt: str) -> str:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt,
        )
        response = model.generate_content(prompt)
        return response.text

    # -------------------------
    # Plain Text (OpenAI)
    # -------------------------
    @staticmethod
    async def generate_text(prompt: str, system_prompt: str) -> str:
        try:
            completion = await openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ]
            )
            return completion.choices[0].message.content

        except Exception as e:
            print(f"❌ Error in OpenAI text generation: {e}")
            return ""
#works #brilliant