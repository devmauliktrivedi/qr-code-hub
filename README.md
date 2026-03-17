# QR Code Hub

A polished Streamlit QR app with accounts, saved QR history, feedback, and an in-app admin panel.

## Public-facing names

These names are cleaner for GitHub and deployment:

- Suggested GitHub repo name: `qr-code-hub`
- Database file: `data/qr_code_hub.db`
- Secret-key helper: `generate_secret_key.py`
- Legacy reference file: `legacy/legacy_mysql_reference.py`

I kept the outer local folder name as `new_avtar_qr` because Windows was locking that folder while it was open in the editor. That does not matter for GitHub. Your GitHub repo can still be named `qr-code-hub`.

## Project structure

```text
project-root/
|-- app.py
|-- avatars/
|-- data/
|   |-- qr_code_hub.db
|-- legacy/
|   |-- legacy_mysql_reference.py
|-- qr_app/
|   |-- config.py
|   |-- constants.py
|   |-- db.py
|   |-- security.py
|   |-- state.py
|   |-- utils.py
|   |-- services/
|   |-- ui/
|-- sql/
|   |-- 001_schema.sql
|   |-- 002_indexes.sql
|-- .env.example
|-- .gitignore
|-- generate_secret_key.py
|-- requirements.txt
|-- setup.sql
```

## Is SQLite okay for sharing with friends?

Yes. For this project, SQLite is a good choice if:

- you are sharing the app with a small group
- traffic is light
- most usage is casual
- you are running a single deployed app instance

For your current use case, it is absolutely fine.

### What SQLite is good at

- learning projects
- portfolio projects
- demos
- small private tools
- apps shared with friends or a small class/team

### What SQLite is not good at

- many users writing at the exact same time
- large public traffic spikes
- multiple server instances writing to one shared database
- apps that need heavy admin/reporting usage all day

### Rough expectation

There is no perfect fixed number, but for a project like this:

- a small group of friends is fine
- light usage from a few to a few dozen people is usually fine
- if many people start creating accounts, feedback, and QR records at the same exact time, SQLite can become a bottleneck because writes lock the database

If this app later grows beyond casual use, move to PostgreSQL.

## Quick start

1. Open a terminal inside the project folder.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Generate a secret key:

```bash
python generate_secret_key.py
```

4. Put that value into `.env` as `SECRET_KEY=...`
5. Run the app:

```bash
python -m streamlit run app.py
```

## Admin access

- The admin panel is locked to username `kisu`
- Log in as `kisu`
- Open `Admin` from the sidebar

## Files you should care about most

- `app.py`: app entry point
- `qr_app/ui/pages.py`: main page layouts
- `qr_app/ui/styles.py`: global styling
- `qr_app/ui/admin.py`: admin panel
- `qr_app/services/`: app logic and database queries
- `qr_app/db.py`: database connection setup
- `sql/001_schema.sql`: database schema
- `.env`: local configuration

## If you want to change the database later

Right now the app uses SQLite. Later, if you want PostgreSQL or another database, the main places to change are:

1. `qr_app/db.py`
2. `sql/001_schema.sql`
3. SQL queries inside:
   - `qr_app/services/auth.py`
   - `qr_app/services/comments.py`
   - `qr_app/services/qr_codes.py`
   - `qr_app/services/admin.py`

### Easy mental model

- `db.py` decides how the app connects
- `sql/` defines the tables
- `services/` contains the queries
- `ui/` should mostly stay the same

That means later database migration is very possible without rebuilding the whole app.

## How to edit the app later

If you want to fix something, add a feature, or change design after deployment:

1. Open the project locally
2. Edit the file you want
3. Test locally with:

```bash
python -m streamlit run app.py
```

4. When it looks good, commit your changes
5. Push to GitHub
6. Your deployment platform can redeploy from GitHub

## GitHub steps

1. Create a new GitHub repository
2. Recommended repo name: `qr-code-hub`
3. Keep the repo public or private, your choice
4. Upload the project files
5. Do not upload:
   - `.env`
   - `data/qr_code_hub.db`
   - `__pycache__/`

### If you are using Git from terminal

Run these commands inside the project folder:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

## Deployment steps

You can deploy from GitHub on a Streamlit-friendly host.

General flow:

1. Push the code to GitHub
2. Connect the GitHub repo to your deployment platform
3. Set the app entry file to `app.py`
4. Add environment variables:
   - `SECRET_KEY`
   - `DATABASE_PATH=data/qr_code_hub.db`
   - `ADMIN_USERNAMES=kisu`
5. Deploy
6. Open the public URL and test login, QR creation, saved history, feedback, and admin access

## Important deployment note for SQLite

SQLite works best when the deployed app keeps a persistent disk.

If your host resets the filesystem often or creates a fresh container every restart, the database file may be lost unless that platform gives you persistent storage.

So before sharing the link, confirm:

- your host keeps files between restarts
- the app is running as a single instance

If not, move later to PostgreSQL.

## Manual rename note

If you want the outer local folder name to look nicer too, close the project in VS Code first, then rename:

```text
new_avtar_qr -> qr_code_hub
```

That outer folder name does not affect the app code itself.
