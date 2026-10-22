# Normalized Study Source

Use this as a lightweight normalization target. Do not expose it verbatim unless useful.

```yaml
source:
  identity:
    type: pdf | document | webpage | github | video | audio | multi | topic
    title: "..."
    origin: "file/url/repository/topic"

  structure:
    - id: "..."
      title: "..."
      children: []

  content:
    - anchor: "page / heading / timestamp / file path"
      text_or_summary: "actual source content"
      kind: prose | code | formula | table | figure | transcript | visual

  reliability:
    primary_content_available: true
    structure_available: true
    anchors_available: true
    visual_content_checked: false

  gaps:
    - anchor: "..."
      issue: "missing / unreadable / unavailable transcript / uncertain order"

  manifest:
    - source_id: "only needed for multi-source study"
      role: primary | supplement | alternative
```

## Rules

- Preserve stable anchors whenever the input supports them.
- Store actual source-derived content or faithful compact summaries; do not fill gaps with generic knowledge.
- Keep visual evidence distinct from transcript/text when that distinction matters.
- For multiple sources, keep provenance attached to each important claim or section.
- `gaps` must survive into planning so the tutor cannot accidentally teach unseen content as source fact.
