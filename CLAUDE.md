# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comportement

@SOUL.md

## Vue d'ensemble

Ce dépôt est la source unique du design system partagé entre `nextBay_App` et `nextBay_Site` (deux projets Tailwind CSS 4 avec `@theme`). Il contient des fichiers CSS de tokens et une config stylelint partagée — pas de code applicatif, pas de build, pas de tests. Les **règles de style** (rôle des accents, fond selon l'imbrication, échelles, exceptions) vivent dans la section « Règles » du `README.md` : toute nouvelle règle s'ajoute là et, si possible, dans `stylelint.config.mjs`.

Il est consommé par les autres repos via un SHA épinglé :
```bash
npm install github:solution-nextBay/nextBay_DesignTokens#<sha du commit de merge>
```

## Workflow de mise à jour

1. Branche + PR vers `main` ici ; merge sur GitHub (« Create a merge commit ») — fait par Marie, le hook de `nextBay_App` bloque le merge vers `main` pour Claude.
2. Dans chaque repo consommateur (`nextBay_App`, `nextBay_Site`), une PR vers `develop` qui épingle le SHA du commit de merge (`npm install github:solution-nextBay/nextBay_DesignTokens#<sha>`).
3. Vérifier que `package.json`, `package-lock.json` et `node_modules` pointent sur le même SHA.

## Architecture des fichiers

- **`palette.css`** — palette de base, un bloc `@theme` Tailwind définissant les couleurs brutes `--color-nextbay-XXX` (001 à 006, plus `-bg` et `-input-bg`), chacune déclinée en nuances `50` à `950` (sauf `600` pour `001`, retiré volontairement). Convention de nommage par familles de couleur : `001` ink black, `002` pine teal, `003` muted teal, `004` celadon, `005` alice blue, `006` tiger orange. C'est le seul fichier qui doit contenir des valeurs de couleur brutes.
- **`theme.css`** — importe `palette.css`, puis définit les tokens sémantiques consommés par les apps (`--bg`, `--surface`, `--surface-2`, `--border`, `--border-2`, `--text`, `--text-muted`, `--accent-1..4`) ainsi que `--font-primary` et un reset CSS minimal (`box-sizing`, `margin`/`padding`, `scroll-behavior`, styles de base `body`/`#app`). C'est le point d'entrée unique documenté dans le README (`@import 'nextbay-design-tokens/theme.css';`) — il ne faut jamais importer `palette.css` séparément côté consommateur.
- **Échelles dans `theme.css`** (`--space-*`, `--radius-*`, `--font-size-*`, `--font-weight-*`, `--container`/`--content-*`, `--shadow-*`, `--focus-ring`, `--font-logo`) — déclarées dans `:root`, **pas** dans `@theme` : les namespaces Tailwind (`--spacing`, `--radius-*`, `--text-*`) changeraient les utilitaires par défaut des consommateurs. Ce ne sont pas des couleurs, donc pas de `light-dark()` ni de report dans le bloc `@supports`.
- **`stylelint.config.mjs`** — config partagée, `extends` côté consommateur. Sévérité `warning` par défaut (migration progressive, plafond `--max-warnings` en CI côté consommateur). Les regex de `declaration-property-value-disallowed-list` sont des chaînes `'/…/'` avec backslashes doublés. Aucune dépendance installée ici : stylelint et `postcss-html` sont des devDependencies des consommateurs. Tester une modification en installant stylelint dans un dossier temporaire et en la lançant sur `nextBay_App/src` et `nextBay_Site/src`.
- **`palette-basics.css`** — fichier de notes/brouillon, non importé nulle part (ni par `theme.css` ni par les repos consommateurs). Il contient des paires de blocs de valeurs (thème sombre puis thème clair) servant de référence lors de la conception d'une variante light de la palette. Ne pas le traiter comme un fichier CSS valide ou actif — c'est un scratchpad de valeurs à reporter manuellement dans `palette.css`/`theme.css` si un thème clair est un jour implémenté.

## Points d'attention

- Certains tokens sémantiques dans `theme.css` référencent directement une nuance précise de `palette.css` (ex. `--accent-2: var(--color-nextbay-002-500)`), d'autres sont des couleurs codées en dur indépendantes de la palette (ex. `--surface`, `--accent-1`, `--accent-3`). Vérifier lequel des deux patterns est utilisé avant de modifier un token, pour ne pas casser le lien avec la palette là où il existe.
- **Modes jour/nuit = une seule déclaration par token** : `--x: light-dark(<jour>, <nuit>);` (jour d'abord). Ne jamais réintroduire de bloc `@media (prefers-color-scheme)` ou `[data-theme='light']` qui redéfinit des couleurs — c'est le `color-scheme` posé dans `theme.css` (piloté par `data-theme`) qui choisit la valeur. Les tokens numérotés (`001`…`006`) changent parfois de rôle entre les deux modes (ex. `001` = encre foncée la nuit, surface pâle le jour) : lire les deux arguments avant de s'en servir comme texte ou fond.
- **Repli vieux navigateurs** : un bloc `@supports not (color: light-dark(#000, #fff))` (fin de `palette.css` et de `theme.css`) redonne les valeurs NUIT en dur aux navigateurs sans `light-dark()` (Tailwind ne le polyfille pas). Toute modification d'une valeur nuit (2e argument d'un `light-dark()`) ou tout nouveau token `light-dark()` doit être reporté dans ce bloc.
- `package.json` n'a ni script `build`, `test`, ni `lint` — rien à exécuter dans ce repo. Tout nouveau fichier destiné aux consommateurs doit être ajouté au tableau `files` de `package.json`.
