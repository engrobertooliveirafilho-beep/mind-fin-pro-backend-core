import ast
from pathlib import Path

path = Path("app/api/whatsapp.py")
src = path.read_text(encoding="utf-8")
lines = src.splitlines()

tree = ast.parse(src)

target = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "eldora_primary_runtime_reply":
        target = node
        break

if target is None:
    raise SystemExit("FUNCTION_NOT_FOUND")

primary_return_line = None
for idx, line in enumerate(lines, start=1):
    if 'return _p19p9_universal_whatsapp_output_guard(inbound_text, visible.get("answer","") if isinstance(visible, dict) else str(visible), str(visible))' in line:
        primary_return_line = idx
        break

if primary_return_line is None:
    raise SystemExit("PRIMARY_PIPELINE_RETURN_NOT_FOUND")

function_end = target.end_lineno

dead_start = primary_return_line + 1
dead_end = function_end

if dead_start > dead_end:
    raise SystemExit("NO_DEAD_CODE_RANGE")

removed = lines[dead_start-1:dead_end]

# safety checks
joined = "\n".join(removed)
required_markers = [
    "P4_28Q_LEGACY_EXPECTED_SHORTCUTS",
    "live_whatsapp_override",
    "semantic_test_injection",
]
if not any(marker in joined for marker in required_markers):
    raise SystemExit("SAFETY_ABORT_MARKERS_NOT_FOUND_IN_DEAD_BLOCK")

new_lines = lines[:dead_start-1] + [
    "",
    "    # P4.63M_DEAD_CODE_REMOVED: unreachable legacy block removed after primary pipeline return.",
] + lines[dead_end:]

path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

print("PATCH_APPLIED_OK")
print("PRIMARY_RETURN_LINE:", primary_return_line)
print("REMOVED_START:", dead_start)
print("REMOVED_END:", dead_end)
print("REMOVED_LINES:", len(removed))
print("REMOVED_BLOCK_BEGIN")
print("\n".join(removed[:80]))
print("REMOVED_BLOCK_END")
