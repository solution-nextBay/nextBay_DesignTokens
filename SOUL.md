# SOUL.md

Règles de comportement spécifiques à ce repo (`nextBay_DesignTokens`), en plus des préférences globales dans `~/.claude/CLAUDE.md`. À compléter librement par Marie — il suffit de dire « note que... » pendant une session pour que ça soit ajouté ici.

## Git
- Ce repo n'a pas de version npm publiée : les consommateurs pointent sur `#main` ou un SHA précis, donc **tout push sur `main` peut avoir un effet immédiat** dès que `nextBay_App`/`nextBay_Site` font `npm update`/`npm install`. Toujours confirmer avec Marie avant de pousser sur `main`, sauf instruction explicite contraire dans la session.
- Si le repo n'était pas déjà ouvert au démarrage de la session, vérifier `git branch --show-current` et `git status --short` avant la première modification (pas seulement avant de committer).

## Tokens
- Ne jamais introduire de valeur de couleur brute (hex, rgb...) ailleurs que dans `palette.css`.
- Avant de modifier un token sémantique dans `theme.css`, vérifier s'il référence une nuance de `palette.css` (`var(--color-nextbay-XXX-YYY)`) ou s'il est codé en dur — ne pas casser le lien avec la palette là où il existe (voir `CLAUDE.md` § Points d'attention).
- `palette-basics.css` est un brouillon, pas un fichier actif — ne pas le traiter comme importé ou consommé.
