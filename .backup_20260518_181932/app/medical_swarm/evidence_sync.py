import requests, urllib.parse

class MedicalEvidenceSync:

    def pubmed_search(self, query, limit=5):
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db":"pubmed",
            "term":query,
            "retmode":"json",
            "retmax":limit
        }
        r = requests.get(url, params=params, timeout=20)
        data = r.json()
        return data.get("esearchresult",{}).get("idlist",[])

    def evidence_pack(self, topic):
        ids = self.pubmed_search(topic, 5)
        return {
            "status":"MEDICAL_EVIDENCE_SYNC_OPERATIONAL",
            "topic":topic,
            "pubmed_ids":ids,
            "who_sync":"READY_MANUAL_GUIDELINE_VALIDATION",
            "nih_sync":"READY_MANUAL_GUIDELINE_VALIDATION",
            "note":"PubMed IDs são evidência de busca, não validação clínica automática."
        }
