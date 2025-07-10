# AI Interview Prep Agent

This project is an AI-powered mock interview agent designed to help users prepare for job interviews. Users can upload their resume/CV and the job description for a position they are applying for. The agent will then generate tailored interview questions.

## Project Setup

This frontend is built with Vue 3, Vite, Vuetify, Pinia, and Vue Router.

### Prerequisites

*   Node.js (v18.x or later recommended)
*   npm (usually comes with Node.js)

### Installation

1.  **Clone the repository (if applicable):**
    ```bash
    # git clone <repository-url>
    # cd interview-prep-agent
    ```

2.  **Navigate to the `interview-prep-agent` directory (if you created the files manually):**
    ```bash
    cd interview-prep-agent
    ```

3.  **Install dependencies:**
    ```bash
    npm install
    ```

### Development Server

To run the development server:

```bash
npm run dev
```

This will typically start the server on `http://localhost:5173`.

### Build for Production

To build the application for production:

```bash
npm run build
```

The production-ready files will be located in the `dist` directory.

### Linting and Formatting

*   To lint files:
    ```bash
    npm run lint
    ```
*   To format files:
    ```bash
    npm run format
    ```

## Project Structure (Frontend - Vue 3)

*   `public/`: Static assets and `index.html`.
*   `src/`: Main application code.
    *   `assets/`: Static assets like images, fonts (processed by Vite).
    *   `components/`: Reusable Vue components (e.g., `FileUpload.vue`, `QuestionDisplay.vue`). To be created.
    *   `layouts/`: Layout components (e.g., `DefaultLayout.vue`). To be created if needed.
    *   `plugins/`: Vue plugins (e.g., `vuetify.js`, `webfontloader.js`).
    *   `router/`: Vue Router configuration (`index.js`).
    *   `stores/`: Pinia state management stores.
        *   `documentsStore.js`: Manages resume/JD upload, text extraction, and question generation.
        *   `interviewStore.js`: Manages the state of the active mock interview session.
    *   `views/`: Page-level components mapped to routes.
        *   `HomeView.vue`: For uploading resume/JD and displaying generated questions.
        *   `InterviewView.vue`: For conducting the mock interview session.
    *   `App.vue`: The root Vue component.
    *   `main.js`: The application entry point.
*   `.eslintrc.cjs`: ESLint configuration.
*   `.prettierrc.json`: Prettier configuration.
*   `vite.config.js`: Vite configuration.
*   `package.json`: Project dependencies and scripts.

## Next Steps (Backend & AI)

The backend will be a Python application using Flask/FastAPI, Langchain, and a Llama model. It will handle:
*   Resume and job description processing.
*   Interaction with the Llama model for question generation.
*   API endpoints for the frontend to communicate with.

*(Further details on backend setup will be added as that part is developed.)*
