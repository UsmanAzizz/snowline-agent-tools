"""
core_memory.py - User profile, task_lock CRUD, and decision history.
"""
import os
import json
from datetime import datetime
from typing import Dict

# ============================================================
# USER PROFILE (persistent, from memory.json)
# ============================================================

_MEMORY_CACHE: Dict[str, int] = {}  # path -> user_level, cached per session


def load_user_level() -> int:
    """Load user_level from .agents/memory.json.

    Returns default 3 if file or field not found (no error).
    Cached per session to avoid repeated disk reads.
    """
    memory_path = '.agents/memory.json'
    if not os.path.isfile(memory_path):
        return 3

    # Check session cache
    cached = _MEMORY_CACHE.get(memory_path)
    if cached is not None:
        return cached

    try:
        with open(memory_path, encoding='utf-8') as f:
            data = json.load(f)
        level = data.get('user_level', 3)
        if not isinstance(level, int) or level < 1 or level > 10:
            level = 3
        _MEMORY_CACHE[memory_path] = level
        return level
    except (json.JSONDecodeError, IOError, KeyError):
        _MEMORY_CACHE[memory_path] = 3
        return 3


# ============================================================
# TASK LOCK
# ============================================================

TASK_LOCK_FILE = '.agents/task_lock.json'


def load_task_lock():
    """Load task_lock.json from current directory."""
    if not os.path.exists(TASK_LOCK_FILE):
        return None
    try:
        with open(TASK_LOCK_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_task_lock(data):
    """Save task_lock.json to current directory."""
    os.makedirs('.agents', exist_ok=True)
    with open(TASK_LOCK_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return True


def start_task_lock(task_id: str, user_intent: str):
    """Start a new task lock."""
    data = {
        "task_id": task_id,
        "user_intent_raw": user_intent,
        "prompt_classification": None,
        "classification_reasoning": "",
        "response_mode": None,
        "response_mode_reasoning": "",
        "clarified_understanding": "",
        "level_target": load_user_level(),
        "grilling_log": [],
        "plan_summary": "",
        "status": "clarifying",
        "created_at": str(datetime.now())
    }
    save_task_lock(data)
    return data


def add_grilling_qa(question: str, answer: str):
    """Add a Q&A pair to the grilling log."""
    data = load_task_lock()
    if not data:
        return None
    data['grilling_log'].append({
        "question": question,
        "answer": answer,
        "timestamp": str(datetime.now())
    })
    save_task_lock(data)
    return data


def update_task_lock(**kwargs):
    """Update task_lock fields."""
    data = load_task_lock()
    if not data:
        return None
    for key, value in kwargs.items():
        if key in data:
            data[key] = value
    save_task_lock(data)
    return data


def get_task_status():
    """Get current task status."""
    data = load_task_lock()
    if not data:
        return {"status": "no_active_task"}
    return data


# ============================================================
# DECISION HISTORY
# ============================================================

DECISION_HISTORY_FILE = '.agents/decision_history.json'
MAX_HISTORY_ENTRIES = 20


def load_decision_history() -> list:
    """Load decision_history.json.

    Returns empty list if file not found (no error).
    This function is for MANUAL reference by the agent only -
    do NOT use it to auto-skip grilling or auto-decide response_mode.
    """
    if not os.path.isfile(DECISION_HISTORY_FILE):
        return []
    try:
        with open(DECISION_HISTORY_FILE, encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_decision_history(history: list):
    """Save decision history, trimmed to MAX_HISTORY_ENTRIES."""
    os.makedirs('.agents', exist_ok=True)
    trimmed = history[-MAX_HISTORY_ENTRIES:]
    with open(DECISION_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(trimmed, f, indent=2, ensure_ascii=False)


def _append_to_history(task_data: dict):
    """Append task summary to decision_history.json before deleting task_lock."""
    history = load_decision_history()
    raw = task_data.get('user_intent_raw', '')
    words = raw.split()
    intent_summary = ' '.join(words[:5])
    if len(words) > 5:
        intent_summary += '...'

    entry = {
        "task_id": task_data.get('task_id', ''),
        "prompt_classification": task_data.get('prompt_classification'),
        "response_mode": task_data.get('response_mode'),
        "intent_summary": intent_summary,
        "completed_at": str(datetime.now())
    }
    history.append(entry)
    save_decision_history(history)


def end_task_lock():
    """Append to decision_history, then delete task_lock.json (task complete)."""
    data = load_task_lock()
    if data:
        _append_to_history(data)
    if os.path.exists(TASK_LOCK_FILE):
        os.remove(TASK_LOCK_FILE)
    return True
