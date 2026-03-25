#!/usr/bin/env python3
"""AI Review Agent — reads step-specific prompts, sends diff to an LLM,
and posts structured feedback as a PR comment.

Usage:
    python3 scripts/agent_reviewer.py <diff_file> <step_id> <pr_number> <repo>

Environment variables:
    MODELS_API_KEY  — API key for GitHub Models (or compatible endpoint)
    GH_TOKEN        — GitHub token for posting comments (fallback: GITHUB_TOKEN)
"""
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / ".github" / "prompts"

# GitHub Models endpoint (OpenAI-compatible chat completions)
MODELS_URL = "https://models.github.ai/inference/chat/completions"
DEFAULT_MODEL = "openai/gpt-4o"
MAX_DIFF_CHARS = 60_000  # truncate very large diffs to stay within context


def load_prompt(step_id: str) -> str:
    """Load and concatenate base prompt + step-specific prompt."""
    base_path = PROMPTS_DIR / "base-prompt.md"
    step_path = PROMPTS_DIR / f"{step_id}.md"

    parts: list[str] = []
    if base_path.exists():
        parts.append(base_path.read_text(encoding="utf-8"))
    else:
        print(f"Warning: {base_path} not found", file=sys.stderr)

    if step_path.exists():
        parts.append(step_path.read_text(encoding="utf-8"))
    else:
        print(f"Warning: {step_path} not found, using base prompt only", file=sys.stderr)

    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, diff_content: str) -> str:
    """Send the prompt + diff to the LLM and return the response text."""
    api_key = os.environ.get("MODELS_API_KEY", "")
    if not api_key:
        raise RuntimeError("MODELS_API_KEY environment variable is not set")

    # Truncate diff if too large
    if len(diff_content) > MAX_DIFF_CHARS:
        diff_content = diff_content[:MAX_DIFF_CHARS] + "\n\n... (diff truncated)"

    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Review the following code diff:\n\n```diff\n{diff_content}\n```",
            },
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    data = json.dumps(payload).encode()
    req = urllib.request.Request(MODELS_URL, data=data, headers=headers, method="POST")

    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode())

    return result["choices"][0]["message"]["content"]


def post_review_comment(repo: str, pr_number: str, body: str) -> None:
    """Post the AI review as a PR comment via post_comment.py logic."""
    # Import the sibling module
    scripts_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(scripts_dir))
    from post_comment import post_or_update

    post_or_update(repo, int(pr_number), "ai-review-agent", body)


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "Usage: agent_reviewer.py <diff_file> <step_id> <pr_number> <repo>",
            file=sys.stderr,
        )
        return 1

    diff_file, step_id, pr_number, repo = sys.argv[1:5]

    diff_path = Path(diff_file)
    if not diff_path.exists():
        print(f"Diff file not found: {diff_file}", file=sys.stderr)
        return 1

    diff_content = diff_path.read_text(encoding="utf-8", errors="replace")
    if not diff_content.strip():
        print("Diff is empty, skipping AI review")
        return 0

    system_prompt = load_prompt(step_id)

    try:
        review = call_llm(system_prompt, diff_content)
    except RuntimeError as exc:
        print(f"Skipping AI review: {exc}", file=sys.stderr)
        return 0
    except urllib.error.HTTPError as exc:
        print(f"LLM API error: {exc.code} {exc.reason}", file=sys.stderr)
        return 0

    comment_body = f"🤖 **AI Review for `{step_id}`**\n\n{review}"

    try:
        post_review_comment(repo, pr_number, comment_body)
    except urllib.error.HTTPError as exc:
        print(f"Failed to post comment: {exc.code} {exc.reason}", file=sys.stderr)
        body = exc.read().decode()
        print(body, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
