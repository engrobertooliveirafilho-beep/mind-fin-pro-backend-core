CANONICAL_FUNCTIONS = {
    "identity": ["normalize_phone_e164","resolve_or_create_user","export_user_data","delete_user_data"],
    "consents": ["require_consent"],
    "plans": ["resolve_plan","enforce_plan_limits"],
    "billing": ["create_subscription","activate_premium"],
    "safety_security_lgpd": ["prompt_firewall","unicode_cleaner","media_gate","abuse_score","child_mode","admin_guard","route_policy"],
    "persona_cognitive": ["human_like_orchestrator","cognitive_runtime","visual_identity_reasoner","emotional_dialogue_engine","response_quality_guard"],
    "perception_reasoning_quality": ["input_normalizer","media_detector","language_detector","entity_extractor","intent_classifier","reasoning_engine","planner","critic","confidence","contradiction_checker","quality_gate","hallucination_guard"],
    "memory": ["eldora_memory","episodic_memory","semantic_memory","emotional_memory","visual_memory","procedural_memory","context_compressor"],
    "media_voice_video_language": ["pdf_sanitizer","file_gate","validate_mime","extract_text_safely","remove_metadata","transcribe_audio","generate_tts_response","select_response_language"],
    "multi_llm_rag_knowledge": ["llm_router","document_loader","chunker","embedding_generator","evidence_index","source_citation_linker","knowledge_graph","select_model_by_cost","fallback_model","retry_with_backoff"],
    "skills_study_lotofacil": ["skills_registry","skills_router","skills_executor","study_router","document_explainer","class_transcript","task_planner","student_memory","lotofacil_run","lotofacil_report"],
    "drive_forensics_industrial_os": ["rclone_inventory","duplicate_detector","folder_tree_mapper","metadata_extractor","quarantine_planner","core_selector","version_comparator","noise_classifier","sqlite_fts5","dependency_graph","runtime_lineage","knowledge_fusion_engine"]
}
STATUS_FINAL_ADICIONAL = "ELDORA_CANONICAL_FUNCTIONS_EXPANDED"
