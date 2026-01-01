import os
from playwright.async_api import async_playwright

class BrowserService:
    @staticmethod
    async def render_html_to_image(html_content: str, output_path: str):
        """
        Renders HTML string to a PNG image using Playwright.
        """
        # 1. Prepare Paths
        abs_output_path = os.path.abspath(output_path)
        temp_html_path = abs_output_path.replace(".png", ".html")
        
        # 2. Save HTML to disk
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        async with async_playwright() as p:
            # 3. Launch Browser with CRITICAL Docker flags
            browser = await p.chromium.launch(
                args=[
                    "--no-sandbox", 
                    "--disable-setuid-sandbox", 
                    "--disable-dev-shm-usage" # Prevents memory crash on Render
                ]
            )
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})
            
            # 4. Open File
            await page.goto(f"file://{temp_html_path}")
            
            # 5. Take Screenshot
            await page.screenshot(path=abs_output_path, full_page=True)
            await browser.close()
            
        # Cleanup
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)