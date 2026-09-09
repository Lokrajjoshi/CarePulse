# GitHub and Future Changes

CarePulse is ready to version in Git. GitHub can store its history and source code; it does not automatically make the FastAPI server public.

## First push from PowerShell

Run these commands from the project root after creating an empty repository on GitHub:

```powershell
cd "C:\Users\Namraj Joshi\Desktop\CarePulse"
git init
git add .
git commit -m "Initial CarePulse project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the repository URL with your own. Do not commit `.env`, `.venv`, `carepulse_demo.db`, exports containing sensitive data, passwords, or real conversations. The included `.gitignore` protects common local files.

## Later modifications

```powershell
git checkout -b feature/my-change
git add .
git commit -m "Describe the change"
git push -u origin feature/my-change
```

Review the branch on GitHub, then merge it into `main`. The local SQLite database can be regenerated with `python scripts\reset_demo.py`; code and documentation changes remain versioned independently.

## Deployment distinction

GitHub stores the project. A public deployment still needs an approved hosting service, environment variables, database strategy, and security review. Because this project has a mandatory zero-cost constraint, no paid cloud resource or billing activation is included.
