FROM python:3.12-slim

# Install system dependencies for Playwright and networking
RUN apt-get update && apt-get install -y \
    dnsutils \
    curl \
    git \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
RUN pip install --no-cache-dir playwright
RUN playwright install chromium --with-deps

# Copy application files
COPY . /app/autonomous_engines/

# Start background 24/7 daemon loop (runs every 60 minutes)
CMD ["python3", "-u", "-c", "import subprocess, time; \
while True: \
    print('Starting 24/7 autonomous engine cycle...'); \
    subprocess.run(['python3', '/app/autonomous_engines/master_orchestrator.py']); \
    print('Cycle complete. Sleeping for 3600 seconds...'); \
    time.sleep(3600)"]
