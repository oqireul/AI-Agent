import subprocess
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# =======================
# Setup
# =======================

load_dotenv()
client = OpenAI()

AUTO_EXECUTE = True
ALLOWED_SHELLS = {"cmd", "powershell"}

print("AI Agent ready (AUTO-EXECUTION ENABLED)")
print("Deletion restricted to Recycle Bin only.\n")


# =======================
# Safety Checks
# =======================

def is_safe_command(command: str) -> bool:
    lowered = command.lower()

    dangerous = [
        "format ",
        "diskpart",
        "del ",
        "rm ",
        "remove-item",
        "shutdown",
        "restart-computer",
        "bcdedit",
        "reg delete"
    ]

    for word in dangerous:
        if word in lowered:
            if "recycle" not in lowered:
                return False

    return True


# =======================
# ChatGPT Planner
# =======================

def ask_ai(user_input: str):
    prompt = (
        f"User asked this: \"{user_input}\".\n"
        "I need to know what to do.\n"
        "Tell me the instructions in a way that Command Prompt or PowerShell commands can do.\n\n"
        "Respond ONLY with valid JSON in this format:\n"
        "{\n"
        "  \"shell\": \"cmd\" or \"powershell\",\n"
        "  \"commands\": [\"command1\", \"command2\"],\n"
        "  \"note\": \"optional explanation\"\n"
        "}\n\n"
        "If no action is required, respond with:\n"
        "{ \"shell\": \"none\" }"
    )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a Windows command planning assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return json.loads(response.choices[0].message.content)


# =======================
# Executor
# =======================

def run_commands(shell: str, commands: list[str]):
    for cmd in commands:
        if not is_safe_command(cmd):
            print(
                "I cannot do that as I am only allowed to delete stuff in the Recycle Bin.\n"
                "If you need to delete something else, I can open File Explorer."
            )
            return

        print(f"\n→ Running ({shell}): {cmd}")

        if shell == "cmd":
            subprocess.run(cmd, shell=True)
        elif shell == "powershell":
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", cmd],
                shell=True
            )


# =======================
# Main Loop
# =======================

def main():
    while True:
        user_input = input("> ").strip()

        if user_input.lower() in {"exit", "quit"}:
            break

        try:
            plan = ask_ai(user_input)

            if plan.get("shell") == "none":
                print("No action required.")
                continue

            shell = plan.get("shell")
            commands = plan.get("commands", [])

            if shell not in ALLOWED_SHELLS:
                print("Blocked: invalid shell.")
                continue

            if not commands:
                print("No executable commands returned.")
                continue

            if AUTO_EXECUTE:
                run_commands(shell, commands)

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
