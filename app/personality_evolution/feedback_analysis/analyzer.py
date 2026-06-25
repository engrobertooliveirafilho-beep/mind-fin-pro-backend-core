class FeedbackAnalyzer:
    def analyze(self, interaction):
        return {
            "confusion": "?" in interaction.get("last_message", ""),
            "engagement": len(interaction.get("history", []))
        }
