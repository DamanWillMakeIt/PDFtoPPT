# Use the official Playwright image
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# 1. Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Install ONLY Chromium
RUN playwright install chromium

# 3. Copy Application Code
COPY . .

# --- FIX FOR ERROR 128 ---
# Remove the .git folder so libraries don't try to run 'git status' and crash
RUN rm -rf .git

# 4. Create Temp Directory
RUN mkdir -p temp

# 5. Start the Server using 'python -m' to avoid PATH issues
# This is safer than just running 'uvicorn'
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
