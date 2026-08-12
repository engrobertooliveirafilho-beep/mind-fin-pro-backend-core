from __future__ import annotations

from typing import Any


def build_image_prompt(decision: dict[str, Any]) -> str:
    return f"""
Use the existing Eldora canonical identity as absolute ground truth.

Create one new photorealistic social-media image.

CREATIVE DECISION
Objective: {decision['objective']}
Platform: {decision['platform']}
Format: {decision['format']}
Scene: {decision['scene']}
Wardrobe: {decision['wardrobe']}
Hair: {decision['hair']}
Makeup: {decision['makeup']}
Prop: {decision['prop']}
Text element: {decision['text_element']}

IDENTITY LOCK
Preserve the exact same adult woman from canonical references.
No face redesign, no age shift, no jaw drift, no eye drift, no nose drift,
no lip drift, no body warp, no plastic skin, no uncanny valley.

VISUAL QUALITY
Natural human anatomy, realistic hands, coherent object interaction,
premium editorial photography, believable lighting, no CGI appearance.

Do not copy any real creator's image or composition.
""".strip()