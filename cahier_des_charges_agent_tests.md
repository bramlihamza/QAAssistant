# Cahier des charges — Agent IA de génération de cas de test fonctionnels

**AIC Formation — Conception Fonctionnelle & Architecture Technique**  
**2026 — Formation GenAI, LLM & Agents IA**

## Exercice 4 — Rédiger le cahier des charges de votre agent

**Durée :** 45 minutes  
**Projet fil rouge :** agent IA de génération de cas de test fonctionnels à partir de user stories et de documentation projet.

---

## 1. Problème métier

| Élément | Votre réponse |
|---|---|
| Processus cible | Rédaction, revue et mise à jour des cas de test fonctionnels à partir des user stories, des critères d’acceptation et de la documentation projet. |
| Volume actuel (h/jour) | 3 à 5 user stories traitées par jour, avec 8 à 20 cas de test potentiels par user story selon la complexité. |
| Temps moyen par occurrence | 45 minutes à 2 heures par user story pour analyser, rédiger et relire les cas de test. |
| Coût actuel estimé | Environ 75 à 200 € par user story, soit 300 à 600 € par jour lorsque QA, PO et développeurs sont mobilisés. |
| Problème principal | Processus manuel, fastidieux et hétérogène : risque d’oubli de scénarios, couverture variable, dépendance à l’expérience des QA/PO, retours tardifs vers les développeurs. |

---

## 2. Objectifs

| Élément | Votre réponse |
|---|---|
| Objectif principal | Mettre à disposition un assistant IA qui propose automatiquement un jeu de cas de test fonctionnels structuré, traçable et révisable à partir d’une user story et de la documentation projet. |
| Gain attendu quantifié | Réduire de 40 % le temps de rédaction initiale des tests ; atteindre au moins 90 % de couverture des critères d’acceptation ; standardiser le format des tests pour faciliter la revue QA. |
| Périmètre inclus | Analyse de user stories, extraction des règles métier, détection d’ambiguïtés, génération de critères d’acceptation complémentaires, génération de cas de test positifs, négatifs et limites, export JSON. |
| Périmètre exclu | Exécution automatisée des tests, tests de performance, sécurité/cybersécurité, tests d’accessibilité avancés, validation finale sans intervention humaine. |

---

## 3. Utilisateurs cibles

| Profil | Rôle | Interaction avec l’agent | Fréquence |
|---|---|---|---|
| Product Owner / Scrum Master | Fournit la vision produit, les user stories et les critères d’acceptation. | Soumet la user story, précise les règles métier, répond aux questions de clarification. | À chaque refinement ou sprint planning. |
| QA / Validation | Prépare, enrichit et valide les scénarios de test. | Génère les cas de test, contrôle la pertinence, ajuste les scénarios et valide le livrable. | Quotidienne pendant la préparation de recette. |
| Développeur | Vérifie la cohérence technique et les comportements attendus. | Consulte les tests proposés pour anticiper les cas limites et clarifier les règles métier. | Régulière, plusieurs fois par user story. |
| Business Analyst / Référent métier | Garantit la conformité aux processus métier. | Valide les règles métier extraites et signale les exceptions non documentées. | Lors des sujets complexes ou transverses. |

---

## 4. Pattern agent

| Élément | Votre réponse |
|---|---|
| Pattern choisi | ReAct. |
| Justification | L’agent doit raisonner sur la user story, rechercher du contexte dans la documentation, identifier les ambiguïtés, produire des cas de test, puis vérifier la cohérence du résultat. Le pattern ReAct est adapté car il alterne raisonnement, actions de recherche et contrôles. Une validation humaine QA reste obligatoire avant usage officiel. |
| Comportement attendu | L’agent commence par analyser la demande, récupère les sources pertinentes, signale les manques, génère les tests au format attendu, puis fournit une synthèse de couverture et les points à valider par l’équipe. |

---

## 5. Entrées et sorties

### Entrées acceptées

