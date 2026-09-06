# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comportement

@SOUL.md

## Vue d'ensemble

Ce dépôt est la source unique du design system partagé entre `nextBay_App` et `nextBay_Site` (deux projets Tailwind CSS 4 avec `@theme`). Il ne contient que des fichiers CSS de tokens — pas de code applicatif, pas de build, pas de tests, pas de linter.

Il est consommé par les autres repos via :
```bash
npm install github:bestrider14/nextBay_DesignTokens#main
```

## Workflow de mise à jour

1. Modifier `palette.css` et/ou `theme.css` ici, commit + push sur `main`.
2. Dans chaque repo consommateur (`nextBay_App`, `nextBay_Site`), lancer `npm update nextbay-design-tokens`.
3. Commit le `package-lock.json` mis à jour dans le repo consommateur.

Il n'y a pas de version publiée sur npm : les consommateurs pointent directement vers la branche `main` du repo GitHub, donc tout push sur `main` a un effet immédiat une fois que les consommateurs font `npm update`.

## Architecture des fichiers

- **`palette.css`** — palette de base, un bloc `@theme` Tailwind définissant les couleurs brutes `--color-nextbay-XXX` (001 à 006, plus `-bg` et `-input-bg`), chacune déclinée en nuances `50` à `950` (sauf `600` pour `001`, retiré volontairement). Convention de nommage par familles de couleur : `001` ink black, `002` pine teal, `003` muted teal, `004` celadon, `005` alice blue, `006` tiger orange. C'est le seul fichier qui doit contenir des valeurs de couleur brutes.
- **`theme.css`** — importe `palette.css`, puis définit les tokens sémantiques consommés par les apps (`--bg`, `--surface`, `--surface-2`, `--border`, `--border-2`, `--text`, `--text-muted`, `--accent-1..4`) ainsi que `--font-primary` et un reset CSS minimal (`box-sizing`, `margin`/`padding`, `scroll-behavior`, styles de base `body`/`#app`). C'est le point d'entrée unique documenté dans le README (`@import 'nextbay-design-tokens/theme.css';`) — il ne faut jamais importer `palette.css` séparément côté consommateur.
- **`palette-basics.css`** — fichier de notes/brouillon, non importé nulle part (ni par `theme.css` ni par les repos consommateurs). Il contient des paires de blocs de valeurs (thème sombre puis thème clair) servant de référence lors de la conception d'une variante light de la palette. Ne pas le traiter comme un fichier CSS valide ou actif — c'est un scratchpad de valeurs à reporter manuellement dans `palette.css`/`theme.css` si un thème clair est un jour implémenté.

## Points d'attention

- Certains tokens sémantiques dans `theme.css` référencent directement une nuance précise de `palette.css` (ex. `--accent-2: var(--color-nextbay-002-500)`), d'autres sont des couleurs codées en dur indépendantes de la palette (ex. `--surface`, `--accent-1`, `--accent-3`). Vérifier lequel des deux patterns est utilisé avant de modifier un token, pour ne pas casser le lien avec la palette là où il existe.
- `package.json` n'a ni script `build`, `test`, ni `lint` — il n'y a rien à exécuter dans ce repo, seulement des fichiers CSS à éditer et publier via git.
