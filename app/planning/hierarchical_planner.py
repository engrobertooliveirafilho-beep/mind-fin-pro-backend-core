from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Iterable, Set

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.planning import ContextItem


@dataclass
class SubTaskPlan:
    id: str
    level: int
    description: str
    parent_id: Optional[str] = None
    done: bool = False


@dataclass
class HierarchicalPlan:
    root_goal: str
    steps: List[SubTaskPlan]

    def by_id(self) -> Dict[str, SubTaskPlan]:
        return {s.id: s for s in self.steps}

    def leaves(self) -> List[SubTaskPlan]:
        ids_with_children: Set[str] = {s.parent_id for s in self.steps if s.parent_id}
        return [s for s in self.steps if s.id not in ids_with_children]


class HierarchicalPlanner:
    """
    Planner hierárquico simples, mas plugável.

    - multi-nível (0, 1, 2)
    - horizon_steps controla granularidade
    - memory_summary "contamina" descrições de leafs
    """

    def build_plan(
        self,
        goal: str,
        horizon_steps: int,
        memory_summary: Optional[str] = None,
        base_context: Optional[Iterable[ContextItem]] = None,
    ) -> HierarchicalPlan:
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError('goal required')
        if type(horizon_steps) is not int or horizon_steps < 1:
            raise ValueError('positive integer horizon required')
        steps: List[SubTaskPlan] = []

        root = SubTaskPlan(
            id="root",
            level=0,
            description=goal.strip(),
            parent_id=None,
            done=False,
        )
        steps.append(root)

        mid_count = min(horizon_steps, max(2, min(4, max(1, horizon_steps // 3))))
        leaf_per_mid, remainder = divmod(horizon_steps, mid_count)

        for i in range(mid_count):
            mid = SubTaskPlan(
                id=f"mid-{i+1}",
                level=1,
                description=f"Sub-objetivo {i+1} para: {goal}",
                parent_id=root.id,
                done=False,
            )
            steps.append(mid)
            for j in range(leaf_per_mid + (i < remainder)):
                desc = f"Passo {j+1} de {mid.id} para avançar em: {goal}"
                if memory_summary:
                    desc += f" (considerando memória: {memory_summary[:80]})"
                leaf = SubTaskPlan(
                    id=f"{mid.id}-leaf-{j+1}",
                    level=2,
                    description=desc,
                    parent_id=mid.id,
                    done=False,
                )
                steps.append(leaf)

        return HierarchicalPlan(root_goal=goal, steps=steps)

    def next_actions(
        self,
        plan: HierarchicalPlan,
        completed_ids: Iterable[str],
    ) -> List[SubTaskPlan]:
        completed: Set[str] = set(completed_ids)
        by_id = plan.by_id()

        # marca como done os steps concluídos
        for cid in completed:
            step = by_id.get(cid)
            if step:
                step.done = True

        candidates: List[SubTaskPlan] = []

        for s in plan.steps:
            if s.done:
                continue

            # nível 0 (root/meta) nunca é "ação executável"
            if s.level == 0 or s.parent_id is None:
                continue

            parent = by_id.get(s.parent_id)
            if not parent:
                continue

            # se o pai é root (level 0), não exigimos que esteja done
            if parent.level == 0 or parent.parent_id is None:
                candidates.append(s)
            # se o pai é mid (ou outro), só libera se pai estiver done
            elif parent.done:
                candidates.append(s)

        # prioriza nível mais profundo primeiro (leafs > mids)
        candidates.sort(key=lambda step: step.level, reverse=True)
        return candidates

