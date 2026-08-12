from pathlib import Path

p = Path("app/retrieval/semantic_provider.py")
s = p.read_text(encoding="utf-8")

if "P4.65E_BROAD_SEARCH_FALLBACK" in s:
    print("PATCH_ALREADY_PRESENT")
    raise SystemExit(0)

old = '''                cur.execute("""
                select
                    message,
                    metadata,
                    1-(embedding <=> %s::vector) as score
                from neura_embeddings
                where sender_id=%s
                order by embedding <=> %s::vector
                limit %s
                """,(emb,sender_id,emb,limit))

                rows=[dict(x) for x in cur.fetchall()]

                return rows
'''

new = '''                cur.execute("""
                select
                    message,
                    metadata,
                    sender_id,
                    1-(embedding <=> %s::vector) as score
                from neura_embeddings
                where sender_id=%s
                order by embedding <=> %s::vector
                limit %s
                """,(emb,sender_id,emb,limit))

                rows=[dict(x) for x in cur.fetchall()]

                # P4.65E_BROAD_SEARCH_FALLBACK
                # If the runtime sender_id has no embedded rows, search global knowledge.
                # This connects Drive/Knowledge ingestion to reasoning without requiring
                # the WhatsApp sender_id to match ingestion sender_id.
                if not rows:
                    cur.execute("""
                    select
                        message,
                        metadata,
                        sender_id,
                        1-(embedding <=> %s::vector) as score
                    from neura_embeddings
                    order by embedding <=> %s::vector
                    limit %s
                    """,(emb,emb,limit))
                    rows=[dict(x) for x in cur.fetchall()]

                return rows
'''

if old not in s:
    print("PATCH_TARGET_NOT_FOUND")
    raise SystemExit(1)

s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("PATCH_APPLIED_OK")
