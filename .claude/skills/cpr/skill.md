# Skill: cpr

Commit + Push + PR en une seule commande.

Adapté du skill `cpr` de `nextBay_App` pour `nextBay_DesignTokens` : pas de suite de tests
Vue/Vitest ici (repo de tokens CSS purs), pas de CI configurée, et une seule branche protégée
(`main` — ce repo n'a pas de `develop`). Les étapes d'analyse post-commit (couverture de tests,
`IMPROVEMENTS.md`, surveillance CI) du skill d'origine ont donc été retirées.

## Invocation

```
/cpr [message optionnel]
```

## Workflow

### 1. Lire l'état git

```bash
python .claude/skills/cpr/scripts/git_state.py state
```

Retourne en un seul appel : branche courante, si elle est protégée, upstream, fichiers modifiés,
diffstat, derniers commits, fichiers à exclure détectés, nom de branche suggéré si protégée.

### 2. Garde-fou branche

Si `is_protected` (branche = `main`) : `git checkout -b <suggested_branch_name> origin/main`.
Afficher : _Branche protégée — `<nom>` créée._

### 3. Stager les fichiers filtrés

```bash
python .claude/skills/cpr/scripts/git_state.py stage
```

Exclut automatiquement `.env`/`*.env`, `dist/`, `node_modules/`, `*.map`, et signale tout fichier
qui ressemble à un secret (clé privée, credentials, service account) sans le stager — à vérifier
manuellement avant de forcer son ajout. Afficher les exclusions si présentes.

### 4. Message de commit

- Argument fourni → l'utiliser tel quel.
- Sinon → `git diff --cached | head -300` pour inférer : `type(scope): description` (anglais
  impératif). Types : `feat` / `fix` / `chore` / `docs` / `style`.

### 5. Commit

```
git commit -m "<message>

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

### 6. Push

```
git push -u origin <branche>
```

### 7. PR

```bash
python .claude/skills/cpr/scripts/git_state.py pr-status
```

- PR existant (`has_pr: true`) → afficher l'URL, terminé.
- Nouveau :
  ```
  gh pr create --base main \
    --title "<1re ligne du commit>" \
    --body "## Summary\n<1-3 bullets>\n\n## Test plan\n- [ ] ...\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)"
  ```

### 8. Checkout + résumé

```
git checkout main
```

Afficher : `<hash court>` — `<PR URL>`

**Rappel propagation** : ce repo est consommé par `nextBay_App` et `nextBay_Site` via un pin
`github:.../nextBay_DesignTokens#<SHA>` dans leur `package.json` — pas un tag semver ni `#main`.
Un changement mergé ici ne prend effet dans ces repos qu'après avoir mis à jour ce SHA et relancé
`npm install nextbay-design-tokens` chez eux. Le signaler dans le résumé final.

## Règles

- Jamais pusher directement sur `main`
- PR existant → ne jamais en créer un nouveau
- Toujours `Co-Authored-By` dans le commit
- Si `gh pr create` échoue → afficher la commande brute pour exécution avec `!`
