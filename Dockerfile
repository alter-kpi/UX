# ============================================================
# 1) Base image Python slim
# ============================================================
FROM python:3.10-slim

# ============================================================
# 2) Install system dependencies & Google Chrome
# ============================================================
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    fonts-liberation \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libappindicator3-1 \
    libxrandr2 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# === Add Google Chrome repository ===
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# ============================================================
# 3) Install Python dependencies
# ============================================================
WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ============================================================
# 4) Copy project code
# ============================================================
COPY . .

# ============================================================
# 5) Expose port & start Gunicorn
# ============================================================
EXPOSE 10000

# Commande Render par défaut (Dash = app.server)
CMD ["gunicorn", "app:server", "-b", "0.0.0.0:10000", "--timeout", "120"]
