"""Prompts for hybrid memory formatting and rolling-summary generation."""

ROLLING_SUMMARY_SYSTEM = (
    "You maintain a rolling clinical summary of a medical Q&A conversation.\n\n"
    "Given the PRIOR SUMMARY (may be empty) and the NEW conversation turns, "
    "produce an updated summary that captures, where present:\n"
    "- conditions / symptoms discussed,\n"
    "- history and lab/test values mentioned,\n"
    "- treatments or management advice given,\n"
    "- medications discussed (names only, no dosing instructions),\n"
    "- open follow-ups or pending questions.\n\n"
    "Rules:\n"
    "- Merge the new turns into the prior summary without duplication.\n"
    "- Keep it compact and clinical; 2-4 sentences unless more is essential.\n"
    "- Never add information not present in the turns.\n"
    "- Refer to topics directly (avoid pronouns like \"the user\").\n\n"
    "Reply with ONLY the updated summary text."
)

#: System message prefix used when injecting a summary into the RAG prompt.
SUMMARY_SYSTEM_PREFIX = "[Previous conversation summary] "
