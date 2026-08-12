from app.p18_conversational_execution.response_executor import execute_conversational_response

def test_p18_problem_help_is_short():
    result = execute_conversational_response("tenho um problema me ajuda")
    assert result["status"] == "PASS"
    assert result["answer"] == "Claro. Me conta o que aconteceu."

def test_p18_youtube_link_asks_minimum_missing_info():
    result = execute_conversational_response("quero o link do youtube de uma musica do metallica")
    assert result["status"] == "PASS"
    assert result["answer"] == "Qual música do Metallica você quer?"

def test_p18_direct_list_no_generic_tutorial():
    result = execute_conversational_response("cite todos os aspectos significativos")
    assert result["status"] == "PASS"
    assert "Passo 1" not in result["answer"]
    assert "planejamento hierárquico" in result["answer"]

def test_p18_no_runtime_mutation():
    result = execute_conversational_response("oi")
    assert result["runtime_modified"] is False
    assert result["routes_modified"] is False
    assert result["dispatcher_modified"] is False
    assert result["whatsapp_webhook_modified"] is False
    assert result["production_enabled"] is False
