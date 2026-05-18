class TutorReasoningLayer:
    def build_explanation(self, question: str, context: str = '') -> dict:
        q = (question or '').lower()
        if 'deriv' in q:
            return {
                'concept': 'Derivada mede a taxa de variaÃ§Ã£o instantÃ¢nea de uma funÃ§Ã£o.',
                'example': 'Se f(x)=xÂ², entÃ£o fâ€™(x)=2x. No ponto x=3, a taxa de variaÃ§Ã£o Ã© 6.',
                'steps': ['Identifique a funÃ§Ã£o', 'Aplique a regra de derivaÃ§Ã£o', 'Interprete a taxa de variaÃ§Ã£o'],
                'application': 'Serve para velocidade, crescimento, otimizaÃ§Ã£o, economia, fÃ­sica e engenharia.',
                'check_question': 'Quer que eu resolva uma derivada passo a passo?'
            }
        return {
            'concept': 'Vou explicar o conceito de forma simples.',
            'example': 'Uso uma definiÃ§Ã£o curta e depois aplico em um exemplo.',
            'steps': ['DefiniÃ§Ã£o', 'Exemplo', 'AplicaÃ§Ã£o', 'Checagem'],
            'application': 'A aplicaÃ§Ã£o depende da matÃ©ria estudada.',
            'check_question': 'Quer uma explicaÃ§Ã£o simples ou avanÃ§ada?'
        }