COMPRESSED_MEMORY = []

def compress_memory(content: str):
    compressed = " ".join(content.split()[:10])

    item = {
        "original_size": len(content),
        "compressed_size": len(compressed),
        "compressed": compressed
    }

    COMPRESSED_MEMORY.append(item)

    return {
        "status": "ok",
        "compression_ratio": round(
            len(compressed) / max(len(content),1), 2
        ),
        "item": item
    }

def compression_report():
    return {
        "status": "ok",
        "compressed_items": len(COMPRESSED_MEMORY),
        "items": COMPRESSED_MEMORY[-20:]
    }
