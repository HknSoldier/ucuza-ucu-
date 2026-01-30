# 1. GitHub'a push et
git init
git add .
git commit -m "🦅 PROJECT TITAN online"
git remote add origin <YOUR_REPO>
git push -u origin main

# 2. Actions'ı etkinleştir (repo → Actions → Enable)

# 3. VEYA yerel test:
pip install -r requirements.txt
playwright install chromium
python main.py
