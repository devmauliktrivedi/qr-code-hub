# QR Code Hub 🔗



**QR Code Hub** is a full-featured QR code generator built with Streamlit. Create, customize, save QR codes with user accounts, admin panel, and feedback system.

## ✨ Features

- **QR Generation**: Custom colors, sizes, styles
- **User Accounts**: Login, save your QR history
- **Admin Dashboard**: Manage users, QRs, comments
- **Feedback System**: User suggestions
- **Responsive Design**: Works on all devices
- **SQLite Database**: Easy deployment
- **Secure**: Password hashing, sessions

## 🎯 Use Cases

- Personal QR codes (contact, WiFi, payments)
- Business cards, events, marketing
- Educational tools
- Portfolio demo projects

## 🚀 Quick Start

```bash
git clone https://github.com/devmauliktrivedi/qr-code-hub.git
cd qr-code-hub
pip install -r requirements.txt
streamlit run app.py
```

**Setup `.env`** from `.env.example`.

## ☁️ Deploy (Streamlit Cloud)

1. Fork this repo
2. share.streamlit.io → New app → your-fork/app.py
3. Add `.env` secrets
4. Live in 2 minutes!

## 🏗️ Architecture

```
app.py (Streamlit)
├── qr_app/
│   ├── config.py (.env)
│   ├── db.py (SQLite)
│   ├── services/ (business logic)
│   └── ui/ (pages, styles)
├── sql/ (schema)
├── avatars/ (UI assets)
└── data/ (.db - gitignore)
```

## 📊 Tech Stack

| Frontend | Backend | Database | Tools |
|----------|---------|----------|-------|
| Streamlit | Python | SQLite | Git |

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Test locally (`streamlit run app.py`)
4. Submit PR



## 🙏 Acknowledgments

Built with [Streamlit](https://streamlit.io), [qrcode](https://pypi.org/project/qrcode/), [SQLite](https://sqlite.org).

---

⭐ Star this repo if useful!