| Type d’entrée | Format | Exemple |
|---|---|---|
| User story | JSON via API REST | « En tant qu’utilisateur, je veux réinitialiser mon mot de passe afin de récupérer l’accès à mon compte. » |
| Critères d’acceptation | Texte | « Étant donné un compte existant, quand l’utilisateur demande un lien, alors un email est envoyé. » |
| Documentation projet | PDF, Markdown, texte | Cahier des charges, règles métier, maquettes, glossaire fonctionnel. |
| Cas de test existants | JSON | Exemples validés servant de référence de structure et de niveau de détail. |

### Sorties produites

| Type de sortie | Format | Exemple / contenu attendu |
|---|---|---|
| Cas de test | JSON | `id`, `titre`, `catégorie`, `préconditions`, `étapes`, `données de test fictives`, `résultat attendu`, `priorité`, `user story associée`, statut « à valider ». |
| Rapport de couverture | Texte synthétique | Liste des critères d’acceptation couverts, partiellement couverts ou non couverts. |
| Questions de clarification | Texte | Points ambigus, règles métier absentes, dépendances ou hypothèses à confirmer par le PO/QA. |
| Erreurs / alertes | JSON | Source inaccessible, format non reconnu, données sensibles détectées, documentation insuffisante. |

---

## 6. Architecture — Schéma des 7 couches

| Couche | Contenu pour votre agent |
|---|---|
| 1. Perception / Entrée | Réception d’une user story depuis Jira, fichier texte, Markdown ou formulaire interne. Normalisation du contenu et détection du type de demande. |
| 2. Orchestration | Pipeline : lecture de la user story → extraction des besoins → recherche documentaire → génération des critères d’acceptation manquants → génération des cas de test → contrôle de cohérence → export. |
| 3. Raisonnement LLM | Analyse fonctionnelle, identification des règles métier, détection des ambiguïtés, génération de scénarios positifs, négatifs, limites et exceptions. |
| 4. Mémoire | Court terme : user story analysée, hypothèses, contexte de session. Long terme : documentation projet, règles métier validées, exemples de tests existants, conventions QA. |
| 5. Outils | Recherche documentaire/RAG, accès au référentiel projet, base de cas de test existants, validateur JSON, dictionnaire métier, exporteur CSV/JSON. |
| 6. Contrôle / Gouvernance | Validation humaine obligatoire, traçabilité entre sources et cas de test, contrôle du format de sortie, gestion des hallucinations, exclusion des données sensibles, logs d’usage. |
| 7. Sortie | Cas de test structurés avec `id`, `titre`, `catégorie`, `préconditions`, `étapes`, `données fictives`, `résultat attendu`, `priorité`, `couverture` et statut « à valider ». |

---

## 7. Données nécessaires

| Source | Type | Volume | Qualité actuelle | Action RGPD / gouvernance |
|---|---|---|---|---|
| User stories | Texte / Jira | Faible au départ, puis 3 à 5 par jour. | Variable selon la maturité produit et le niveau de détail des critères. | Interdire les données personnelles réelles ; anonymiser les exemples ; conserver la traçabilité source → test. |
| Documentation projet | Texte, PDF, Confluence, Markdown | Moyen à élevé selon la maturité du projet. | Souvent incomplète ou dispersée ; nécessite une source de vérité. | Restreindre l’accès par rôle ; indexer uniquement les documents autorisés ; historiser les versions utilisées. |
| Cas de test existants | JSON, XLSX, texte | Au moins 20 cas validés pour calibrer le style ; 5 minimum pour un prototype. | Fiables si déjà validés par QA, mais hétérogènes selon les équipes. | Utiliser uniquement des données fictives ou anonymisées ; exclure les exports de production. |
| Règles métier / glossaire | Texte structuré | Moyen. | Critique mais parfois implicite ou non centralisé. | Désigner un propriétaire métier ; valider les règles avant ingestion dans la base documentaire. |
| KPIs et retours QA | Texte / tableur | Faible au démarrage, enrichi à chaque sprint. | Dépend de la discipline de revue et du suivi des corrections. | Stocker des indicateurs agrégés ; éviter les commentaires contenant des informations sensibles. |

---

## 8. KPIs

