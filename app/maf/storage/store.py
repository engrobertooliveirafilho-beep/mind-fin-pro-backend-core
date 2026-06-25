class AssetStore:
    def save(self, asset_type, data):
        return {
            "stored": True,
            "type": asset_type,
            "id": "asset_001"
        }
