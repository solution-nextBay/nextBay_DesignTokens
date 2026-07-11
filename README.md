# nextBay Design Tokens

Source unique des couleurs partagées entre `nextBay_App` et `nextBay_Site` (Tailwind CSS 4, `@theme`).

## Installation

```bash
npm install github:mariecloe28/nextBay_DesignTokens#main
```

## Usage

Dans le fichier CSS d'entrée du projet (ex. `src/style.css`), remplacer l'import local de `palette.css` par :

```css
@import 'nextbay-design-tokens/palette.css';
```

## Mettre à jour une couleur

1. Modifier `palette.css` ici, commit + push sur `main`.
2. Dans chaque repo consommateur (`nextBay_App`, `nextBay_Site`) :
   ```bash
   npm update nextbay-design-tokens
   ```
3. Commit le `package-lock.json` mis à jour.
