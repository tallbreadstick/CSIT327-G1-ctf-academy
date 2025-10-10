# CTF Academy — Development setup (Windows, cmd.exe)

This README explains exactly what a first-time contributor should do after pulling the repository on a Windows machine. It follows the workflow your lead developer expects and adds the missing Tailwind/npm step so CSS will build correctly.

Follow these steps in order (copy-paste into a cmd.exe prompt)

## 1) Run the project's update script (creates venv + installs Python deps)

From the repository root (the directory that contains `run.bat` and `update.bat`), run:

```cmd
cd /d C:\Users\user\Documents\3RD_YEAR_BSIT\IT317\PROJECTS\CTF-ACADEMY\scrum-ctf-academy
update.bat
```

What this does
- Creates (or re-uses) the Python virtual environment `.venv` and activates it
- Installs Python packages listed in `requirements.txt`

If `update.bat` is missing any of these steps, run them manually (see "Manual steps" below).

## 2) Add a `.env` file (ask the maintainer for the SECRET_KEY)

The project reads configuration from a repo-level `.env` (located in the repository root, next to `run.bat`). Ask the project author or lead for the value of `SECRET_KEY`. Create the `.env` file (do not commit it).

Example `.env` contents (replace values):

```
# Django settings
SECRET_KEY=django-insecure-<paste-secret-key-from-author-here>
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Postgres (if using the supplied DB) — replace these if you run your own DB
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
DB_NAME=yourdbname
```

Security note: Never add `.env` to version control. Keep secrets private.

If you don't have Postgres and want to run quickly, ask in the repo if a sqlite fallback is allowed or request guidance from the author.

## 3) Build the Tailwind CSS (npm)

This project uses Tailwind (via `theme/static_src`). Your lead's `update.bat` may not include npm steps; run them now.

Open a new cmd.exe terminal (not PowerShell, or run from cmd within PowerShell using `cmd /c ...`) and run:

```cmd
cd ctf_academy\theme\static_src
npm install
npm run build
```

Notes:
- `npm run build` generates the compiled CSS at `ctf_academy\theme\static\css\dist\styles.css` which Django serves as static files.
- For active development (auto-rebuild when you edit templates/CSS), use:

```cmd
npm run dev
```

Keep `npm run dev` running in its own terminal while you work so styles update automatically.

If you get PowerShell execution policy errors when running `npm` in PowerShell, run the npm commands from cmd.exe or prefix with `cmd /c`.

## 4) Run migrations and start the development server

