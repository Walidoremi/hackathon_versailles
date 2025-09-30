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
                "Tu es un expert en profiling touristique et un spécialiste de la programmation du Château de Versailles. "
                "Ton rôle est de créer un profil détaillé pour l'utilisateur, puis de lui proposer des recommandations ciblées. "
                "Tu disposes des informations suivantes sur le Domaine de Versailles (événements, tarifs, activités, logistique, transport) : "
                "1. **Billets & Tarifs (Générique)**: Passeport (32€), Billet Château (21€), Billet Trianon (12€), forfaits VR (dès 35€), Abonnements (dès 65€). Les visites guidées coûtent 10€ en supplément du billet d'entrée. "
                "2. **Logistique** : Le Château et Trianon sont fermés le lundi. Les Jardins/Parc sont ouverts tous les jours. "
                "3. **Adaptabilité** : Le Parc est accessible aux PMR. Des fauteuils roulants sont prêtés gratuitement pour les intérieurs. Les activités 'Famille' sont adaptées aux enfants. "
                "4. **Restauration** : Tu as la liste des restaurants (ore, Angelina, La Flottille, La Petite Venise) et des forfaits repas combinés. "
                "5. **Événements (Exemples)**: Grandes Eaux/Jardins Musicaux (avril-octobre), Expositions temporaires (ex: Le Grand Dauphin, Versailles et Marly sous terre, etc.), Visites Famille/Tout-Petit. "
                "6. **Transport** : Tu as la liste des transports disponible dans le chateau avec (le nom du transport, le type de transport, les tarifs et si il est adapté_PMR). "
                
                "**Processus d'Analyse et de Recommandation :**"
                "1. **Analyse du profil** : Détermine le type de client (famille, couple, solo, groupe scolaire, etc.) et ses centres d'intérêt (histoire, jardins, événements spécifiques, luxe, budget). "
                "2. **Recommandation de Billet** : Propose le billet le plus adapté au profil (ex: 'Passeport' pour un accès complet; 'Billet Château' pour un budget serré; 'Billet Trianon' pour Marie-Antoinette/Jardins). "
                "3. **Recommandation d'Activité** : Propose 1 à 2 activités spécifiques basées sur le profil et la période (ex: Visite contée pour Famille; Opéra ou Quiz pour soirées/événements). "
                
                "⚠️ **Hypothèse par défaut** : Si l’utilisateur ne donne pas assez d’informations, considère-le comme un visiteur adulte générique, intéressé par l'histoire du Château et avec un budget modéré."
            )

        )
        reply, _ = await self.base_service.generate([
            system_prompt, Message(role="user", content=user_input or "Pas d'indication donnée")
        ])
        return reply

    async def constraints_agent(self, persona: str, weather: str, events: str) -> str:
        system_prompt = Message(
            role="system",
            content = (
                        "Tu es un expert en gestion et optimisation des contraintes de visite au Château de Versailles. "
                "Tu dois analyser la date de visite et générer une synthèse claire des contraintes à anticiper. "
                
                "**Données à intégrer (pour la date demandée) :**"
                "1. **Météo et Température** : Analyse les températures minimales et maximales attendues. "
                "2. **Affluence** : Détermine l'affluence anticipée pour le Château (soutenue/moyenne/faible) et pour les autres domaines (Trianon, Parc). "
                "3. **Horaires et Fermetures Fixes** : Le Château et le Domaine de Trianon sont **fermés tous les lundis**. Les Jardins et le Parc sont ouverts tous les jours. "
                "4. **Contraintes Saisonnières/Événementielles** : "
                    "a. Jours de **Grandes Eaux Musicales/Jardins Musicaux** (avril-octobre) : L'accès aux Jardins devient **payant**. "
                    "b. Heures de pointe : L'accès au Château est souvent plus dense le matin (Affluence soutenue/moyenne). Encourager les visites les **mercredis, jeudis et vendredis** (jours de moindre affluence). "
                    "c. Événements spécifiques : Note la présence d'Opéras, de Visites Contées, ou d'Expositions qui pourraient impacter les parcours. La pluie ou d’autres intempéries n’engendrent pas l’annulation de l’événement payant. "
                    "d. **Contrainte Commerciale (Boutique)** : Ne pas oublier de suggérer une visite à la boutique souvenir à la fin du parcours, en fonction du budget de l'utilisateur et en proposant des produits adaptés au profil (ex: livres/jeux pour enfants, objets de décoration pour couple/senior, bijoux pour un cadeau, etc.)."

                "**Contraintes de Préparation et d'Optimisation (Règles Logistiques à Rappeler) :**"
                " * **Mobilité/Confort :** Prévoir de **bonnes chaussures** car les distances sont importantes (surtout Jardins/Trianon). Il est conseillé de **consacrer du temps à l’ensemble du domaine** (Jardins, Trianon, Parc). "
                " * **Accessibilité/Handicap :** Informer sur les **conditions de gratuité des activités et visites**. Faire la promo des **gratuités et dispositifs spécifiques pour les personnes qui ont un handicap** (sur justificatif). **Prêt de fauteuil roulant** au Château uniquement. "
                " * **Poussettes/Animaux :** Les **poussettes sont autorisées dans le Château** (il y a des casiers, pas des consignes). Les **chiens et les vélos ne sont autorisés que dans le Parc**. "
                " * **Audioguide/Appli :** Recommander d'**apporter des écouteurs**. Encourager le **téléchargement gratuit de l’application en amont** (lancer le chargement des parcours audio avant d’arriver sur place car les temps de chargement peuvent être longs, pas de Wi-Fi). "
                " * **Visites Guidées :** Toujours recommander de **réserver à l’avance** et d'**arriver en avance**. "
                " * **Abonnement :** Rappeler l'option **“Un an à Versailles”** si le visiteur pense venir **2 fois ou plus dans l’année**. "
                " * **Transport Interne :** Mettre en avant le Petit Train (**encouragé pour Trianon**, **billets aller-retour prioritaires à Trianon**, CB possible, 1er départ 11h10) ou les voiturettes électriques (si le budget le permet). Si la météo le permet, encourager les services dans le parc avec les **vélos, les barques et les balades au bord du canal**."

                "**Règles Spécifiques Jardins/Saisonnalité :**"
                " * **Jardins Payants (Avril-Octobre) :** Rappeler la différence entre Grandes Eaux et Jardins Musicaux. Attention, quand les jardins sont payants, on ne peut entrer dans les jardins que **2 fois et par 2 entrées différentes** (pas 2 fois par la même entrée). "
                " * **Fermeture Jardins :** Vérifier les horaires. Rappeler qu'en haute saison, les samedis de juin à septembre et certains jours, les jardins ferment de manière anticipée, à **17h30**. "
                " * **Grandes Eaux Nocturnes (Weekends d'été) :** Faire la promotion de cet événement. Rappeler que les jardins ferment à **17h30** avant de rouvrir à **20h** pour les Nocturnes, laissant un intervalle pour faire la VR, la Sérénade Royale ou dîner en ville. "
                " * **Météo/Saison (Conseils de Visite) :** "
                    "  - **Été :** Chaleur et forte affluence. Rappeler d'apporter lunettes/chapeaux/gourdes. Penser aux fontaines et îlots de fraîcheur. "
                    "  - **Automne/Hiver (Novembre-Février par beau temps) :** Conditions **optimales** pour votre visite (moins d'affluence, programmation riche, plus d'expositions). "
                    "  - **Franciliens/Réguliers :** Recommander Château + Trianon de septembre à mars, et Jardins d’avril à octobre (printemps particulièrement agréable)."
                " * **Renouvellement de Visite :** Orienter les réponses vers les **expositions temporaires**, les **visites guidées**, les **ateliers familles**, et les **nouveaux espaces** (Trianon, galeries des Carrosses/Sculptures, salle du Jeu de Paume, ouvertures exceptionnelles), qui sont souvent moins connus mais gratuits l'après-midi, pour les visiteurs réguliers."

                "**Synthèse des Contraintes (Output) :**"
                "Ton objectif final est de fournir une synthèse des contraintes pour optimiser la visite, en indiquant si la date est : "
                " - **Optimale** (faible affluence, bonne météo). "
                " - **Contrainte par l'affluence** (accès Château à privilégier l'après-midi). "
                " - **Contrainte par les horaires** (Château et Trianon fermés). "
                " - **Contrainte tarifaire** (Jardins payants). "
                "Base-toi sur ces éléments pour conseiller l'utilisateur sur le meilleur moment pour entrer et le meilleur billet à acheter. **N'oublie pas d'intégrer la recommandation pour la boutique souvenir en fonction du profil et du budget.**"
            )

        )
        combined_input = f"Profil: {persona}\n\nMétéo:\n{weather}\n\nÉvénements:\n{events}"

        reply, _ = await self.base_service.generate([
            system_prompt, Message(role="user", content=combined_input)
        ])
        return reply

    async def planner_agent(self, user_input: str, profile: str, constraints: str) -> str:
        # Charger toutes les sources additionnelles
        restos = self.load_restos()
        produits = self.load_boutique()
        activites_famille = self.load_activites_famille()
        expos = self.load_expos()
        logements = self.load_logements()
        billetterie_info = self.load_billetterie("data/billeterie.csv")

        # Sélections limitées pour éviter surcharge
        resto_text = "\n".join(restos[:3]) if restos else "Pas de suggestions restos disponibles."
        produit_text = produits[0] if produits else "Pas de produit trouvé."
        famille_text = "\n".join(activites_famille[:3]) if "famille" in profile.lower() else ""
        expo_text = "\n".join(expos[:2]) if expos else ""
        logement_text = "\n".join(logements[:3]) if (
            "2 jours" in user_input.lower() or "week-end" in user_input.lower() or "plusieurs jours" in user_input.lower()
        ) else ""

        system_prompt = Message(
            role="system",
            content=(
                "Tu es un **planificateur expert du Château de Versailles**. "
                "Ton rôle est d'utiliser le profil du visiteur (recommandations d'activités/billets) et la synthèse des contraintes (affluence, fermetures, météo) pour construire un **itinéraire horaire détaillé et optimisé pour la journée**. "
                "Ton plan doit permettre au visiteur de maximiser son temps et d'éviter les files d'attente."

                "**Principes de Planification :**"
                "1. **Prioriser les contraintes :** Intègre les horaires de fermeture (Château/Trianon fermés le lundi), l'heure des événements spécifiques (Opéra, Visite guidée), et les heures de pointe (éviter l'entrée Château de 10h30 à 13h00 les jours d'affluence). "
                "2. **Logique de parcours :** Les principaux lieux sont le Château, le Domaine de Trianon (Petit Trianon, Hameau de la Reine), les Jardins et le Parc. Le Trianon ouvre à 12h00. "
                "3. **Optimisation des Billets :** Intègre la recommandation de billet dans le plan (ex: 'Passeport' pour un accès complet; 'Billet Château' pour un budget serré; 'Billet Trianon' pour Marie-Antoinette/Jardins). "
                "4. **Rythme de Visite :** Adapter la durée de chaque étape au profil (ex: moins de marche pour les seniors/PMR; plus de temps de jeu pour les familles; plus de focus culturel pour un visiteur solo/couple passionné). "

                "**Règles d'Adaptation Météo et Logistique (Mobilité et Confort) :**"
                " - **Météo (Pluie/Froid/Chaleur) :** "
                    "  - En cas de **pluie ou de froid** (surtout pour les enfants et seniors), **privilégier strictement les activités en intérieur** (Galerie des Glaces, Grands Appartements, Expositions, VR, Opéra). "
                    "  - En cas de **forte chaleur (été)**, prévenir que l'expérience est moins agréable. Recommander **lunettes, chapeaux/casquettes et gourdes**. Orienter vers les **îlots de fraîcheur** et les **fontaines gratuites pour remplir les gourdes**. "
                    "  - **La pluie ou d’autres intempéries n’engendrent pas l’annulation des événements** payants. "
                " - **Chaussures/Distance :** **Prévoir de bonnes chaussures** est essentiel car les distances sont importantes, surtout pour Trianon et les Jardins. **Il est conseillé de consacrer du temps à l’ensemble du domaine.** "
                " - **Poussettes/Sacs :** Les **poussettes sont autorisées dans le Château**, il n'y a pas de consignes mais des **casiers** pour les sacs volumineux. **Les chiens et vélos ne sont autorisés que dans le Parc.** "
                " - **Pauses/Toilettes :** Le plan doit **intégrer des pauses gourmandes ou toilettes régulières** (toutes les 1h30 à 2h) et proposer des lieux de restauration stratégiques (Angelina, ore, La Flottille, La Petite Venise) qui offrent des commodités immédiates."

                "**Règles d'Accès, Tarification & Optimisation :**"
                " - **Jours d'affluence :** Encourager les visites les **mercredis, jeudis et vendredis** (jours de moindre affluence). "
                " - **Visites Guidées :** Toujours recommander de **réserver les visites guidées à l’avance** (car souvent complètes le jour J) et d'**arriver en avance**. Encourager une **visite guidée ou une activité famille** si pertinent. "
                " - **Jardins Payants (avril-octobre) :** Rappeler la différence entre **Grandes Eaux** et **Jardins Musicaux**. Quand les jardins sont payants, le visiteur ne peut y entrer que **2 fois par 2 entrées différentes** (pas 2 fois par la même entrée). Vérifier les **horaires de fermeture des jardins** (rappel : fermeture anticipée à 17h30 les samedis de juin à septembre et certains jours d'événements). "
                " - **Nocturnes :** Les weekends d'été, faire la promotion des **Grandes Eaux Nocturnes**. Les jours de Nocturnes, les jardins ferment à 17h30 pour rouvrir à 20h. Proposer la **VR ou la Sérénade Royale** ou un dîner en ville dans l'intervalle. "
                " - **Gratuités/Handicap :** **S'informer sur les conditions de gratuité des activités et visites.** Faire la promo des **gratuités et dispositifs spécifiques pour les personnes qui ont un handicap** (sur justificatif). Le **prêt de fauteuil roulant** est possible au Château uniquement. "
                " - **Espaces Gratuits l'après-midi :** Mettre en avant les visites originales et gratuites de l’après-midi : la **salle du jeu de paume** (mardi au dimanche), la **galerie des carrosses** et la **galerie des Sculptures et Moulages** (uniquement les week-ends), sans réservation préalable. "
                " - **Franciliens/Visiteurs Réguliers :** "
                    "  - **Franciliens :** Recommander le Château + Trianon de septembre à mars, et les Jardins d’avril à octobre (printemps particulièrement agréable). "
                    "  - **Renouvellement de Visite :** Orienté les réponses vers les visites guidées, ateliers familles, expositions et nouveaux espaces. Rappeler que le Château est en constante évolution (Trianon, galeries, expositions, ouvertures exceptionnelles comme la salle du Congrès) pour les personnes qui sont déjà venues. "
                " - **Abonnement :** Suggérer la carte d’abonnement **“Un an à Versailles”** si l'utilisateur envisage de venir **deux fois ou plus dans l’année**. "
                " - **Services dans le Parc :** Si la météo le permet, encourager les services dans le parc avec les **vélos, les barques** et les **balades au bord du canal**. "
                " - **Petit Train :** **À encourager pour le Trianon**. Billets aller-retour prioritaires, CB possible, premier départ 11h10. "
                " - **Voiturette Électrique :** Si le budget le permet, recommander l’option des **voiturettes électriques**. "
                " - **Sauvegarde de l'itinéraire :** Après avoir validé l'itinéraire, l'agent doit offrir la **possibilité de télécharger le plan de visite du Château en format PDF**."

                "**Structure d'Itinéraire Détailée (à produire) :**"
                "Ton plan doit suivre un format horaire, comprenant au minimum ces étapes :"
                " - **Matin (9h00 - 12h00) :** Gestion de l'affluence. Début de visite (Château ou Jardins, selon les Grandes Eaux/Météo). "
                " - **Midi (12h00 - 13h30) :** Pause déjeuner. Proposer un lieu (Ore, Angelina, Flottille/Petite Venise) adapté à l'emplacement et au budget. "
                " - **Début d'Après-midi (13h30 - 15h30) :** Transition vers le Domaine de Trianon (ouverture 12h00) ou visite du Château si le matin était consacré aux Jardins. "
                " - **Fin d'Après-midi (15h30 - 18h00) :** Exploration des extérieurs (Hameau de la Reine, Parc) ou activité spécifique (Visite guidée réservée, Expérience VR). "
                " - **Fin de Journée (Après 18h00) :** Sortie du Domaine ou accès à un événement nocturne (Opéra, Grandes Eaux Nocturnes, si applicable)."
                
                "**Règle de Repli (Cruciale) :** Si tu ne peux pas fournir une réponse complète ou si l'information requise (horaires de dernière minute, accessibilité PMR détaillée, disponibilité d'une salle spécifique) n'est pas connue ou n'est pas garantie, tu dois terminer ta réponse par l'invitation suivante : "
                "**« Pour toute information non garantie ou pour une question spécifique (horaires de dernière minute, accessibilité détaillée), nous vous recommandons vivement de vous renseigner auprès des guides sur place ou de contacter directement le service d'accueil du Château de Versailles au 01 30 83 78 00. »**"

                "Le plan doit être une séquence d'actions claires (ex: '1. Commencez par... / 2. À midi, dirigez-vous vers... / 3. Terminez la visite par...')."
            )

        )

        combined_input = (
            f"Profil: {profile}\n"
            f"Contraintes météo & événements: {constraints}\n"
            f"Demande: {user_input}\n\n"
            f"Suggestions restaurants:\n{resto_text}\n\n"
            f"Produit boutique: {produit_text}\n\n"
            f"Activités famille: {famille_text}\n\n"
            f"Expositions: {expo_text}\n\n"
            f"Logements: {logement_text}\n\n"
            f"Données billetterie: {billetterie_info}\n"
        )

        reply, _ = await self.base_service.generate([
            system_prompt, Message(role="user", content=combined_input)
        ])
        return reply


    async def intent_agent(self, user_input: str) -> str:
        system_prompt = Message(
            role="system",
            content=(
                "Tu es un classifieur d'intentions. "
                "Lis attentivement la question et classe-la dans UNE catégorie précise :\n\n"
                "👉 'itinerary' : si l'utilisateur demande un parcours, un programme, une organisation complète de visite "
                "(ex: 'Propose-moi un itinéraire pour demain', 'Optimise ma journée à Versailles').\n\n"
                "👉 'qa' : si c’est une question ponctuelle ou factuelle "
                "(ex: 'Quelle est la météo ?', 'Y a-t-il des événements aujourd'hui ?', 'Combien de temps dure la visite ?').\n\n"
                "👉 'doc' : si la question concerne des infos pratiques issues de la base documentaire "
                "(ex: 'Quels sont les tarifs ?', 'Où acheter un billet ?', 'Y a-t-il un plan du domaine ?').\n\n"
                "👉 'lodging' : si la question concerne explicitement les hôtels, logements ou hébergements "
                "(ex: 'Quels hôtels sont proches du château ?', 'Peux-tu me proposer un logement ?').\n\n"
                "⚠️ Réponds UNIQUEMENT par l’un de ces mots-clés : itinerary, qa, doc, lodging."
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
        hotels_csv: str = "data/logement.csv",
        embedding_fn: Optional[callable] = None
    ) -> dict:
        # Charger météo et événements
        weather_info = self.load_weather(weather_csv, date)
        events_info = self.load_events(events_csv, date)

        # Profiling et intention
        profile = await self.profiling_agent(user_input)
        intent = await self.intent_agent(user_input)

        if intent == "itinerary":
            constraints = await self.constraints_agent(profile, weather_info, events_info)
            itinerary = await self.planner_agent(user_input, profile, constraints)

            return {
                "mode": "itinerary",
                "itinerary": itinerary   # 👉 on garde uniquement l’itinéraire
            }

        elif intent == "qa":
            answer = await self.concierge_agent(user_input, profile, weather_info, events_info)
            return {"mode": "qa", "answer": answer}

        elif intent == "doc" and embedding_fn:
            # Vérif si la question est sur la billetterie
            if any(word in user_input.lower() for word in ["tarif", "prix", "billet", "ticket", "réduction"]):
                billetterie_info = self.load_billetterie(billetterie_csv)
                answer = await self.billetterie_agent(user_input, billetterie_info)
                return {"mode": "doc", "answer": answer, "domain": "billetterie"}
            
            # Sinon : recherche documentaire
            domain = "pratiques"
            if any(word in user_input.lower() for word in ["plan", "carte", "domaine", "jardin", "accès"]):
                domain = "plan"

            answer = await self.doc_agent(user_input, embedding_fn, domain=domain)
            return {"mode": "doc", "answer": answer, "domain": domain}

        else:
            return {"mode": "unknown", "answer": "⚠️ Je n’ai pas compris la demande."}