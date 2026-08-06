"""
core_grilling.py - Grilling decision logic.
"""
from .core_memory import load_user_level


def should_grill(result) -> dict:
    """
    Deteksi sederhana apakah instruksi butuh grilling.
    Bahasa disesuaikan berdasarkan user_level dari memory.json.

    Args:
        result: AnalyzeResult from core_intent.analyze_intent()

    Returns:
        dict dengan:
        - needs_grilling: bool
        - reason: str (penjelasan kenapa)
    """
    # Guard: ensure entities is never None
    _entities = result.entities if result.entities is not None else []
    user_level = load_user_level()

    # Micro Task criteria:
    # HIGH confidence + HIGH specificity = langsung eksekusi
    if result.confidence_level == "HIGH" and result.specificity == "high":
        return {
            "needs_grilling": False,
            "reason": "Micro Task - specific dan confident, langsung eksekusi"
        }

    # Specific entity + high specificity = Micro Task ( MESKIPUN MEDIUM confidence)
    if len(_entities) >= 1 and result.specificity == "high":
        return {
            "needs_grilling": False,
            "reason": "Micro Task - specific entity detected"
        }

    # MEDIUM/LOW confidence without specific entity = perlu clarify
    if result.confidence_level in ("MEDIUM", "LOW", "NONE"):
        if user_level >= 7:
            # Technical language for experienced users
            reason = (
                f"confidence={result.confidence_level}, specificity={result.specificity} "
                f"({len(_entities)} entities extracted) - perlu konfirmasi"
            )
        else:
            # Simple language for default/low level
            reason = f"Confidence {result.confidence_level} - perlu konfirmasi"
        return {
            "needs_grilling": True,
            "reason": reason
        }

    # Long instruction without entities = ambiguous
    words = result.input.split()
    if len(words) > 15 and len(_entities) == 0:
        if user_level >= 7:
            reason = f"instruction length={len(words)} words, 0 entities, confidence={result.confidence_level} - perlu konfirmasi"
        else:
            reason = f"Instruction >15 words tanpa entitas spesifik - perlu konfirmasi"
        return {
            "needs_grilling": True,
            "reason": reason
        }

    # Default: grilling needed for non-trivial tasks
    return {
        "needs_grilling": True,
        "reason": "Ambiguous intent"
    }
