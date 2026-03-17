# GIT CHEAT SHEET - Copy Always!

## UPDATE GitHub (Files changed)
```
cd \"c:/Users/Ankur/Desktop/qr_new/qr_code_hub\"
git add .
git commit -m \"your message\"
git push
```

## CHECK STATUS
```
cd \"c:/Users/Ankur/Desktop/qr_new/qr_code_hub\"
git status
```

## NEW Changes Pattern
```
1. git add .           # Add all (gitignore blocks secrets)
2. git status          # Check what's staged  
3. git commit -m \"msg\" # Save snapshot
4. git push           # Upload to GitHub
```

## .gitignore Auto-Protects
```
✅ .env (SECRET_KEY)
✅ data/*.db (database) 
✅ Never uploaded!
```

## Run App
```
cd \"c:/Users/Ankur/Desktop/qr_new/qr_code_hub\"
streamlit run app.py
```

**GitHub**: devmauliktrivedi/qr-code-hub
**Deploy**: share.streamlit.io
