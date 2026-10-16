/**
 * Config stylelint partagée nextBay_App + nextBay_Site — fait respecter les règles du README
 * (section « Règles ») au lieu de compter sur la mémoire de chacun.
 *
 * Côté consommateur (stylelint + postcss-html installés en devDependencies) :
 *
 *   // stylelint.config.mjs
 *   export default { extends: ['nextbay-design-tokens/stylelint.config.mjs'] }
 *
 * Sévérité « warning » par défaut, le temps de migrer l'existant. Une fois un repo propre,
 * il passe en bloquant en ajoutant `defaultSeverity: 'error'` dans sa propre config.
 *
 * Vraie exception (Stripe Elements, FullCalendar, couleur du garage --tenant-primary, logo) :
 *   /* stylelint-disable-next-line <règle> -- raison *\/
 */
export default {
  defaultSeverity: 'warning',
  overrides: [{ files: ['**/*.vue', '**/*.html'], customSyntax: 'postcss-html' }],
  rules: {
    // Couleurs : uniquement des tokens sémantiques (--bg, --surface, --text, --accent-*, --color-*).
    'color-no-hex': true,
    'color-named': 'never',
    'function-disallowed-list': ['rgb', 'rgba', 'hsl', 'hsla'],

    'declaration-property-value-disallowed-list': {
      // La palette numérotée change de rôle entre jour et nuit : jamais en direct hors tokens.
      '/.*/': ['/--color-nextbay-/'],
      // Tout le texte est aligné à gauche (ou centré), jamais justifié avec coupure de mots.
      'text-align': ['justify'],
      // Polices : var(--font-primary) / var(--font-logo), ou inherit pour les champs natifs.
      'font-family': ['/^(?!var\\(|inherit)/'],
      // Échelles : une valeur brute = une valeur hors échelle.
      'font-size': ['/\\d(px|rem|em)/'],
      'font-weight': ['/^\\d+$/'],
      'border-radius': ['/[1-9]\\d*(px|rem)/'],
      '/^(gap|row-gap|column-gap|padding|margin)/': ['/(^|\\s)[1-9]\\d*(\\.\\d+)?(px|rem)/'],
      'box-shadow': ['/\\d+px\\s+\\d+px/'],
    },
  },
}
