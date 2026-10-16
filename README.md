# nextBay Design Tokens

Source unique du design system partagé entre `nextBay_App` et `nextBay_Site` (Tailwind CSS 4, `@theme`) :

- `palette.css` — couleurs brutes (palette numérotée), usage interne aux tokens ;
- `theme.css` — tokens sémantiques (couleurs, polices, espacements, arrondis, tailles de texte, graisses, largeurs, ombres, focus) + reset ;
- `stylelint.config.mjs` — config stylelint partagée qui fait respecter les règles ci-dessous.

## Installation

```bash
npm install github:solution-nextBay/nextBay_DesignTokens#<sha>
```

Toujours épingler un SHA de commit de merge (pas `#main`), voir « Livrer un changement ».

## Usage

Dans le fichier CSS d'entrée du projet (ex. `src/style.css`), après `@import 'tailwindcss';` :

```css
@import 'nextbay-design-tokens/theme.css';
```

`theme.css` importe déjà `palette.css` — pas besoin de l'importer séparément.

## Règles

Ces règles valent pour l'App et le Site, sans exception hors des cas listés en fin de section.
Stylelint (voir plus bas) en vérifie automatiquement la plupart.

### Couleurs

- **Jamais de couleur brute** dans un composant (hex, `rgb()`, `white`…) : uniquement des tokens sémantiques.
- **Jamais de `--color-nextbay-*`** (palette numérotée) hors de ce repo : ces tokens changent de rôle entre jour et nuit (`001` = encre la nuit, surface pâle le jour).
- **Rôle des accents** (décision du 2026-10-15) :

  | Token        | Couleur  | Sert à                                                    |
  | ------------ | -------- | --------------------------------------------------------- |
  | `--accent-4` | orange   | **Actions uniquement** : bouton principal, CTA            |
  | `--accent-1` | sarcelle | Liens, libellés, puces, onglet actif, focus               |
  | `--accent-2` | sauge    | Seul vert de l'interface : parcours client, succès        |
  | `--accent-3` | rouge    | Danger, erreur                                            |

  Le céladon de la palette reste réservé au logo, aux illustrations et aux graphiques (`--data-*`).
  États : `--color-success`, `--color-warning`, `--color-danger`, `--color-info`.

- **Fond d'une boîte = son niveau d'imbrication**, pas une préférence :

  | Niveau                                  | Token         |
  | --------------------------------------- | ------------- |
  | Page                                    | `--bg`        |
  | Carte, panneau, barre posée sur la page | `--surface`   |
  | Carte dans une carte                    | `--surface-2` |
  | Champ de formulaire (effet encastré)    | `--input-bg`  |

  `--input-bg` ne sert qu'aux champs de formulaire, jamais comme fond de section ou de barre.

  Avant de choisir le fond d'une carte, regarder le fond de son parent.

### Typographie

- **Outfit** (`--font-primary`) pour tout le texte. **Syne** (`--font-logo`) seulement pour le logo et le titre des écrans d'authentification.
- Tailles : uniquement `--font-size-*`. Titre de page = `--font-size-2xl` (22 px), partout.
- Graisses : uniquement `--font-weight-*` (400 / 500 / 600 / 700). 800 est réservé au logo.
- **Jamais de `text-align: justify`** : texte aligné à gauche (ou centré pour un titre de section).

### Espacements, arrondis, ombres

- Espacements (`padding`, `margin`, `gap`) : uniquement `--space-*` (grille de 4 px + demi-pas 2 et 6 px). `0` et `auto` restent permis.
- Arrondis : `--radius-sm` (6) / `--radius-md` (8) / `--radius-lg` (12) / `--radius-full` (pilule). Cercle : `50%`.
- Ombres : `--shadow-sm` / `--shadow-md` / `--shadow-lg`. Focus clavier : `box-shadow: var(--focus-ring)`.

### Mise en page

- Sections pleine largeur du Site : contenu centré à `max-width: var(--container)` (1200 px), toutes les sections et le pied de page.
- Texte long (légal, à propos) : `--content-narrow` (720 px). Formulaire dans une page pleine largeur : `--content-form` (560 px).
- Chaque page commence par le même en-tête (`PageHeader` dans l'App).

### Composants

- **Une action = un style** : la même action (ex. « Créer mon garage ») a le même bouton partout où elle apparaît.
- Un seul bouton principal (orange) par zone ; les autres actions sont `secondary` ou `ghost`.
- Boutons, champs et badges passent par les composants partagés de chaque repo (`Button`, `FormInput`, `StatusBadge`…), jamais par du CSS écrit à la main.

### Exceptions

Seulement quand une librairie ou une donnée externe impose la valeur : Stripe Elements, FullCalendar,
couleur du garage (`--tenant-primary`), logo. Toujours avec une justification :

```css
/* stylelint-disable-next-line color-no-hex -- couleur imposée par Stripe Elements */
```

## Stylelint

Dans chaque repo consommateur :

```bash
npm install -D stylelint postcss-html
```

```js
// stylelint.config.mjs
export default {
  extends: ['nextbay-design-tokens/stylelint.config.mjs'],
}
```

```json
// package.json
"lint:css": "stylelint \"src/**/*.{vue,css}\""
```

La config partagée est en `warning` pour permettre une migration progressive. Pour empêcher toute
nouvelle dérive dès le premier jour, la CI lance `stylelint --max-warnings <compte actuel>` et ce
plafond ne fait que baisser, migration après migration. Quand un repo atteint 0, il ajoute
`defaultSeverity: 'error'` à sa config.

## Livrer un changement

1. Branche + PR vers `main` dans ce repo.
2. Merge sur GitHub (« Create a merge commit »).
3. Dans `nextBay_App` et `nextBay_Site` (une PR vers `develop` chacune) :
   ```bash
   npm install github:solution-nextBay/nextBay_DesignTokens#<sha du commit de merge>
   ```
4. Vérifier que `package.json`, `package-lock.json` et `node_modules` pointent sur le même SHA.
