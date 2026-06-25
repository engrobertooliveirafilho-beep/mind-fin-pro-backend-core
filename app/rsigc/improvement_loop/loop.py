class RecursiveImprovementLoop:
    def improve(self, metrics):
        return {
            "improved": True,
            "next_iteration": metrics["score"] + 0.01
        }