| KPI | Cible | Méthode de mesure |
|---|---|---|
| KPI 1 : couverture des critères d’acceptation | ≥ 90 % des critères couverts par au moins un cas de test. | Matrice de traçabilité user story → critères → cas de test ; revue QA à chaque sprint. |
| KPI 2 : temps moyen de rédaction initiale | Réduction de 40 % par rapport au processus manuel de référence. | Mesure du temps passé avant/après sur un échantillon de user stories comparables. |
| KPI 3 : taux de retouches majeures QA | < 20 % des cas générés nécessitent une réécriture importante. | Suivi des corrections QA : accepté, modifié légèrement, modifié fortement, rejeté. |
| KPI 4 : taux de tests exploitables au premier passage | ≥ 75 % des cas générés sont directement utilisables après revue rapide. | Évaluation QA sur une grille simple : exploitable / à compléter / non exploitable. |
| KPI 5 : satisfaction des utilisateurs | Score moyen ≥ 4/5 auprès des QA, PO et développeurs pilotes. | Questionnaire court après chaque sprint pilote et collecte des irritants. |

---

## 9. Parties prenantes

| Partie prenante | Rôle dans le projet | Quand l’impliquer |
|---|---|---|
| Métier / Product Owner | Valide les règles métier, les hypothèses et les scénarios critiques. | Dès le cadrage, pendant les refinements et avant validation des livrables QA. |
| QA / Validation | Définit le format cible, valide la qualité des tests et mesure les KPIs. | À toutes les étapes : conception, prototype, pilote et industrialisation. |
| IT / Développement / Architecture | Intègre l’agent aux outils existants, sécurise les accès et garantit la maintenabilité. | Pendant la conception technique, l’intégration Jira/Confluence et la mise en production. |
| Juridique / DPO | Valide les règles RGPD, la politique de conservation et les restrictions sur les données sensibles. | Au cadrage, avant le pilote avec vraies données projet et avant mise en production. |
| Direction / Sponsor | Arbitre budget, priorités, ROI et passage en production. | Au lancement, à la revue du pilote et au go/no-go de généralisation. |

---

## 10. Déploiement, risques et critères d’acceptation du MVP

| Thème | Décision / contenu réaliste |
|---|---|
| MVP proposé | Mode assistant uniquement : l’agent génère des propositions de cas de test, mais aucun test n’est considéré comme validé sans revue QA. Sources limitées aux user stories, critères d’acceptation et documentation projet approuvée. |
| Workflow cible | 1) PO/QA soumet la user story. 2) L’agent recherche le contexte. 3) L’agent génère les tests et signale les ambiguïtés. 4) QA révise et valide. 5) Les cas validés enrichissent la base d’exemples. |
| Planning réaliste | Cadrage : 1 semaine. Prototype : 2 semaines. Pilote sur 10 à 20 user stories : 2 à 3 semaines. Ajustements et gouvernance : 2 semaines. Industrialisation progressive : 1 à 2 mois. |
| Risques principaux | Hallucinations, documentation obsolète, ambiguïtés non détectées, surconfiance des utilisateurs, exposition de données sensibles, formats de sortie non respectés. |
| Mesures de réduction des risques | RAG avec sources citées, statut « à valider » par défaut, validation humaine obligatoire, tests sur jeux de données fictifs, contrôle JSON automatique, journalisation des prompts/réponses, checklist RGPD. |
| Critères d’acceptation du MVP | L’agent génère au moins 8 cas de test pertinents pour une user story simple, couvre les critères fournis, signale les ambiguïtés, produit un JSON valide, n’utilise pas de données de production et permet une revue QA en moins de 15 minutes. |
| Décision go/no-go | Go si les KPIs de couverture, gain de temps et qualité QA sont atteints sur le pilote ; no-go ou itération si les retouches majeures dépassent 30 % ou si les règles de gouvernance ne sont pas respectées. |

---

## Synthèse

L’agent doit être positionné comme un **copilote QA**, non comme un outil de validation automatique. Sa valeur vient de la **standardisation**, de la **traçabilité** et du **gain de temps**, avec une **revue humaine systématique**.