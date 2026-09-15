"""All prompt templates for Nura.

Prompts are centralized here as named exports so they stay versionable,
reviewable, and reusable across providers.  Never inline prompt strings
in routes, services, or UI code.
"""

from medibot.prompts.contextualize import CONTEXTUALIZE_Q_PROMPT, CONTEXTUALIZE_Q_SYSTEM
from medibot.prompts.intent import (
    CLASSIFY_INTENT_JSON_SCHEMA,
    CLASSIFY_INTENT_SYSTEM,
    REFUSAL_SYSTEM,
    STATIC_REFUSAL,
)
from medibot.prompts.judge import JUDGE_JSON_SCHEMA, JUDGE_RUBRICS, build_judge_system
from medibot.prompts.memory import ROLLING_SUMMARY_SYSTEM, SUMMARY_SYSTEM_PREFIX
from medibot.prompts.qa import MEDICAL_SYSTEM_PROMPT, QA_PROMPT

__all__ = [
    "CLASSIFY_INTENT_JSON_SCHEMA",
    "CLASSIFY_INTENT_SYSTEM",
    "CONTEXTUALIZE_Q_PROMPT",
    "CONTEXTUALIZE_Q_SYSTEM",
    "JUDGE_JSON_SCHEMA",
    "JUDGE_RUBRICS",
    "MEDICAL_SYSTEM_PROMPT",
    "QA_PROMPT",
    "REFUSAL_SYSTEM",
    "ROLLING_SUMMARY_SYSTEM",
    "STATIC_REFUSAL",
    "SUMMARY_SYSTEM_PREFIX",
    "build_judge_system",
]
