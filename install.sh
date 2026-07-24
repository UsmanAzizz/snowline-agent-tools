#!/bin/bash

echo "[INIT] Installing 12-Pillars Agent Ecosystem (Project-Level)..."

PROJECT_ROOT=$(pwd)
AGENTS_DIR="$PROJECT_ROOT/.agents"
SKILLS_DIR="$AGENTS_DIR/skills"
KNOWLEDGE_DIR="$AGENTS_DIR/knowledge"
REPO_URL="https://github.com/UsmanAzizz/snowline-agent-tools.git"

# Ensure .agents and .agents/knowledge exist
mkdir -p "$AGENTS_DIR"
mkdir -p "$KNOWLEDGE_DIR"

# Scaffold skills
if [ -d "$SKILLS_DIR" ]; then
    echo "[INFO] Found existing skills directory at $SKILLS_DIR"
    if [ -d "$SKILLS_DIR/.git" ]; then
        echo "[UPDATE] Pulling latest updates..."
        (cd "$SKILLS_DIR" && git pull origin main) || echo "[ERROR] Failed to update repository."
    else
        echo "[WARN] Existing skills directory is not a git repository. Skipping git pull."
    fi
else
    echo "[DOWNLOAD] Downloading 12-Pillars skills..."
    if ! git clone "$REPO_URL" "$SKILLS_DIR"; then
        echo "[ERROR] Failed to clone repository. Make sure git is installed."
        exit 1
    fi
fi

# Copy AGENTS_TEMPLATE.md to AGENTS.md
TEMPLATE_PATH="$SKILLS_DIR/AGENTS_TEMPLATE.md"
LOCAL_AGENTS_PATH="$AGENTS_DIR/AGENTS.md"

if [ -f "$TEMPLATE_PATH" ]; then
    if [ ! -f "$LOCAL_AGENTS_PATH" ]; then
        echo "[CREATE] Creating Project AGENTS.md..."
        cp "$TEMPLATE_PATH" "$LOCAL_AGENTS_PATH"
        echo "[SUCCESS] Project AGENTS.md created successfully."
    else
        echo "[INFO] Project AGENTS.md already exists. Skipping overwrite."
    fi
fi

# Scaffold PLAN.md
PLAN_PATH="$PROJECT_ROOT/PLAN.md"
if [ ! -f "$PLAN_PATH" ]; then
    echo "[CREATE] Creating PLAN.md..."
    echo -e "# Project Plan / Task Tracker\n\n- [ ] Initial task" > "$PLAN_PATH"
fi

echo -e "\n[DONE] Installation Complete!"
echo "This project is now powered by the 12-Pillars Ecosystem."
