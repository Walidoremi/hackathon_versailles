from qdrant_client import QdrantClient

class QdrantService:
    def __init__(self):
        # 👉 Mets ici ton URL et ta clé Qdrant
        QDRANT_URL = "https://297ee593-6fa8-4047-ae42-47c57cf7c0ff.europe-west3-0.gcp.cloud.qdrant.io:6333/"   # exemple cloud
        QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.A-zfCSbpxNgq7BYyAKgkf1AUPY3fsyJYL9k7l6D4gkI"

        self.client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            verify=False
        )

        # Définition des collections disponibles
        self.collections = {
            "billetterie": "_billets_et_tarifs_",
            "pratiques": "_modalites_pratiques_",
            "plan": "_decouverte_du_domaine_"
        }

    def search(self, query_vector, domain="pratiques", top_k=5):
        """
        domain = clé qui pointe vers une collection
        """
        collection_name = self.collections.get(domain)
        if not collection_name:
            raise ValueError(f"Collection inconnue: {domain}")

        hits = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
        )
        return [hit.payload for hit in hits]