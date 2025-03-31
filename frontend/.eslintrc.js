module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier'
  ],
  overrides: [{
    files: ["src/app/**/*.{ts,tsx}"],
    excludedFiles: [
    "node_modules/**",
    "dist/**",
    "build/**",
    ".next/**"
  ],
}]
};
