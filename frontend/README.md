# LinkedIn AI Assistant Chrome Extension

A Chrome extension that helps draft responses to LinkedIn messages using AI.

## Project Requirements

### Development Environment
- Node.js >= 18.0.0
- npm >= 9.0.0
- Chrome >= 88.0.0

### Core Dependencies
```json
{
  "@mui/material": "^5.0.0",
  "@mui/icons-material": "^5.0.0",
  "react": "^18.0.0",
  "react-dom": "^18.0.0",
  "typescript": "^5.0.0"
}
```

## Local Development Setup

1. Install dependencies:
```bash
npm install
```

2. Build the extension:
```bash
npm run build
```

3. Load the extension in Chrome:
- Open Chrome and navigate to `chrome://extensions/`
- Enable "Developer mode"
- Click "Load unpacked" and select the `dist` directory

## Coolify Deployment Requirements

### Environment Variables
```env
VITE_API_BASE_URL=https://your-api-url.com
NODE_VERSION=18
```

### Build Configuration
```json
{
  "build_command": "npm run build",
  "install_command": "npm install",
  "output_directory": "dist"
}
```

### Resource Requirements
- Node.js >= 18.0.0
- Minimum 512MB RAM
- 1GB storage space

### Deployment Steps for Coolify

1. Create a new Static Site service in Coolify
2. Configure build settings:
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Node Version: 18
   - Install Command: `npm install`

3. Set environment variables:
   - Add `VITE_API_BASE_URL` pointing to your API

4. Deploy:
   - The static files will be served from the `dist` directory
   - Coolify will handle the build process automatically

### Health Checks
- Build artifacts in `dist/` directory
- Manifest file at `dist/manifest.json`
- Entry points:
  - `dist/sidepanel.html`
  - `dist/background.js`
  - `dist/content-script.js`

## Project Structure

```
src/
├── api/               # API integration layer
├── sidepanel/        # Extension UI components
│   ├── views/        # Main view components
│   │   ├── general/  # General UX components
│   │   └── onboarding/ # Onboarding flow
│   └── main.tsx      # Entry point
├── logic/            # Business logic
└── manifest.json     # Extension manifest
```

## Development Workflow

1. Make changes to source files
2. Run `npm run build` to build the extension
3. Reload the extension in Chrome to test changes

## Production Build

```bash
npm run build
```

This will create a production build in the `dist` directory, optimized for deployment.

## Notes for Deployment

- Ensure all API endpoints are properly configured
- CORS headers must be set up on the API
- SSL certificates must be valid
- Environment variables must be properly set

## Monitoring & Logging

The extension uses Chrome's built-in error reporting. For production monitoring:

1. Set up error boundaries in React components
2. Configure error reporting service
3. Monitor Chrome Web Store metrics
4. Set up API endpoint monitoring

## Security Considerations

- API keys and secrets must be stored securely
- Content Security Policy is enforced
- All API communications use HTTPS
- User data is handled according to privacy policy

## Support

For issues and feature requests, please create an issue in the repository.

# Chrome Extension - Vite + React + TypeScript (using CRXJS)

This project is boilerplate for a Chrome extension built using Vite, React, and TypeScript. It uses the `crxjs/vite-plugin` to simplify the development and build process for Chrome extensions (and otherwise .css had to be injected manually)

Sources used to create this project:
* https://ajaynjain.medium.com/how-i-built-a-chrome-extension-with-react-and-vite-without-crxjs-plugin-b607194c4f5e
* Gemini 2.5
* Lot's of cursing during the previous Chrome plugin I built ;)


## Project Setup

The project was initially based on the Vite `react-ts` template and has been modified to use CRXJS.

```bash
# If starting fresh (optional)
npm init vite@latest . -- --template react-ts
npm install
# Add CRXJS
npm install @crxjs/vite-plugin@beta --save-dev
```

## Development Approach with CRXJS

Building Chrome extensions with modern tools can be tricky. The CRXJS Vite plugin (`@crxjs/vite-plugin`) is used in this project to help solve common problems:

