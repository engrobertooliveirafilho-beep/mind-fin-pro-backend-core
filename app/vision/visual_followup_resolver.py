from app.vision.multi_vision_consensus_runtime import MultiVisionConsensusRuntime

class VisualFollowupResolver:

    def __init__(self):
        self.consensus = MultiVisionConsensusRuntime()

    def is_visual_followup(self, message):

        msg = str(message).lower()

        keys = [
            "carro",
            "ano",
            "modelo",
            "flor",
            "imagem",
            "foto",
            "detalhe",
            "analise",
            "aprofunde"
        ]

        return any(k in msg for k in keys)

    def answer(self, message, visual_context):

        if not visual_context:
            return None

        analysis = visual_context.get("analysis", "")

        if not analysis:
            return None

        return self.consensus.refine(message, analysis)