From the repository root, with the virtual environment active (if `update.bat` didn't already activate it):

```cmd
call .venv\Scripts\activate.bat
python ctf_academy\manage.py migrate
python ctf_academy\manage.py createsuperuser

REM then start the server
cd /d C:\Users\user\Documents\3RD_YEAR_BSIT\IT317\PROJECTS\CTF-ACADEMY\scrum-ctf-academy
.\run.bat
```

`run.bat` will activate the venv (if needed) and call `manage.py runserver`. The dev server listens on `http://127.0.0.1:8000/` by default.

## Manual steps (if `update.bat` didn't do everything)

- Create venv and activate:

```cmd
python -m venv .venv
call .venv\Scripts\activate.bat
```

- Install Python deps:

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

## Troubleshooting (common problems)

- CSS still 404 after `npm run build`:
  - Confirm `ctf_academy\theme\static\css\dist\styles.css` exists.
  - If you're using `npm run dev`, wait for the first build to finish then refresh the browser (hard refresh).

- `Set the SECRET_KEY environment variable` error when starting Django:
  - Make sure `.env` is in the repository root (next to `run.bat`) and contains `SECRET_KEY=...`.

- `npm` blocked in PowerShell due to execution policy:
  - Run npm commands from cmd.exe or use `cmd /c "npm install"` to run from PowerShell.

- Database connection errors on migrate:
  - Confirm DB_* values in `.env` are correct for your Postgres instance, or ask the author for DB access.
  - If you don't have Postgres locally, request the author to allow a sqlite fallback or provide a dev database.

## Optional improvements (ask for permission before applying)

- Add npm install & build to `update.bat` so new contributors get Node deps and built CSS automatically. Suggested snippet:

```bat
REM Install theme npm deps and build tailwind CSS (cmd.exe)
if exist "ctf_academy\theme\static_src\package.json" (
    echo Installing theme npm dependencies and building CSS...
    pushd ctf_academy\theme\static_src
    cmd /c "npm install"
    cmd /c "npm run build"
    popd
)
```

- Add a small `DEVELOPMENT.md` with these commands (I can add it for you).

## Quick checklist before opening a PR

- [ ] `.env` added locally and not committed
- [ ] `npm run build` or `npm run dev` completed and `styles.css` exists
- [ ] `python manage.py migrate` ran successfully
- [ ] Dev server runs and home page loads with Tailwind styling

---

# CTF Academy - Description

A web platform for education in higher-level abstractions of cybersecurity and pentesting tools, techniques, and methodologies.

## About

CTF Academy is a web-based platform designed to train users by giving them experience dealing with abstract cybersecurity and pentesting concepts. The platform takes a leetcode-style approach, providing an open problem set with various capture-the-flag style challenges. Each challenge introduces different key cybersecurity concepts from the basics to intermediate, including endpoints, exposed surfaces, privileges, and encryption.

Each challenge contains a graph of nodes which represents a network of host machines, mimicing real world network topologies and security layers. Users must use a set of given tools to inspect, analyze, and understand system architectures with the objective of finding exploits that lead them to capturing the flag. Tools provided to users will include terminals, scripts, and webviews.

Challenges range from various difficulties including easy, medium, and hard problems. Higher difficulty challenges completed award higher points to a user's general ranking on the leaderboards. Users' challenge histories, attempts, and submissions are also recorded. CTF Academy also fosters continuous support through streaks, encouraging users to maintain daily challenge streaks to gain score bonuses.

## Backend Internals

This section dictates specifications for backend internals with respect to different individual features.

### Challenges

Each challenge's data, details, and specifications are stored as static resources in the application's backend. When a user attempts a challenge, a docker container is created according to the challenge's specifications. This wills serve as the sandbox or the challenge play area. All interactions with terminal tools, scripts, and webviews as well as mutable interactions with nodes occur within the user's open docker container for the challenge. Challenge state is stored on the cloud in the application's backend database. Returning to a challenge in progress restores the saved state of the challenge.

### Ranking and Streaks

As users complete challenges, points are awarded to their accounts. Every consecutive day in which a challenge is solved awards a growing score multiplier. Breaking a steak resets the score multiplier. Scores and streaks are also stored persistently in the application's backend database.

### Terminal

When solving challenges, users are provided with a terminal or command interface with a fixed set of built-in commands. (Commands TBA)

### Scripts

When solving challenges, users are provided with code editors to write scripts for automated tasks. The default scripting language provided is python, with the possibility of javascript being added in the future.

### WebView

When solving challenges, users are also provided with a web browser which they can use to access sites within the challenge using a GUI. This could use an `<iframe>` tag in the frontend, with most sites being restricted by default. Each challenge specification will also come with a list of `allowed_sites` as a whitelist.

# CTF Academy - Collaborators

| Member | Role | Email |
| - | - | - |
| [Jeremiah Ramos](https://github.com/tallbreadstick) | Lead Developer | jeremiah.ramos@cit.edu |
| [Kean Maverick Saligue](https://github.com/MystoganF) | Developer | keanmaverick.saligue@cit.edu |
| [Christian Andrey Reyes](https://github.com/nahuyadada) | Developer | christianandrey.reyes@cit.edu |

Scrum Master: [Kervin Gino Sarsonas](https://github.com/Desiigner101)

# CTF Academy - Tech Stack

### Backend

![Tech Stack](https://go-skill-icons.vercel.app/api/icons?i=python,django)

### Frontend

![Tech Stack](https://go-skill-icons.vercel.app/api/icons?i=html,css,js,tailwind)

### Database

![Tech Stack](https://go-skill-icons.vercel.app/api/icons?i=postgres,supabase)