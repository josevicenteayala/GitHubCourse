# Step 01 — Code Completion

## Copilot Feature
Inline code completion

## Criteria
1. `normalize_username(name: str) -> str` is implemented:
   - Trims leading/trailing whitespace
   - Converts to lowercase
   - Replaces spaces with underscores
   - Removes all characters not in `[a-z0-9_]`
2. `build_slug(title: str) -> str` is implemented:
   - Converts to lowercase
   - Splits into words, removes punctuation
   - Joins with single hyphens
   - Returns empty string for all-punctuation input
3. Both functions handle edge cases (empty strings, special characters, multiple spaces).
4. Code is clean and Pythonic (e.g., uses `re` module or string methods appropriately).
5. `copilot-evidence.md` contains the word "prompt" and shows real interaction with Copilot inline completion.
