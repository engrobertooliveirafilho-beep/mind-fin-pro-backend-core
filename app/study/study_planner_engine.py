class StudyPlannerEngine:
    def create_plan(self, message: str, profile=None):
        return {'adaptive': True, 'plan': ['mapear conteÃºdo', 'revisar teoria', 'resolver exercÃ­cios', 'gerar flashcards', 'simulado curto']}