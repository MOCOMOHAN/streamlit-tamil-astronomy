# 🚀 விண்வெளி தமிழ் — Space Tamil App

A full Tamil-language space exploration app built with Streamlit.

## Features
- 🏠 **முகப்பு (Home)** — Welcome, space description, app goals, shortcut cards
- 🛰️ **ISS கண்காணிப்பு (ISS Locator)** — Simulated ISS position on world map with crew details
- 🖼️ **தொகுப்பகம் (Gallery)** — NASA APOD images with Tamil captions
- 📰 **விண்வெளி செய்திகள் (Space News)** — News grids for asteroids, stars, Mars, Moon
- 👩‍🚀 **விண்வெளி உதவியாளர் (Astronaut Assistant)** — Tamil AI chatbot powered by OpenAI

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Create `.streamlit/secrets.toml`:
```toml
NASA_API_KEY = "your_key_from_api.nasa.gov"
OPENAI_API_KEY = "your_openai_key"
```

Get free NASA API key: https://api.nasa.gov/

### 3. Add Robot Image (for Astronaut Assistant)
Place your robot image as `robot.png` in the app folder.
Update path in app.py: `robot_img_path = "robot.png"`

### 4. Run locally
```bash
streamlit run app.py
```

## Deployment Options

### Option A: Streamlit Community Cloud (Free, easiest)
1. Push to GitHub
2. Go to https://share.streamlit.io
3. Connect your repo → Deploy
4. Add secrets in the dashboard
5. Get a free `.streamlit.app` subdomain

### Option B: Custom Domain on VPS (e.g., DigitalOcean, AWS EC2)
```bash
# On your server:
pip install -r requirements.txt
streamlit run app.py --server.port 8501

# Use Nginx as reverse proxy:
# nginx config snippet:
# server {
#     server_name yourdomain.com;
#     location / {
#         proxy_pass http://localhost:8501;
#         proxy_http_version 1.1;
#         proxy_set_header Upgrade $http_upgrade;
#         proxy_set_header Connection "upgrade";
#     }
# }
# certbot --nginx -d yourdomain.com  (for HTTPS)
```

### Option C: Railway / Render (Simple PaaS)
- Push to GitHub, connect to Railway or Render
- Set environment variables for API keys
- Use `streamlit run app.py` as start command

## Dark/Light Mode
Click the 🌙/☀️ button in the top-right corner to toggle themes.

## Tamil Fonts
The app uses Google Fonts `Noto Sans Tamil` — works in all modern browsers.
