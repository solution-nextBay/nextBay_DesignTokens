# nextBay Design Tokens

Source unique du design system partagé entre `nextBay_App` et `nextBay_Site` (Tailwind CSS 4, `@theme`) : couleurs (`palette.css`) + variables sémantiques, police et reset (`theme.css`).

## Installation

```bash
npm install github:mariecloe28/nextBay_DesignTokens#main
```

## Usage

Dans le fichier CSS d'entrée du projet (ex. `src/style.css`), après `@import 'tailwindcss';` :

```css
@import 'nextbay-design-tokens/theme.css';
```

`theme.css` importe déjà `palette.css` — pas besoin de l'importer séparément. Les imports propres à chaque repo (polices additionnelles, primeicons, etc.) restent avant/après selon le besoin du repo.

## Mettre à jour le design system

1. Modifier `palette.css` et/ou `theme.css` ici, commit + push sur `main`.
2. Dans chaque repo consommateur (`nextBay_App`, `nextBay_Site`) :
   ```bash
   npm update nextbay-design-tokens
   ```
3. Commit le `package-lock.json` mis à jour.
