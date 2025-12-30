import json
import subprocess
import pyautogui
import os
from openai import OpenAI
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv(dotenv_path=".env", override=True)

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found. Check your .env file.")

client = OpenAI(api_key=API_KEY)

# -----------------------------
# Safety configuration
# -----------------------------
pyautogui.FAILSAFE = True

ALLOWED_ACTIONS = {
    "open_app",
    "type_text",
    "press_key",
    "sleep"
}

# -----------------------------
# Action executor
# -----------------------------
def execute(action: dict):
    name = action.get("action")

    if name not in ALLOWED_ACTIONS:
        print("Blocked action:", name)
        return

    if name == "open_app":
        subprocess.Popen(action["app"], shell=True)

    elif name == "type_text":
        pyautogui.write(action["text"], interval=0.03)

    elif name == "press_key":
        key = action["key"]
        if "+" in key:
            pyautogui.hotkey(*key.split("+"))
        else:
            pyautogui.press(key)

    elif name == "sleep":
        seconds = action.get("seconds") or action.get("duration")
        if seconds is None:
            print("Sleep action missing duration")
            return

        # Support ms or seconds
        if seconds > 10:
            seconds = seconds / 1000

        pyautogui.sleep(seconds)

# -----------------------------
# AI request
# -----------------------------
def ask_ai(command: str):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Windows automation agent.\n"
                    "Respond ONLY with valid JSON.\n"
                    "ALWAYS return a JSON ARRAY of actions.\n"
                    "Each action must contain an 'action' field.\n"
                    "Allowed actions: open_app, type_text, press_key, sleep.\n"
                    "For open_app use key 'app'.\n"
                    "For sleep use key 'seconds'.\n"
                    "For press_key use key 'key'.\n"
                    "Key combos must use '+' (example: ctrl+shift+enter).\n"
                    "Never delete files, modify system settings, or access the registry."
                )
            },
            {"role": "user", "content": command}
        ]
    )

    data = json.loads(response.choices[0].message.content)

    # Normalize single action → list
    if isinstance(data, dict):
        data = [data]

    return data

# -----------------------------
# Main loop
# -----------------------------
print("AI Agent ready. Type a command or 'exit'.")

while True:
    user_cmd = input("> ")

    if user_cmd.lower() == "exit":
        break

    try:
        actions = ask_ai(user_cmd)
        print("Proposed actions:", actions)

        confirm = input("Run these actions? (y/n): ").lower()
        if confirm == "y":
            for act in actions:
                execute(act)

    except Exception as e:
        print("Error:", e)
