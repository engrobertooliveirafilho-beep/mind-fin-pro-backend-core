from datetime import datetime
class StudentMemoryGraph:
    def extract_nodes(self, sender_id: str, message: str):
        low = (message or '').lower()
        nodes = []
        for key, typ in [('estudando','discipline'),('dificuldade','difficulty'),('prova','exam'),('objetivo','goal')]:
            if key in low:
                nodes.append({'sender_id': sender_id, 'node_type': typ, 'value': message, 'confidence': .82, 'created_at': datetime.utcnow().isoformat()})
        return nodes