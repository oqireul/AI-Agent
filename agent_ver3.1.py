import os
import sys
import json
import subprocess
import webbrowser
from dotenv import load_dotenv
from openai import OpenAI

# =========================
# METADATA
# =========================

VERSION = "v3.1"
GITHUB_URL = "https://github.com/oqireul/AI-Agent"

# =========================
# INIT
# =========================

load_dotenv()
client = OpenAI()

print("Made by BrennanW1, aka oqireul on GitHub.")
print(f"See {GITHUB_URL} for other versions.\n")
print("AI Agent ready (AUTO-EXECUTION ENABLED)")
print(f"Running version {VERSION}\n")

# =========================
# BUILT-IN COMMANDS
# =========================

def cmd_help():
    print("\nBuilt-in commands:")
    print("  help     - Show this message")
    print("  github   - Open AI Agent GitHub repo")
    print("  cls      - Clear the screen")
    print("  exit     - Exit the agent\n")

def cmd_github():
    print("Opening GitHub repository...")
    webbrowser.open(GITHUB_URL)

def cmd_exit():
    print("Goodbye 👋")
    sys.exit(0)

def cmd_cls():
    os.system("cls" if os.name == "nt" else "clear")

BUILT_INS = {
    "help": cmd_help,
    "github": cmd_github,
    "exit": cmd_exit,
    "cls": cmd_cls,
}

ALIASES = {
    "github": ["github", "open github", "repo"],
    "exit": ["exit", "quit", "bye", "close agent"],
    "cls": ["cls", "clear", "clear screen"],
    "help": ["help", "commands", "what can you do"]
}

# =========================
# INTENT DETECTION
# =========================

SEARCH_TRIGGERS = [
    "google",
    "search",
    "search up",
    "look up",
    "find online"
]

LOCAL_VERBS = [
    "open", "run", "start", "close", "delete", "empty", "check", "show"
]

def normalize(text):
    return text.lower().strip()

def match_builtin(user_input):
    text = normalize(user_input)

    if text in BUILT_INS:
        return BUILT_INS[text]

    for cmd, aliases in ALIASES.items():
        if text in aliases:
            return BUILT_INS[cmd]

    return None

def extract_search_query(user_input):
    text = normalize(user_input)

    for trigger in SEARCH_TRIGGERS:
        if text.startswith(trigger):
            query = text[len(trigger):].strip()
            return query

    return None

def is_local_intent(user_input):
    text = normalize(user_input)
    return any(v in text for v in LOCAL_VERBS)

# =========================
# AI LOCAL HANDLER
# =========================

SYSTEM_PROMPT = (
    "You are a Windows automation assistant.\n"
    "RULES:\n"
    "- ONLY return valid JSON\n"
    "- ONLY suggest local actions\n"
    "- NEVER suggest web browsing\n"
    "- If nothing applies, return:\n"
    "  {\"action\": \"NO_ACTION\"}\n\n"
    "Allowed actions:\n"
    "- open_app (name)\n"
    "- run_cmd (command)\n"
)

def ask_ai_local(user_input):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
    )
    return json.loads(response.choices[0].message.content)

def execute_action(action):
    if action.get("action") == "NO_ACTION":
        print("No local action available.")
        return

    if action["action"] == "open_app":
        app = action.get("name")
        if not app:
            print("No app specified.")
            return
        subprocess.Popen(app, shell=True)

    elif action["action"] == "run_cmd":
        cmd = action.get("command")
        if not cmd:
            print("No command specified.")
            return
        subprocess.Popen(cmd, shell=True)

    else:
        print("Blocked or unknown action:", action.get("action"))

# =========================
# MAIN LOOP
# =========================

while True:
    user_input = input("> ").strip()

    if not user_input:
        continue

    # 1️⃣ BUILT-IN COMMANDS
    builtin = match_builtin(user_input)
    if builtin:
        builtin()
        continue

    # 2️⃣ SEARCH (cleaned query)
    query = extract_search_query(user_input)
    if query is not None:
        if query:
            print(f"Searching for: {query}")
            webbrowser.open(
                "https://www.google.com/search?q=" +
                query.replace(" ", "+")
            )
        else:
            print("Opening Google...")
            webbrowser.open("https://www.google.com")
        continue

    # 3️⃣ LOCAL AI ACTION
    if is_local_intent(user_input):
        try:
            action = ask_ai_local(user_input)
            execute_action(action)
        except Exception as e:
            print("Error:", e)
        continue

    # 4️⃣ FALLBACK
    print("I’m not sure what you want to do.")
    print("Type 'help' to see available commands.")
