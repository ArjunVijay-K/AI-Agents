/* eslint-env node */
require('@rushstack/eslint-patch/modern-module-resolution');

module.exports = {
  root: true,
  extends: [
    'plugin:vue/vue3-essential',
    'eslint:recommended',
    '@vue/eslint-config-prettier/skip-formatting',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
  },
  rules: {
    'vue/multi-word-component-names': 'off', // Allow single-word component names for views like HomeView.vue
    'vue/no-unused-vars': 'warn',
    'no-unused-vars': 'warn',
    // Add any project specific ESLint rules here
  }
};
