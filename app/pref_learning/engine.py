from dataclasses import dataclass
from typing import Any, Dict, DefaultDict
from collections import defaultdict


@dataclass
class PreferenceStats:
    """
    STEP 541 - Estatísticas agregadas de preferencia.
    """
    total_reward: float = 0.0
    count: int = 0

    def update(self, reward: float) -> None:
        self.total_reward += float(reward)
        self.count += 1

    @property
    def avg_reward(self) -> float:
        if self.count == 0:
            return 0.0
        return self.total_reward / float(self.count)


class LongHorizonPreferenceLearner:
    """
    STEP 541 - Núcleo minimo de aprendizado de preferencias de longo prazo.

    - 100% em memoria
    - nao toca em BD nem em rotas
    - interface simples:
        update(user_id, signal, reward)
        get_preferences(user_id)
    """

    def __init__(self) -> None:
        self._per_user: DefaultDict[str, PreferenceStats] = defaultdict(PreferenceStats)

    def update(self, user_id: str, signal: Dict[str, Any], reward: float) -> None:
        """
        Atualiza as estatisticas do usuario com um novo "reward" agregado.
        O `signal` é aceito mas nao é usado neste STEP (espaço para evolucao futura).
        """
        _ = signal  # mantido para futura expansao
        self._per_user[user_id].update(reward)

    def get_preferences(self, user_id: str) -> Dict[str, Any]:
        stats = self._per_user.get(user_id)
        if stats is None:
            return {
                "user_id": user_id,
                "count": 0,
                "avg_reward": 0.0,
            }
        return {
            "user_id": user_id,
            "count": stats.count,
            "avg_reward": stats.avg_reward,
        }

