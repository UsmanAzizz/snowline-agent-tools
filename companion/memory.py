"""
MEMORY - Learning Loop Module
===========================
Tracks tool usage patterns and suggests based on history.

Concept:
- Every time companion selects a tool, store it
- Next time similar intent appears, suggest based on history
- Track success/failure of tool selections
- Learn from patterns
"""

import os
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

MEMORY_FILE = os.path.expanduser("~/.snowline_memory.json")

@dataclass
class UsageEntry:
    """A recorded tool usage."""
    timestamp: str
    intent: str
    keywords: List[str]
    tool_selected: str
    success: bool
    notes: str = ""


class Memory:
    """
    Learning loop for companion.

    Tracks what tools are selected for what intents.
    Suggests based on past usage.
    """

    def __init__(self):
        self.entries: List[UsageEntry] = []
        self.load()

    def load(self):
        """Load memory from disk."""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = [
                        UsageEntry(**e) for e in data.get("entries", [])
                    ]
            except Exception:
                self.entries = []
        else:
            self.entries = []

    def save(self):
        """Save memory to disk."""
        try:
            os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "entries": [
                        e.__dict__ for e in self.entries[-100:]  # Keep last 100 entries
                    ]
                }, f, indent=2)
        except Exception:
            pass

    def record(self, intent: str, keywords: List[str], tool: str, success: bool = True, notes: str = ""):
        """Record a tool selection."""
        entry = UsageEntry(
            timestamp=time.strftime("%Y-%m-%d %H:%M"),
            intent=intent,
            keywords=keywords,
            tool_selected=tool,
            success=success,
            notes=notes
        )
        self.entries.append(entry)
        self.save()

    def suggest(self, intent: str, keywords: List[str]) -> Optional[str]:
        """
        Suggest tool based on history.

        Returns tool name if confidence > 70%, else None.
        """
        if not self.entries:
            return None

        # Find similar intents/keywords
        matches = {}
        for entry in self.entries[-50:]:  # Check recent
            # Keyword overlap
            overlap = len(set(keywords) & set(entry.keywords))
            if overlap > 0:
                key = entry.tool_selected
                if key not in matches:
                    matches[key] = {"count": 0, "success": 0}
                matches[key]["count"] += overlap
                if entry.success:
                    matches[key]["success"] += 1

        if not matches:
            return None

        # Calculate confidence
        best_tool = None
        best_confidence = 0

        for tool, stats in matches.items():
            success_rate = stats["success"] / max(stats["count"], 1)
            # Simple confidence: success rate * recency bonus
            confidence = success_rate
            if confidence > best_confidence and confidence >= 0.7:
                best_confidence = confidence
                best_tool = tool

        return best_tool

    def get_stats(self) -> Dict:
        """Get memory statistics."""
        tool_counts = {}
        for entry in self.entries:
            tool_counts[entry.tool_selected] = tool_counts.get(entry.tool_selected, 0) + 1

        return {
            "total_entries": len(self.entries),
            "tool_usage": tool_counts,
            "last_used": self.entries[-1].timestamp if self.entries else None
        }

    def reset(self):
        """Clear memory."""
        self.entries = []
        if os.path.exists(MEMORY_FILE):
            os.remove(MEMORY_FILE)


# Quick interface
memory = Memory()

def remember(intent: str, keywords: List[str], tool: str, success: bool = True):
    """Quick record."""
    memory.record(intent, keywords, tool, success)

def recall(intent: str, keywords: List[str]) -> Optional[str]:
    """Quick recall."""
    return memory.suggest(intent, keywords)

def stats() -> Dict:
    """Quick stats."""
    return memory.get_stats()
