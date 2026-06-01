from app.globalgrid.global_grid_engine import GlobalGridEngine
from app.multiavatar.multi_avatar_engine import MultiAvatarEngine
from app.callworld.call_world_engine import CallWorldEngine

class GlobalPresenceEngine:
    """
    Liga GRID GLOBAL → Avatares → CallWorld
    Cria presença cognitiva regionalizada.
    """

    def __init__(self):
        self.grid = GlobalGridEngine()
        self.avatars = MultiAvatarEngine()
        self.worlds = CallWorldEngine()

    def _ensure_default_infra(self):
        # se não tiver cluster nenhum, cria um default
        if not self.grid.list_clusters():
            if not self.grid.list_regions():
                self.grid.add_region("global-default", "Global Default", latency_ms=80.0)
            self.grid.add_cluster("global-cluster-1", "global-default", capacity_score=1.0)

    def provision(self, tenant_id: str):
        self._ensure_default_infra()
        placement = self.grid.place_tenant(tenant_id)
        cluster = placement.cluster_id

        avatar_id = f"avatar-{tenant_id}"
        world_id = f"world-{tenant_id}"

        self.avatars.create(avatar_id)
        self.worlds.create_world(world_id)
        self.worlds.add_participant(world_id, tenant_id)

        return {
            "tenant": tenant_id,
            "cluster": cluster,
            "avatar_id": avatar_id,
            "world_id": world_id
        }
