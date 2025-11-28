FROM python:3.10-slim

# 1. Install system dependencies (ffmpeg, playwright, tesseract)
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates curl unzip \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon0 \
    libgtk-3-0 libgbm1 libasound2 libxcomposite1 libxdamage1 libxrandr2 \
    libxfixes3 libpango-1.0-0 libcairo2 \
    tesseract-ocr \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python tools
RUN pip install --no-cache-dir playwright uv uvicorn

# 3. Install Playwright browsers
RUN playwright install --with-deps chromium

WORKDIR /app

# 4. Copy files
COPY . .

# 5. Install dependencies SYSTEM-WIDE (Bypassing venv to avoid path issues)
RUN uv pip install --system -r pyproject.toml || uv pip install --system .

# 6. CRITICAL: Fix permissions for Hugging Face
RUN mkdir -p LLMFiles && chmod -R 777 LLMFiles

# 7. Expose the port
EXPOSE 7860

# 8. Start directly with Uvicorn (Most stable method)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]