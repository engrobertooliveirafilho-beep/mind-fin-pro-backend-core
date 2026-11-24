import csv
from p2281_guard import pretest

def run(edges_path):
    with open(edges_path, newline='', encoding='utf-8') as stream:
        edges = list(csv.DictReader(stream))
    for edge in edges:
        edge['edge_id'] = edge.get('edge_id') or '|'.join(edge[k] for k in ('symbol','timeframe','strategy','params'))
    return pretest(edges)
