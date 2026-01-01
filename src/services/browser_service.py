import os
import asyncio
from playwright.async_api import async_playwright

class BrowserService:
    @staticmethod
    async def render_html_to_image(html_content: str, output_path: str):
        """
        Renders HTML string to a PNG image using a headless browser.
        """
        # Save HTML to a temporary file so the browser can load it
        temp_html_path = os.path.abspath(output_path.replace(".png", ".html"))
        
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})
            
            # Open the local file
            await page.goto(f"file://{temp_html_path}")
            
            # Wait for animations (if any) to settle
            await page.wait_for_timeout(1000) 
            
            # Take screenshot
            await page.screenshot(path=output_path, full_page=True)
            await browser.close()
            
        # Optional: Clean up HTML file
        # os.remove(temp_html_path)