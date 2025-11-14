# Flower Hackathon UI

React + Vite application for the Flower Hackathon project.

## Local Development

1. Install dependencies:
```bash
npm install
```

2. Run the dev server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Build

```bash
npm run build
```

This creates a `dist/` folder with the production build.

## Deployment on Render

The UI is configured for deployment as a static site in the `render.yaml` file at the repository root.

### Deploy via Blueprint (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" and select "Blueprint"
3. Connect your repository
4. Render will deploy both the API and UI together

### Deploy UI Only via Dashboard

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" and select "Static Site"
3. Connect your repository
4. Configure:
   - **Name**: flower-hackathon-ui
   - **Root Directory**: `ui`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
5. Click "Create Static Site"

### Connecting to the API

If you need to call the API from your frontend, set the API URL as an environment variable:

1. In your Render static site settings, add an environment variable:
   - **Key**: `VITE_API_URL`
   - **Value**: Your deployed API URL (e.g., `https://flower-hackathon-api.onrender.com`)

2. Use it in your React code:
```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

### Free Tier Notes

- Static sites on Render's free tier have:
  - Free bandwidth: 100GB/month
  - Automatic SSL certificates
  - Custom domains support
  - CDN included

---

## React + TypeScript + Vite Template Notes

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
