import pandas as pd
import logging
from typing import Optional
from app.services.chat_service import ChatService
from app.services.qdrant_service import QdrantService
from app.models.chat import Message

log = logging.getLogger(__name__)

class MultiAgentService:
    def __init__(self):
        self.base_service = ChatService()
        self.qdrant = QdrantService()

    # --- Lecture générique CSV ---
    def load_csv(self, path: str, sep=";", parse_dates=None) -> Optional[pd.DataFrame]:
        try:
            return pd.read_csv(path, sep=sep, parse_dates=parse_dates, dayfirst=True)
        except Exception as e:
            log.error(f"Erreur lecture {path}: {e}")
            return None

    # --- Lecture CSV météo ---
    def load_weather(self, csv_path: str, date: str) -> str:
        df = self.load_csv(csv_path, parse_dates=["datetime"], sep = ',')
        if df is None:
            return "⚠️ Impossible de lire les données météo."
        df_day = df[df["datetime"].dt.date.astype(str) == date]
        if df_day.empty:
            return f"Aucune donnée météo pour {date}."
        return "\n".join(
            f"{row['datetime'].strftime('%H:%M')} - {row['weather']} ({row['temperature']}°C)"
            for _, row in df_day.iterrows()
        )

    # --- Lecture CSV événements ---
    def load_events(self, csv_path: str, date: str) -> str:
        df = self.load_csv(csv_path, parse_dates=["date"])
        if df is None:
            return "⚠️ Impossible de lire les événements."
        df_day = df[df["date"].dt.date.astype(str) == date]
        if df_day.empty:
            return f"Aucun événement prévu le {date}."
        return "\n".join(
            f"🎭 {row.get('titre', 'Sans titre')} "
            f"(Lieu: {row.get('lieu', 'Non précisé')}, "
            f"Affluence: {row.get('affluence', 'Non précisée')}, "
            f"Durée: {row.get('duree_de_visite', 'Non précisée')})"
            for _, row in df_day.iterrows()
        )

    # --- Lecture CSV supplémentaires ---
    def load_boutique(self, path="data/prdt_boutique.csv") -> list[str]:
        df = self.load_csv(path)
        if df is None: return []
        return [f"{row['Nom_produit']} ({row['tarif']})" for _, row in df.iterrows()]

    def load_expos(self, path="data/expo.csv") -> list[str]:
        df = self.load_csv(path, parse_dates=["date"])
        if df is None: return []
        return [f"🖼️ {row['nom_exposition']} ({row['periode']})" for _, row in df.iterrows()]

    def load_activites_famille(self, path="data/activ_famille.csv") -> list[str]:
        df = self.load_csv(path)
        if df is None: return []
        return [f"{row['nom_activite']} - {row['type_activite']} ({row['tarif']})" for _, row in df.iterrows()]

    def load_restos(self, path="data/resto.csv") -> list[str]:
        df = self.load_csv(path)
        if df is None: return []
        return [f"🍽️ {row['nom_restaurant']} ({row['type_offre']} – {row['tarif_moyen']})" for _, row in df.iterrows()]

    def load_logements(self, path="data/logement.csv") -> list[str]:
        df = self.load_csv(path)
        if df is None: return []
        return [
            f"🏨 {row['nom_logement']} ({row['tarif_moyen']}, {row['proximité_chateau']}, "
            f"Adapté PMR: {row.get('adapté_PMR', 'Non précisé')})"
            for _, row in df.iterrows()
        ]
    # --- Lecture CSV billetterie ---
    def load_billetterie(self, csv_path: str) -> str:
        try:
            df = pd.read_csv(csv_path, sep=";")
            df.columns = df.columns.str.strip()

            rows = []
            for _, row in df.iterrows():
                rows.append(
                    f"🎟️ {row.get('titre_activite', 'Sans titre')} "
                    f"(Type: {row.get('type_evenement', 'Non précisé')}, "
                    f"Affluence: {row.get('affluence_domaine', 'Non précisée')}, "
                    f"Tarif plein: {row.get('tarif_adultes_plein', 'Non précisé')}, "
                    f"Tarif réduit: {row.get('tarif_reduit_supp', 'Non précisé')}, "
                    f"Durée estimée: {row.get('duree_estimee', 'Non précisée')})"
                )
            return "\n".join(rows)
        except Exception as e:
            log.error(f"Erreur lecture billetterie: {e}")
            return "⚠️ Impossible de charger les données billetterie."


    # --- Agents ---
    async def profiling_agent(self, user_input: str) -> str:
        system_prompt = Message(
            role="system",
            content=(
                "Tu es un expert en profiling touristique au Château de Versailles. "
                "Analyse le type de visiteur (famille, couple, senior, groupe scolaire, etc.). "
                "⚠️ Si aucun indice n’est donné, suppose un profil 'visiteur adulte standard'."
            )
        )
        reply, _ = await self.base_service.generate([
            system_prompt, Message(role="user", content=user_input or "Pas d'indication donnée")
        ])
        return reply

    async def constraints_agent(self, persona: str, weather: str, events: str) -> str:
        system_prompt = Message(
            role="system",
            content=(
                "Tu es un expert en gestion des contraintes touristiques. "
                "Analyse la météo et les événements prévus. "
                "Donne une synthèse utile et exploitable pour planifier la visite."
            )
        )
        combined_input = f"Profil: {persona}\n\nMétéo:\n{weather}\n\nÉvénements:\n{events}"

        reply, _ = await self.base_service.generate([
            system_prompt, Message(role="user", content=combined_input)
        ])
        return reply

    async def planner_agent(self, user_input: str, profile: str, constraints: str) -> str:
        restos = self.load_restos()
        produits = self.load_boutique()
        activites_famille = self.load_activites_famille()
        expos = self.load_expos()
        logements = self.load_logements()

        resto_text = "\n".join(restos[:3]) if restos else "Pas de suggestions restos disponibles."
        produit_text = produits[0] if produits else "Pas de produit trouvé."
        famille_text = "\n".join(activites_famille[:3]) if "famille" in profile.lower() else ""
        expo_text = "\n".join(expos[:2]) if expos else ""
        logement_text = "\n".join(logements[:3]) if ("2 jours" in user_input.lower() or "week-end" in user_input.lower()) else ""

        system_prompt = Message(
            role="system",
            content=(
                "Tu es un assistant touristique expert du Château de Versailles.\n\n"
                "👉 Si la demande concerne l’optimisation ou la planification de visite :\n"
                "- Propose un itinéraire clair et structuré en Markdown\n"
                "- Ajoute une pause déjeuner avec suggestions de restaurants\n"
                "- Termine par un passage à la boutique avec une suggestion adaptée au profil\n"
                "- Si profil = famille, propose aussi des activités adaptées aux familles\n"
                "- Mentionne éventuellement une exposition temporaire si pertinente\n"
                "- ⚠️ Si la visite dure plus d'une journée (mots-clés: 2 jours, week-end, plusieurs jours), "
                "ajoute des suggestions de logements proches du château."
            )
        )

        combined_input = (
            f"Profil: {profile}\n"
            f"Contraintes: {constraints}\n"
            f"Demande: {user_input}\n\n"
            f"Suggestions restos:\n{resto_text}\n\n"
            f"Souvenir boutique: {produit_text}\n\n"
            f"Activités famille: {famille_text}\n\n"
            f"Expositions: {expo_text}\n\n"
            f"Logements: {logement_text}\n"
        )

        reply, _ = await self.base_service.generate([
            system_prompt, Message(role="user", content=combined_input)
        ])
        return reply

    async def intent_agent(self, user_input: str) -> str:
        system_prompt = Message(
            role="system",
            content=(
                "Tu es un classifieur d'intentions.\n"
                "- Réponds 'itinerary' si la demande est un plan, un parcours ou une optimisation de visite.\n"
                "- Réponds 'qa' si c’est une question ponctuelle (météo, affluence, événements).\n"
                "- Réponds 'doc' si la question nécessite des infos pratiques issues de la base documentaire.\n"
                "- Réponds 'lodging' si la demande concerne directement les hôtels, logements ou hébergements.\n"
                "⚠️ Réponds UNIQUEMENT par 'itinerary', 'qa', 'doc' ou 'lodging'."
            )
        )
        reply, _ = await self.base_service.generate([
            system_prompt, Message(role="user", content=user_input)
        ])
        return reply.strip().lower()

    async def concierge_agent(self, user_input: str, profile: str, weather: str, events: str) -> str:
        system_prompt = Message(
            role="system",
            content="Tu es un assistant touristique. Réponds simplement à la question, "
                    "en utilisant si pertinent le profil, la météo et les événements fournis."
        )
        combined = f"Profil: {profile}\nMétéo: {weather}\nÉvénements: {events}\n\nDemande: {user_input}"

        reply, _ = await self.base_service.generate([
            system_prompt, Message(role="user", content=combined)
        ])
        return reply

    async def doc_agent(self, user_input: str, embedding_fn, domain: str = None) -> str:
        if domain is None:
            domain = "pratiques"
            if any(word in user_input.lower() for word in ["tarif", "prix", "billet", "ticket", "réduction"]):
                domain = "billetterie"
            elif any(word in user_input.lower() for word in ["plan", "carte", "domaine", "jardin", "accès"]):
                domain = "plan"
            elif any(word in user_input.lower() for word in ["hôtel", "hotel", "logement", "hébergement"]):
                domain = "logement"

        query_vector = embedding_fn(user_input)
        docs = self.qdrant.search(query_vector, domain=domain, top_k=5)
        context = "\n".join([d.get("text", "") for d in docs]) if docs else "Aucun document trouvé."

        system = Message(
            role="system",
            content=(
                f"Tu es un assistant documentaire spécialisé sur le Château de Versailles ({domain}). "
                "Réponds uniquement à partir du contexte fourni ci-dessous. "
                "Si l’information n’est pas présente, indique-le clairement."
            )
        )

        combined = f"Contexte:\n{context}\n\nQuestion: {user_input}"

        reply, _ = await self.base_service.generate([
            system, Message(role="user", content=combined)
        ])
        return reply
    
    async def billetterie_agent(self, user_input: str, billetterie_info: str) -> str:
            system_prompt = Message(
                role="system",
                content=(
                    "Tu es un assistant expert de la billetterie du Château de Versailles. "
                    "Réponds uniquement à partir des données fournies (types d’activités, tarifs, réductions, accessibilité). "
                    "Ne fais pas d’invention."
                )
            )
            combined = f"Données billetterie:\n{billetterie_info}\n\nQuestion: {user_input}"

            reply, _ = await self.base_service.generate([
                system_prompt, Message(role="user", content=combined)
            ])
            return reply


    async def run(
        self,
        user_input: str,
        date: str,
        weather_csv: str,
        events_csv: str,
        billetterie_csv: str = "data/billeterie.csv",
        logements_csv: str = "data/logement.csv",  # ✅ renommé
        embedding_fn: Optional[callable] = None
    ) -> dict:
        # Charger météo, événements, billetterie, logements
        weather_info = self.load_weather(weather_csv, date)
        events_info = self.load_events(events_csv, date)
        billetterie_info = self.load_billetterie(billetterie_csv)
        logements_info = self.load_logements(logements_csv)  # ✅ appel correct

        # Profiling et intention
        profile = await self.profiling_agent(user_input)
        intent = await self.intent_agent(user_input)

        if intent == "itinerary":
            constraints = await self.constraints_agent(profile, weather_info, events_info)
            itinerary = await self.planner_agent(user_input, profile, constraints)

            # 👉 Suggestion logements si séjour > 1 jour
            if any(word in user_input.lower() for word in ["2 jours", "week-end", "plusieurs jours", "logement", "hôtel"]):
                logements_text = "\n".join(logements_info[:3]) if logements_info else "Pas de suggestions logements disponibles."
                itinerary += f"\n\n### 🏨 Suggestions d’hébergement\n{logements_text}"

            return {
                "mode": "itinerary",
                "profiling": profile,
                "constraints": constraints,
                "itinerary": itinerary,
            }

        elif intent == "qa":
            # Réponse simple
            answer = await self.concierge_agent(user_input, profile, weather_info, events_info)
            return {"mode": "qa", "answer": answer}

        elif intent == "doc" and embedding_fn:
            # Vérif si la question est sur la billetterie
            if any(word in user_input.lower() for word in ["tarif", "prix", "billet", "ticket", "réduction"]):
                answer = await self.billetterie_agent(user_input, billetterie_info)
                return {"mode": "doc", "answer": answer, "domain": "billetterie"}
            
            # Sinon on passe par Qdrant
            domain = "pratiques"
            if any(word in user_input.lower() for word in ["plan", "carte", "domaine", "jardin", "accès"]):
                domain = "plan"
            elif any(word in user_input.lower() for word in ["hôtel", "hotel", "logement", "hébergement"]):
                domain = "logement"

            answer = await self.doc_agent(user_input, embedding_fn, domain=domain)
            return {"mode": "doc", "answer": answer, "domain": domain}

        elif intent == "lodging":
            logements_text = "\n".join(logements_info[:3]) if logements_info else "Pas de suggestions logements disponibles."
            return {"mode": "lodging", "answer": logements_text}

        else:
            return {"mode": "unknown", "answer": "⚠️ Je n’ai pas compris la demande."}
