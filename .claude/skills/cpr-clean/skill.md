# Skill: cpr-clean

Démêle un working tree sale en groupes logiques indépendants, crée une branche propre par groupe,
commite chaque groupe séparément, pousse et ouvre un PR par groupe vers `main`.

Adapté du skill `cpr-clean` de `nextBay_App` pour `nextBay_DesignTokens` (repo de tokens CSS purs,
pas de `develop` ici — la branche de base est `main`).

Idéal quand on a travaillé sur plusieurs sujets en même temps (ex. palette + doc + config) sans
commiter au fur et à mesure.

## Invocation

```
/cpr-clean
```

Pas d'argument. Le skill analyse le contexte et propose le découpage.

## Workflow

### 1. Analyser l'état complet

Exécuter en parallèle :

- `git status --short` — tous les fichiers (staged, unstaged, untracked)
- `git diff` — changements unstaged
- `git diff --cached` — changements stagés
- `git branch --show-current` — branche courante
- `git log --oneline origin/main..HEAD` — commits locaux non encore sur main

Si **rien à traiter** (working tree propre, pas de commits locaux) : informer et stopper.

Si la branche courante est `main` : c'est normal, continuer — /cpr-clean crée lui-même ses
branches depuis `origin/main` à l'étape 5.

### 2. Inventorier tous les changements

Construire la liste complète des fichiers touchés :

- Fichiers modifiés (staged + unstaged) depuis `origin/main`
- Fichiers non-trackés (untracked)
- Commits locaux uniquement si le working tree est propre

Exclure systématiquement : `.env`, `dist/`, `node_modules/`, `*.map`

### 3. Analyser et proposer le découpage

Pour chaque fichier, inférer le domaine (`palette` pour `palette.css`/`palette-basics.css`,
`theme` pour `theme.css`, `docs` pour `README.md`/`CLAUDE.md`, `config` pour `package.json` et
fichiers d'outillage, `claude` pour `.claude/`) et déterminer si les changements sont indépendants
ou couplés.

**Règles de groupement :**

- Changements de tokens de couleur (`palette.css`) et de tokens sémantiques/reset (`theme.css`)
  → même groupe si liés (ex. un nouveau token sémantique qui référence une nouvelle nuance de
  palette), groupes séparés sinon
- Fichiers de config/meta (`package.json`, `.claude/`) → groupe séparé `chore`
- Documentation (`README.md`, `CLAUDE.md`) → groupe séparé `docs`, sauf si elle documente
  directement le changement d'un autre groupe (alors attachée à ce groupe)

Pour chaque groupe, proposer :

- Nom de branche : `feat/`, `fix/`, `chore/`, `docs/` + nom court kebab-case
- Message de commit conventionnel
- Base branch : toujours `origin/main`

**Afficher le plan proposé** :

```
Groupe 1 — feat/success-warning-tokens  [1 fichier]
  - theme.css
  Commit : feat: add semantic state tokens (success/warning/danger/info)

Groupe 2 — docs/readme-update  [1 fichier]
  - README.md
  Commit : docs: document new semantic state tokens

Continuer ? (oui pour procéder, ou donne des corrections)
```

**Attendre la confirmation de l'utilisateur avant de procéder.**
Si l'utilisateur donne des corrections (ex. « met le fichier X dans le groupe 2 »), ajuster et
re-afficher.

### 4. Sauvegarder tout le working tree

```
git stash push -u -m "cpr-clean-work"
```

Le `-u` inclut les fichiers non-trackés. Le working tree est maintenant propre.
Vérifier avec `git status` que tout est bien sauvegardé.

**Si la commande échoue** (ex. rien à stasher) : ajuster selon la situation (peut-être que les
changements sont des commits locaux → passer à l'étape 6 directement).

### 5. Pour chaque groupe (dans l'ordre)

Pour chaque groupe `G` avec ses fichiers `[f1, f2, ...]` et son nom de branche `<branch>` :

#### a. Créer la branche depuis main

```
git checkout -b <branch> origin/main
```

#### b. Extraire les fichiers du groupe depuis le stash

Pour chaque fichier `f` du groupe :

```
git checkout stash@{0} -- <f>
```

#### c. Stager et commiter

```
git add <f1> <f2> ...
git commit -m "<message>

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

#### d. Pusher

```
git push -u origin <branch>
```

#### e. Ouvrir le PR

```
gh pr create --base main --title "<titre>" --body "..."
```

Corps du PR : résumé des changements + note de propagation si `theme.css`/`palette.css` sont
touchés (rappeler que `nextBay_App`/`nextBay_Site` doivent bumper leur pin `#<SHA>` et relancer
`npm install`).

#### f. Revenir à la branche de travail

```
git checkout -
```

### 6. Nettoyer le stash

Une fois tous les groupes traités :

```
git stash drop stash@{0}
```

Si certains fichiers n'ont été assignés à aucun groupe : créer un groupe `misc` ou demander à
l'utilisateur où les mettre avant de dropper le stash.

### 7. Checkout main

Une fois tous les PRs créés, checkout sur la branche main.

### 8. Résumé final

Afficher un tableau :

```
+---------------------------+-------------------------------------------+
| Branche                   | PR                                        |
+---------------------------+-------------------------------------------+
| feat/success-warning...   | https://github.com/.../pull/12            |
| docs/readme-update        | https://github.com/.../pull/13            |
+---------------------------+-------------------------------------------+
```

## Règles

- **Toujours demander confirmation** avant d'exécuter les opérations git (étape 3 → 4)
- Ne jamais modifier les fichiers source pendant l'analyse
- Si `git checkout stash@{0} -- <file>` échoue (fichier nouveau/non-tracké) :
  utiliser `git show stash@{0}:<file>` pour récupérer le contenu et le recréer
- Si un fichier est dans plusieurs groupes logiques : le mettre dans le groupe dominant et le
  signaler à l'utilisateur
- En cas d'échec à mi-parcours : le stash est toujours là (`git stash list`), informer
  l'utilisateur — `git stash pop` pour récupérer son travail
- Ne jamais pusher directement sur `main`
- Si `gh pr create` échoue : afficher la commande brute pour exécution avec `!`

## Gestion des commits locaux (cas avancé)

Si `git log --oneline origin/main..HEAD` montre des commits locaux ET que le working tree est
propre (rien à stasher) :

1. Identifier les fichiers dans ces commits : `git diff origin/main..HEAD --name-only`
2. Utiliser `git cherry-pick` ou rebaser pour réorganiser si nécessaire
3. Proposer le découpage à l'utilisateur avant tout cherry-pick
4. Ce cas est rare — l'indiquer clairement et demander confirmation avant de procéder
