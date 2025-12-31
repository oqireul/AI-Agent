import os
import sys
import json
import subprocess
import webbrowser
import shutil
from dotenv import load_dotenv
from openai import OpenAI

# =========================
# Startup / Metadata
# =========================

SCRIPT_NAME = os.path.basename(__file__)
VERSION = SCRIPT_NAME.replace("agent_ver", "").replace(".py", "")

GITHUB_URL = "https://github.com/oqireul/AI-Agent"

print("Made by BrennanW1, aka oqireul on GitHub.")
print(f"See {GITHUB_URL} for other versions.\n")
print("AI Agent ready (AUTO-EXECUTION ENABLED)")
print(f"Running version v{VERSION}\n")

# =========================
# OpenAI Setup
# =========================

load_dotenv()
client = OpenAI()

# =========================
# App Aliases
# =========================

APP_ALIASES = {
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "file explorer": "explorer",
    "explorer": "explorer",

    # CMD
    "cmd": "cmd",
    "cmd.exe": "cmd",
    "command prompt": "cmd",
    "command line": "cmd",

    # PowerShell
    "powershell": "powershell",
    "powershell.exe": "powershell",
    "pwsh": "pwsh",
    "pwsh.exe": "pwsh",
    "power shell": "powershell",
    "windows powershell": "powershell",
    "ps": "powershell",
}

# =========================
# Helpers
# =========================

def open_app(app_name: str):
    app_name = app_name.lower().strip()

    if app_name in APP_ALIASES:
        target = APP_ALIASES[app_name]
        subprocess.Popen(target, shell=True)
        return

    # If not an app, assume it's a website/search
    webbrowser.open(f"https://www.google.com/search?q={app_name}")

def safe_delete(path: str):
    if "recycle" not in path.lower():
        print(
            "I cannot do that as I am only allowed to delete stuff in the Recycle Bin.\n"
            "If you need to delete something else, I can open File Explorer."
        )
        return

    try:
        subprocess.Popen(
            ["powershell", "-command", "Clear-RecycleBin -Force"],
            shell=True
        )
    except Exception as e:
        print("Deletion failed:", e)

# =========================
# AI Interface
# =========================

def ask_ai(user_input: str):
    prompt = (
        f"User asked this: '{user_input}'. "
        "Tell me what to do using simple JSON instructions. "
        "Allowed actions:\n"
        "- open_app (requires app)\n"
        "- delete (requires path)\n\n"
        "Respond ONLY with valid JSON.\n"
        "Example:\n"
        "[{\"action\": \"open_app\", \"app\": \"notepad\"}]"
    )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.choices[0].message.content)

# =========================
# Action Executor
# =========================

def execute(action: dict):
    action_type = action.get("action")

    if action_type == "open_app":
        app = action.get("app")
        if not app:
            print("No app specified.")
            return
        open_app(app)

    elif action_type == "delete":
        path = action.get("path")
        if not path:
            print("No path specified.")
            return
        safe_delete(path)

    else:
        print("Blocked or unknown action:", action_type)

# =========================
# Main Loop
# =========================

def main():
    while True:
        try:
            user_input = input("> ").strip()

            if user_input.lower() in {"exit", "quit"}:
                break

            # Built-in GitHub command (local handling)
            if user_input.lower() == "github":
                print("Opening GitHub repository...")
                webbrowser.open(GITHUB_URL)
                continue

            actions = ask_ai(user_input)

            if not actions:
                print("No action required.")
                continue

            if isinstance(actions, dict):
                actions = [actions]

            print("Executing actions...")
            for act in actions:
                execute(act)

        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
