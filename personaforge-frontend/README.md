# PersonaForge AI Frontend

This is the React frontend for PersonaForge AI.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the development server:
   ```bash
   npm run dev
   ```
   The app will be available at http://localhost:5173 (or next available port).

## Usage
- Enter a Reddit username or profile URL to analyze.
- View the AI-generated persona dashboard and download the PDF report.

## Notes
- **No API keys are required in the frontend.** All API keys are managed in the backend.
- The frontend communicates with the backend at `http://localhost:8080` by default.

## Build for Production
```bash
npm run build
```

## License
MIT 