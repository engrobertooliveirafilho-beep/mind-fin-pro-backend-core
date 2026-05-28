from app.runtime.intent_arbitration_priority_engine import arbitrate_intent_priority
CTX={"last_topic":"implantação"}
def test_social_override(): assert arbitrate_intent_priority("quem é vc?",CTX).selected_intent=="social"
def test_calculation_override(): assert arbitrate_intent_priority("quanto é 4x6",CTX).selected_intent=="calculation"
def test_troubleshooting_override(): assert arbitrate_intent_priority("ainda deu errado",CTX).selected_intent=="troubleshooting"
def test_task_override(): assert arbitrate_intent_priority("busque o erro",CTX).selected_intent=="task_execution"
def test_verification_override(): assert arbitrate_intent_priority("verifique isso",CTX).selected_intent=="verification"
def test_followup_short(): assert arbitrate_intent_priority("aprofunde",CTX).selected_intent=="followup_contextual"
def test_open_loop(): assert arbitrate_intent_priority("e depois?",CTX).selected_intent=="open_loop_continuation"
def test_ambiguity(): assert arbitrate_intent_priority("isso",CTX).selected_intent=="open_loop_continuation"
def test_topic_switch(): assert arbitrate_intent_priority("calcule 20 mais 30",CTX).selected_intent=="calculation"
def test_topic_return(): assert arbitrate_intent_priority("prossiga",CTX).selected_intent=="followup_contextual"
