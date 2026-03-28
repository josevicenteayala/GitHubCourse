# Copilot Evidence — Step 01

## Prompt 1 — `normalize_username`

`Complete this function to normalize usernames following the rules in the docstring.`

### Copilot Suggestion

```python
name = name.strip().lower().replace(" ", "_")
name = re.sub(r"[^a-z0-9_]", "", name)
name = re.sub(r"_+", "_", name)
return name.strip("_")
```

## Prompt 2 — `build_slug`

`Complete this function to normalize usernames following the rules in the docstring.`

### Copilot Suggestion

```python
title = title.lower()
title = re.sub(r"[^a-z0-9]+", "-", title)
return title.strip("-")
```

## Why you accepted the suggestions

Both suggestions were accepted because they correctly implemented every rule described in the docstrings, using idiomatic Python with `re.sub` for clean and readable code.

## Final check

No changes were needed after acceptance — the generated code satisfied all the documented rules for both functions on the first suggestion.