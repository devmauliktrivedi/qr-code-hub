# QR Code Hub - Streamlit Deployment TODO (Beginner Guide)

## Progress Tracker
- [ ] 1. Local Test
- [ ] 2. GitHub Upload  
- [ ] 3. Streamlit Cloud Deploy
- [ ] 4. Test Live App

---

## 1. Local Test (2 mins - Do this first!)
```
# Open PowerShell/VSCode terminal in qr_code_hub/
pip install -r requirements.txt
streamlit run app.py
```
- App opens in browser
- Login: `kisu` (admin)
- Test QR generator, save, admin panel
- Close when done (Ctrl+C)

**Your .env already has SECRET_KEY/DB - perfect!**

## 2. GitHub (5 mins - NO typing commands)
1. github.com → Sign in → Green \"New repository\"
2. Name: `qr-code-hub` | Public | **Skip README** | Create
3. \"uploading an existing file?\" → Drag entire `qr_code_hub` folder
4. **❌ Uncheck** these 2 files:
   - `.env` (your secrets)
   - `data/qr_code_hub.db` (local data)
5. \"Commit changes\"
6. Copy repo URL (e.g. https://github.com/YourUser/qr-code-hub)

## 3. Streamlit Cloud Deploy (FREE, 3 mins)
1. share.streamlit.io → \"Sign up with GitHub\"
2. \"New app\" → Paste GitHub repo URL → `app.py` → \"Deploy\"
3. Wait 1-2 min → Gets public URL like `https://yourapp.streamlit.app`
4. **Settings → Secrets** (add these from your .env):
```
SECRET_KEY=your_actual_key_from_env
DATABASE_PATH=data/qr_code_hub.db
ADMIN_USERNAMES=kisu
```
5. Redeploy → Live!

## 4. Test Live App
- New data (SQLite resets)
- Login `kisu` → All features work
- Share URL!

## Notes
- **SQLite**: Data resets on restart (demo fine)
- **Later**: GitHub edits → auto-redeploy
- **Help**: Reply if stuck!

**Status: Ready to deploy! Start with local test.**
