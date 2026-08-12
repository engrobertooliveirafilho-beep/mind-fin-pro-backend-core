from pathlib import Path

p = Path("tests/test_p19p36m_hotfix_exclude_current_message.py")
s = p.read_text(encoding="utf-8")

s = s.replace(
'''    assert advisor["should_use_memory"] is True
    assert "joelho" in advisor["memory_hits"] or "emagrecer" in advisor["memory_hits"]
''',
'''    assert advisor["should_use_memory"] is True
    assert "joelho" in advisor["memory_hits"] or "emagrecer" in advisor["memory_hits"]
    assert ctx["p19p36l_memory_fusion_shadow"]["domain_semantic_bridge"]["matched"] is True
'''
)

p.write_text(s, encoding="utf-8")
print("P19P36M_H2_HOTFIX_TEST_UPDATED")
