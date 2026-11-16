---
name: objection
description: "Tribunal des IA : fait débattre des agents Claude (Défense, Accusation, Juge) sur une question, un fichier ou un artefact, puis rejoue le procès dans la salle d'audience en pixel art. Trigger : /objection, « fais un procès », « tribunal », « fais juger cet artefact »."
argument-hint: "<question, chemin de fichier ou lien d'artefact> [nombre de manches]"
---

# /objection

Tu es le Greffier. Tu organises un procès entre agents Claude indépendants sur l'affaire donnée en argument, tu l'écris dans un fichier, puis tu ouvres la salle d'audience pour que l'utilisateur le regarde.

Tu ne plaides pas et tu ne juges pas toi-même : chaque rôle est un agent séparé, pour que personne ne soit influencé par ton avis.

## 1. Instruire l'affaire

L'argument peut être :

- une question ou une demande (« quelle stack pour telle application ? ») ;
- un ou plusieurs fichiers du projet ;
- un lien d'artefact claude.ai : lis-le avec l'outil Artifact (`action: "read"`), enregistre son contenu dans un fichier du scratchpad et donne ce chemin aux agents.

Formule l'affaire en une phrase courte, c'est le champ `q`. Pour une pièce à juger (fichier, artefact), la question par défaut est : « Cette pièce est-elle bonne telle quelle, et que faut-il changer ? »

S'il n'y a aucun argument, demande l'affaire à l'utilisateur.

### Le règlement du tribunal

Avant tout procès, lis le règlement : ce sont les critères permanents de l'utilisateur (qui il est, ses priorités, ce qu'il ne veut pas). `$SKILL` est défini à la section suivante.

```bash
python3 "$SKILL/greffe.py" reglement
```

S'il existe, cite-le en entier dans la consigne de chaque agent, sous le titre « Règlement du tribunal, écrit par le client ». Les avocats plaident au regard de ces critères et le Juge tranche d'abord selon eux. S'il n'existe pas, tiens le procès sans, et signale en une ligne à la fin qu'un règlement rendrait les verdicts plus personnels.

Si l'utilisateur demande à voir, créer ou changer le règlement (par exemple `/objection règlement`), ne lance pas de procès : montre-lui le fichier indiqué par la commande et modifie-le avec lui. Le fichier `reglement.exemple.md`, à côté, sert de modèle.

## 2. Ouvrir la salle avant les débats

L'utilisateur suit l'audience en direct dans la salle en pixel art : elle affiche qui prépare sa prise de parole, puis joue chaque réplique dès qu'elle est écrite. Il ne doit rien retaper ni cliquer pour que ça démarre.

Le greffe est le script `greffe.py` de ce dossier. Il tient à jour le fichier que la salle relit toutes les 1,5 seconde.

Dans toutes les commandes, `$SKILL` désigne le dossier de base de ce skill, celui que l'invocation indique en tête (« Base directory for this skill »). Remplace-le par ce chemin.

```bash
python3 "$SKILL/greffe.py" start "L'affaire en une phrase"
```

Cette commande crée le procès et ouvre la salle dans le navigateur.

Dis à l'utilisateur en une ligne que la salle est ouverte dans son navigateur (un clic dans la page active le son).

## 3. Tenir l'audience

Deux manches par défaut (l'utilisateur peut en demander de 1 à 5). Ordre des prises de parole : Défense, Accusation, à chaque manche, puis le Juge une seule fois à la fin.

Lance chaque rôle avec l'outil Agent (`subagent_type: "general-purpose"`). Les avocats en `model: "sonnet"`, le Juge sans préciser de modèle. Les prises de parole se suivent : chaque agent a besoin de ce qui a été dit avant lui, donc pas de lancement en parallèle. Pour la deuxième manche et les suivantes, reprends le même agent avec SendMessage en lui donnant la dernière réplique adverse, pour qu'il garde le fil.

Consigne commune à donner à chaque agent, suivie de son rôle :

> Tu joues dans un tribunal comique où des agents débattent pour trouver la meilleure décision. Affaire : {q}. Pièces à lire avant de parler : {chemins, ou « aucune »}. Lis vraiment les pièces et appuie-toi sur des éléments précis. Réponds en français, sans markdown, ton théâtral de prétoire mais arguments réels et concrets. Ta réponse finale est uniquement ta prise de parole, sans introduction ni commentaire. Débats jusqu'ici : {transcription, ou « aucun, tu ouvres l'audience »}.

- **Défense** : « Tu es l'avocat de la Défense. Pour une question, propose une solution concrète à ta première intervention. Pour une pièce, défends ses choix. Tiens ta position contre l'Accusation. 90 mots maximum. »
- **Accusation** : « Tu es le Procureur. Attaque les failles (coût, complexité, risques, défauts concrets) et plaide pour une alternative précise que tu juges meilleure. 90 mots maximum. »
- **Juge** : « Tu es le Juge. Rends le verdict : désigne le gagnant (Défense ou Accusation), justifie en deux phrases, puis écris « Décision : » suivi des étapes concrètes retenues, numérotées en chiffres (1., 2., 3.), une par ligne. 150 mots maximum. » La salle transforme ces lignes numérotées en liste à cocher : si le Juge ne les numérote pas en chiffres, redemande-lui cette forme.

**Dès qu'une réplique arrive, verse-la au greffe avant de lancer l'agent suivant**, sinon la salle reste figée. Le premier argument est l'orateur avec son modèle réel entre parenthèses, le second est le prochain orateur attendu (`Défense`, `Accusation` ou `Juge`). La réplique passe par l'entrée standard, telle que l'agent l'a rendue, sans réécriture ni résumé :

```bash
python3 "$SKILL/greffe.py" add "Défense (Claude Sonnet)" "Accusation" <<'REPLIQUE'
Le texte exact de la réplique.
REPLIQUE
```

Pour le verdict du Juge, ne donne pas de prochain orateur : cela clôt le procès.

```bash
python3 "$SKILL/greffe.py" add "Juge (Claude Fable)" <<'REPLIQUE'
Le verdict.
REPLIQUE
```

Si un agent échoue, relance-le une fois ; s'il échoue encore, clos l'audience avec `python3 "$SKILL/greffe.py" end ko` et explique ce qui s'est passé.

Entre deux prises de parole, n'écris rien de plus qu'une courte ligne dans le terminal : le spectacle est dans la salle.

## 4. Rendre compte

Dans le terminal, donne le verdict du Juge en entier. N'ajoute pas ton propre avis, sauf si l'utilisateur le demande ou si le verdict repose sur une erreur factuelle que tu as vue dans les pièces.

## 5. Appliquer la décision

Un verdict sert à agir. Regarde les étapes numérotées de la décision :

- Si certaines sont des changements que tu peux faire toi-même sur les pièces jugées (modifier un fichier, corriger un artefact), demande à l'utilisateur s'il veut que tu les appliques, en nommant lesquelles. N'applique rien sans son accord.
- Les étapes qui ne dépendent pas de toi (une validation par quelqu'un, un choix à faire) restent à l'utilisateur : dis-le.
- Si la décision ne contient rien que tu puisses appliquer (une simple question de choix, par exemple), ne propose rien.

Après avoir appliqué des étapes, coche-les dans la salle avec leurs numéros, puis dis ce qui est fait et ce qui reste :

```bash
python3 "$SKILL/greffe.py" fait 1 3
```