*   **Simplified Builds:** CRXJS uses your `public/manifest.json` to figure out what to build (popups, content scripts, etc.). You generally only need one Vite config file (`vite.config.ts`).
*   **Content Script Loading:** CRXJS automatically handles loading your React content scripts (like `src/overlay/main.tsx`) correctly, so you don't need manual workarounds like dynamic imports.
*   **CSS Handling:** CSS imported directly into your React components (e.g., `import './MyComponent.css'`) should be automatically bundled and injected where needed. This avoids the need for manual CSS injection.
*   **Hot Module Replacement (HMR):** CRXJS provides HMR during development (`npm run dev`) for faster testing.

## Key Configuration Files

*   **`public/manifest.json`:** The core configuration for your Chrome extension. Define your popup, content scripts, permissions, background scripts, etc., here. CRXJS reads this file to determine build inputs.
*   **`vite.config.ts`:** The main Vite configuration file. It includes the `crx({ manifest })` plugin and React plugin configuration.
*   **`package.json`:** Defines project dependencies, metadata (`version`), and build scripts (`build:development`, `build:production`, etc.).

## Application Core Structure

The extension is built on a loosely coupled architecture that separates responsibilities into distinct parts. This makes the codebase easier to maintain, test, and scale.

*   **`src/content/dom-watcher.ts` (The On-Page Coordinator/Watcher):**
    *   This is a [Content Script](https://developer.chrome.com/docs/extensions/mv3/content_scripts/) that runs on LinkedIn messaging pages.
    *   It acts as the on-page coordinator. Its primary job is to intelligently watch the page for the main message container to appear.
    *   Once the container is found, it calls the `html-parser` to extract structured data *directly from the live DOM*.
    *   It then broadcasts the clean, structured data to other parts of the extension (the background script and the side panel).

*   **`src/logic/` (The Core Logic):**
    *   This directory contains the "brains" of the extension, with no dependency on browser-specific APIs.
    *   **`html-parser.ts`:** Responsible for taking a specific DOM element from the LinkedIn page and extracting a clean, structured array of messages from it.
    *   **`linkedin-helpers.ts`:** Contains pure utility functions for formatting dates and generating unique IDs for messages.
    *   **`backend-api.ts`:** Responsible for all communication with your external backend service.

*   **`src/background/index.ts` (The Background Coordinator):**
    *   This is the extension's main background script (Service Worker).
    *   Its role is simple: it listens for the final, structured message data broadcast from the content script and passes it to the `backend-api` to be sent to your server. It does no parsing itself.

*   **`src/sidepanel/` (The UI):**
    *   This contains the React component for the extension's side panel.
    *   It also listens for the structured message data and uses it to render the conversation view in real-time.

## Shadow DOM
To prevent conflicts between our plugin and the host website, we are using a shadowdom. See documentation how we implemented this

## Installing ShadCN and Tailwind for Vite
**IMPORTANT**: Shadcn and Tailwind are not compatible with CRXJS! No longer using this, leaving this in for reference.

## Using MUI
Instead, we are using MUI 
and MUI's sx props for styling
or inline css


## Build Process

The build process uses Vite with the CRXJS plugin and includes steps for versioning, copying, and zipping.

1.  **Versioning:** The `update-manifest` script updates the `version` in `public/manifest.json` to match the `version` in `package.json`.
2.  **TypeScript Check:** `tsc -b` checks for TypeScript errors.
3.  **Vite Build:** `vite build --mode [mode]` runs the build using CRXJS. It outputs the bundled extension files into the `dist/` directory.
4.  **Copy Output:** The `copy:[mode]` script copies the contents of the `dist/` directory to a versioned, mode-specific folder (e.g., `output_folders/dist-development-0.0.1/`). This provides a clean, shareable unpacked extension folder.
5.  **Zipping:** The `zip:[mode]` script creates a zip archive of the copied output folder (e.g., `output_packages/comparisonplugin-react-development-v0.0.1.zip`), ready for distribution or uploading.

**Build Commands:**

*   `npm run build:production` (or `npm run build`): Creates a production build.
*   `npm run build:development`: Creates a development build (with sourcemaps).
*   `npm run build:localhost`: Creates a build configured for localhost (if specific `.env.localhost` settings are needed).

## Loading the Extension

1.  **Build:** Run one of the build commands (e.g., `npm run build:development`).
2.  **Open Chrome Extensions:** Navigate to `chrome://extensions` in Chrome.
3.  **Enable Developer Mode:** Ensure the "Developer mode" toggle is switched on (usually in the top-right corner).
4.  **Load Unpacked:** Click the "Load unpacked" button.
5.  **Select Folder:** Choose the correct output folder from the `output_folders/` directory (e.g., `output_folders/dist-development-0.0.1`).

Remember to reload the extension in Chrome after making changes and rebuilding.

## Environment Variables

You can define environment-specific variables (like API keys or URLs) in `.env.[mode]` files:

*   `.env.development`
*   `.env.production`
*   `.env.localhost`

Variables prefixed with `VITE_` (e.g., `VITE_API_URL`) will be available in your code via `import.meta.env.VITE_API_URL`.

## Adding New Features (Current CRXJS Approach)

CRXJS simplifies adding common extension features:

*   **Popup:** Modify files in `src/popup/`. The entry point (`src/popup/index.html`) is defined in `manifest.json` (`action.default_popup`).
*   **Content Script:** Modify files in `src/overlay/`. The entry point (`src/overlay/main.tsx`) is defined in `manifest.json` (`content_scripts[].js`). Ensure the `matches` property targets the correct pages.
*   **Background Script:**
    1.  Create your script (e.g., `src/background/background.ts`).
    2.  Add a `background` section to `manifest.json` pointing to your script:
        ```json
        "background": {
          "service_worker": "src/background/background.ts",
          "type": "module"
        }
        ```
    CRXJS will automatically detect and build it when you run the build commands.

(Refer to the `README-PROJECT-STRUCTURE.md` for the current file layout.)

## Adding New Features (Manual Multi-Config Approach - Reference Only)

***Note:** The following steps describe the previous manual approach used before CRXJS was integrated. This is kept for reference but is **not** the standard way to add features in the current setup. Use the CRXJS approach described above for new features.*

*   **Popup:** Modify components and logic within the `src/popup/` directory. The main Vite config (`vite.config.ts`) handles this build.
*   **New Content Script (for a different feature):**
    1.  Create a new source directory (e.g., `src/new-feature-script/`).
    2.  Add your React components, main logic (`main.tsx`), and the dynamic import entry script (`content-entry.ts`) inside the new directory.
    3.  Create a new Vite config file (e.g., `vite.new-feature.config.ts`), copying the structure from `vite.content.config.ts`. Update the `rollupOptions.input` paths to point to your new files and ensure `build.emptyOutDir` is `false`. **Ensure this config only includes inputs for this specific new feature.**
    4.  Add the new Vite config to the `build` script in `package.json` (e.g., `... && vite build --config vite.new-feature.config.ts`).
    5.  Add a new entry to the `content_scripts` array in `manifest.json`, pointing its `js` property to the output of your new entry script (e.g., `scripts/new-feature-entry.js`).
    6.  Add the main logic script output (e.g., `scripts/new-feature-main.js`) to the `web_accessible_resources` in `manifest.json`.
    7.  **Double-check:** Ensure the path in your new `content-entry.ts`'s `chrome.runtime.getURL()` call matches the output path defined in `vite.new-feature.config.ts`.
*   **Background Script:**
    1.  Create `src/background/background.ts`.
    2.  Create `vite.background.config.ts` (similar structure, `emptyOutDir: false`, define the background script as the input). **Ensure this config only includes the background script input.**
    3.  Add the build step (`&& vite build --config vite.background.config.ts`) to `package.json`.
    4.  Add the `"background": { "service_worker": "scripts/background.js", "type": "module" }` section to `manifest.json` (adjust path/type as needed).