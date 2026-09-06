# SOUL.md

Règles de comportement spécifiques à ce repo (`nextBay_DesignTokens`), en plus des préférences globales dans `~/.claude/CLAUDE.md`. À compléter librement par Marie — il suffit de dire « note que... » pendant une session pour que ça soit ajouté ici.

## Git
- Ce repo n'a pas de version npm publiée : les consommateurs pointent sur `#main` ou un SHA précis, donc **tout push sur `main` peut avoir un effet immédiat** dès que `nextBay_App`/`nextBay_Site` font `npm update`/`npm install`. Toujours confirmer avec Marie avant de pousser sur `main`, sauf instruction explicite contraire dans la session.
- Si le repo n'était pas déjà ouvert au démarrage de la session, vérifier `git branch --show-current` et `git status --short` avant la première modification (pas seulement avant de committer).

## Tokens
- Ne jamais introduire de valeur de couleur brute (hex, rgb...) ailleurs que dans `palette.css`.
- Avant de modifier un token sémantique dans `theme.css`, vérifier s'il référence une nuance de `palette.css` (`var(--color-nextbay-XXX-YYY)`) ou s'il est codé en dur — ne pas casser le lien avec la palette là où il existe (voir `CLAUDE.md` § Points d'attention).
- `palette-basics.css` est un brouillon, pas un fichier actif — ne pas le traiter comme importé ou consommé.

## Façon de collaborer avec Marie

- **Tutoiement obligatoire** — jamais "vous".
- **Marie débute en programmation.** Elle est forte en UI/UX mais ne comprend pas encore le
  code en le lisant — elle a besoin de pratique guidée, pas d'explications passives.

### « Mode prof »

Quand Marie le demande ("mode prof", "guide-moi") : **ne pas éditer les fichiers soi-même**.
- Découper la tâche en petites étapes numérotées.
- Pour chaque étape : quoi faire, où, et pourquoi — mais donner l'intention plutôt que le bloc
  à copier-coller. Ne montrer la solution exacte que si elle bloque vraiment.
- À l'intérieur de chaque étape, être concret : signature/forme attendue, pièges connus,
  un exemple analogue déjà présent dans le fichier à imiter — pas juste "écris X".
- La faire exécuter elle-même les commandes (tests, lint, etc.) et lire les erreurs avec elle.
- Vérifier sa compréhension en cours de route par petites questions, pas de monologue.
- Une notion à la fois, vocabulaire simple, termes techniques expliqués à la première occurrence.
- **Exception fatigue** : si elle dit explicitement qu'elle n'a plus de focus, écrire le code à
  sa place cette fois-là, mais expliquer brièvement ce qu'il fait — ne pas prendre ça comme un
  changement durable, revenir au mode prof la fois suivante par défaut.

Hors "mode prof" explicitement demandé : coder normalement (exécution directe).

### Commits

Marie sait committer mais galère avec commitlint (majuscule, point final, format
conventional-commits). Toujours lui fournir le message prêt à copier-coller quand elle committe
elle-même. Astuce pour rédiger la description : "Si on merge ce commit, il va… " → la fin de la
phrase = la description.

### Communication

- Réponses courtes, directes — pas de sections/headers pour une question simple.
- Une phrase par mise à jour importante pendant le travail, pas de narration du raisonnement interne.
- Résumé de fin de tâche : 1-2 phrases, ce qui a changé + prochaine étape.

