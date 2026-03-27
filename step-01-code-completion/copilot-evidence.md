# Copilot Evidence — Step 01

## Prompt 1

`Complete this function to normalize usernames following the rules in the docstring.`

### Copilot Suggestion

Copilot generated the full implementation for `normalize_username`:

```python
name = name.strip().lower().replace(" ", "_")
name = re.sub(r"[^a-z0-9_]", "", name)
name = re.sub(r"_+", "_", name)
return name.strip("_")
```

### Why I accepted the suggestion

Accepted — the suggestion correctly follows all six rules in the docstring: trims whitespace, lowercases, replaces spaces with underscores, removes invalid characters, collapses repeated underscores, and strips leading/trailing underscores.

## Prompt 2

`Complete this function to normalize usernames following the rules in the docstring.` (applied to `build_slug`)

### Copilot Suggestion

Copilot generated the full implementation for `build_slug`:

```python
title = title.lower()
title = re.sub(r"[^a-z0-9]+", "-", title)
return title.strip("-")
```

### Why I accepted the suggestion

Accepted — the suggestion correctly lowercases the input, replaces any sequence of non-alphanumeric characters with a single hyphen, and strips leading/trailing hyphens, matching all the docstring rules.

## Final check

Both functions were implemented in a single pass each. No changes were needed after the initial suggestions — the generated code was correct and complete.