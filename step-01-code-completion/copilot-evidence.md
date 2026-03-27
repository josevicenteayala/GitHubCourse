# Copilot Evidence — Step 01

## Prompt 1

`Complete this function to normalize usernames following the rules in the docstring.`

### Copilot Suggestion — `normalize_username`

Copilot generated the full implementation using `re.sub` to strip invalid characters, collapse repeated underscores, and trim leading/trailing underscores:

```python
name = name.strip().lower().replace(" ", "_")
name = re.sub(r"[^a-z0-9_]", "", name)
name = re.sub(r"_+", "_", name)
return name.strip("_")
```

## Prompt 2

`Complete this function to normalize usernames following the rules in the docstring.`

### Copilot Suggestion — `build_slug`

Copilot generated a concise slug builder that lowercases the title, replaces non-alphanumeric sequences with a single hyphen, and strips leading/trailing hyphens:

```python
title = title.lower()
title = re.sub(r"[^a-z0-9]+", "-", title)
return title.strip("-")
```

## Why you accepted the suggestions

Both suggestions were accepted because they correctly followed every rule in the docstrings, used idiomatic Python with `re.sub`, and produced clean, readable implementations.

## Final check

No changes were needed after acceptance — the generated code satisfied all the documented rules for both functions on the first suggestion.