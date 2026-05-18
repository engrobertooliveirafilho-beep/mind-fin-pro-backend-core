from app.api.eldora_cognitive_runtime import respond
def assert_scores(out):
    s=out["scores"]
    assert s["persona_consistency_score"] >= 0.90
    assert s["context_continuity_score"] >= 0.90
    assert s["generic_response_score"] <= 0.10
    assert s["memory_relevance_score"] >= 0.85
    assert s["answer_utility_score"] >= 0.90
def test_visual_persona(): assert_scores(respond({"user_id":"Roberto","message":"quero ajustar seu rosto/persona visual"}))
def test_ai_deep_dive(): assert_scores(respond({"user_id":"Roberto","message":"aprofundar em IA para o MIND"}))
def test_continuity(): assert_scores(respond({"user_id":"Roberto","message":"prosseguir evolução"}))
def test_correction(): assert_scores(respond({"user_id":"Roberto","message":"corrigir desvio de assunto"}))
def test_ufc_no_mix(): assert_scores(respond({"user_id":"Roberto","message":"pergunta sobre UFC sem misturar IA"}))
def test_emotional(): assert_scores(respond({"user_id":"Roberto","message":"estou desanimado com o projeto"}))
def test_technical_mind(): assert_scores(respond({"user_id":"Roberto","message":"debug técnico MIND Render Supabase"}))
def test_memory_roberto_mind_eldora(): assert_scores(respond({"user_id":"Roberto","message":"Roberto MIND Eldora memória"}))
