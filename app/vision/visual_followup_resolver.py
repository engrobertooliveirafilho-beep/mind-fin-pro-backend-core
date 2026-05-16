from app.vision.multi_vision_consensus_runtime import MultiVisionConsensusRuntime

class VisualFollowupResolver:

    def __init__(self):
        self.consensus = MultiVisionConsensusRuntime()

    def is_visual_followup(self, message):
        msg = str(message or "").lower()

        keys = [
            "imagem","foto","carro","modelo","ano",
            "flor","flores","detalhe","aprofund",
            "analise","visual","parece"
        ]

        return any(k in msg for k in keys)

    def answer(self, message, visual_context):

        try:

            if not visual_context:
                return None

            analysis = visual_context.get("analysis", "")

            if not analysis:
                return None

            result = self.consensus.refine(message, analysis)

            if not result:
                return analysis[:800]

            return str(result)[:1200]

        except Exception as e:

            print(f"VISUAL_FOLLOWUP_ERROR={type(e).__name__}:{str(e)[:120]}")

            if visual_context:
                return str(
                    visual_context.get("analysis", "")
                )[:800]

            return "Recebi sua pergunta visual, mas ocorreu uma falha temporária."
