# Start the engine calculator from Windows (PowerShell, in the repo root): .\scripts\talysworld\start.ps1
# then open http://localhost:8765/ . The service runs in laptop WSL (production engine 16606b356d6e, at most 3 jobs at nice 10).
# Equivalent one-liner: wsl -e python3 scripts/talysworld/server.py
wsl -e python3 scripts/talysworld/server.py @args
