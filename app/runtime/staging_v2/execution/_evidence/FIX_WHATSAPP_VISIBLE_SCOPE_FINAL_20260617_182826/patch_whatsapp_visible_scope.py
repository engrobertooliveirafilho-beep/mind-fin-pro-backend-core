from pathlib import Path

path = Path("app/api/whatsapp.py")
text = path.read_text(encoding="utf-8")

text = text.replace(
    "from app.runtime.automotive_execution_bias_guard import automotive_execution_bias_guard\n",
    ""
)

text = text.replace(
    "        visible = run_cognitive_pipeline(sender_id, expanded_message)\n"
    "    return visible.get(\"answer\",\"\") if isinstance(visible, dict) else str(visible)\n",
    "        visible = run_cognitive_pipeline(sender_id, expanded_message)\n"
    "        return visible.get(\"answer\",\"\") if isinstance(visible, dict) else str(visible)\n"
)

text = text.replace(
    "        visible = run_cognitive_pipeline(sender_id, expanded_message)\r\n"
    "    return visible.get(\"answer\",\"\") if isinstance(visible, dict) else str(visible)\r\n",
    "        visible = run_cognitive_pipeline(sender_id, expanded_message)\r\n"
    "        return visible.get(\"answer\",\"\") if isinstance(visible, dict) else str(visible)\r\n"
)

path.write_text(text, encoding="utf-8")
print("PATCH_OK")
