# P19P38-L rollback
# Moves quarantined files back to original paths.

New-Item -ItemType Directory -Force (Split-Path "P19P37_REAL_COGNITION_MASTER.ps1") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/P19P37_REAL_COGNITION_MASTER.ps1" "P19P37_REAL_COGNITION_MASTER.ps1"

New-Item -ItemType Directory -Force (Split-Path "P2230_MIND_FTMO_PROP_DESK_PIPELINE_CLOSEOUT.ps1") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/P2230_MIND_FTMO_PROP_DESK_PIPELINE_CLOSEOUT.ps1" "P2230_MIND_FTMO_PROP_DESK_PIPELINE_CLOSEOUT.ps1"

New-Item -ItemType Directory -Force (Split-Path "P5_4_CANONICAL_DIAMOND_DEDUP.ps1") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/P5_4_CANONICAL_DIAMOND_DEDUP.ps1" "P5_4_CANONICAL_DIAMOND_DEDUP.ps1"

New-Item -ItemType Directory -Force (Split-Path "P8_MASTER_CONTROLLED_IMPLEMENTATION.txt") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/P8_MASTER_CONTROLLED_IMPLEMENTATION.txt" "P8_MASTER_CONTROLLED_IMPLEMENTATION.txt"

New-Item -ItemType Directory -Force (Split-Path "_evidence_p482a_patched_files.txt") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/_evidence_p482a_patched_files.txt" "_evidence_p482a_patched_files.txt"

New-Item -ItemType Directory -Force (Split-Path "_institutional/") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/_institutional__" "_institutional/"

New-Item -ItemType Directory -Force (Split-Path "_maintenance/") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/_maintenance__" "_maintenance/"

New-Item -ItemType Directory -Force (Split-Path "app/main.py.bak_p4_46x") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/app__main.py.bak_p4_46x" "app/main.py.bak_p4_46x"

New-Item -ItemType Directory -Force (Split-Path "cleanup_f1_strict.py") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/cleanup_f1_strict.py" "cleanup_f1_strict.py"

New-Item -ItemType Directory -Force (Split-Path "cleanup_weak_valuations.py") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/cleanup_weak_valuations.py" "cleanup_weak_valuations.py"

New-Item -ItemType Directory -Force (Split-Path "code_symbol_search_p56e.txt") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/code_symbol_search_p56e.txt" "code_symbol_search_p56e.txt"

New-Item -ItemType Directory -Force (Split-Path "cognitive.diff") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/cognitive.diff" "cognitive.diff"

New-Item -ItemType Directory -Force (Split-Path "custom_search_siterestrict_test.py") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/custom_search_siterestrict_test.py" "custom_search_siterestrict_test.py"

New-Item -ItemType Directory -Force (Split-Path "custom_search_smoke_test.py") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/custom_search_smoke_test.py" "custom_search_smoke_test.py"

New-Item -ItemType Directory -Force (Split-Path "google_cse_debug.py") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/google_cse_debug.py" "google_cse_debug.py"

New-Item -ItemType Directory -Force (Split-Path "google_cse_test.py") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/google_cse_test.py" "google_cse_test.py"

New-Item -ItemType Directory -Force (Split-Path "hardcode_inventory.txt") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/hardcode_inventory.txt" "hardcode_inventory.txt"

New-Item -ItemType Directory -Force (Split-Path "repo_tree.txt") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/repo_tree.txt" "repo_tree.txt"

New-Item -ItemType Directory -Force (Split-Path "rollback_bad_animals.py") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/rollback_bad_animals.py" "rollback_bad_animals.py"

New-Item -ItemType Directory -Force (Split-Path "scripts/") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/scripts__" "scripts/"

New-Item -ItemType Directory -Force (Split-Path "tools/") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/tools__" "tools/"

New-Item -ItemType Directory -Force (Split-Path "trade_log.txt") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/trade_log.txt" "trade_log.txt"

New-Item -ItemType Directory -Force (Split-Path "whatsapp.diff") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/whatsapp.diff" "whatsapp.diff"

New-Item -ItemType Directory -Force (Split-Path "youtube_api_debug.py") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/youtube_api_debug.py" "youtube_api_debug.py"

New-Item -ItemType Directory -Force (Split-Path "yt_video_test.py") | Out-Null
Move-Item -Force "_quarantine/P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732/yt_video_test.py" "yt_video_test.py"
