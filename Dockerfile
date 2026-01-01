# We MUST use the official Playwright image to get all the Linux dependencies
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# 1. Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Install ONLY Chromium (Saves space vs installing all browsers)
RUN playwright install chromium

# 3. Copy Application Code
COPY . .

# 4. Create Temp Directory
RUN mkdir -p temp

# 5. Start the Server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]