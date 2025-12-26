# React.js Frontend Migration Plan

## Goal
Convert the existing HTML/CSS frontend to React.js and connect it to the Flask backend API. This is a straightforward frontend conversion - no new features, just a technology change.

## Current Frontend Analysis

### Current Stack
- **Backend**: Flask (Python) with Jinja2 templates
- **Frontend**: Server-side rendered HTML with Bootstrap 5
- **JavaScript**: Inline vanilla JS (no framework)
- **Styling**: Custom CSS with glassmorphism effects
- **API**: RESTful endpoints (`/query`, `/health`, `/stats`, `/history`, `/clear-chat`)

### Current Features (to replicate in React)
1. Chat interface with message history
2. Sidebar with live statistics
3. Quick action buttons
4. Recent queries history
5. Token counter
6. Real-time stats updates
7. Responsive design

## Migration Strategy

### Step 1: Setup React Project
1. **Create React App**
   - Use Vite with React + TypeScript template
   - Project name: `ucla-basketball-rag-frontend`
   - Install basic dependencies only

2. **Project Structure**
   ```
   src/
   ├── components/
   │   ├── Chat/
   │   │   ├── ChatContainer.tsx
   │   │   ├── MessageList.tsx
   │   │   ├── MessageBubble.tsx
   │   │   ├── ChatInput.tsx
   │   │   └── TypingIndicator.tsx
   │   ├── Sidebar/
   │   │   ├── StatsCard.tsx
   │   │   ├── QuickActions.tsx
   │   │   └── RecentQueries.tsx
   │   └── Layout/
   │       ├── Navbar.tsx
   │       └── Footer.tsx
   ├── services/
   │   └── api.ts
   ├── App.tsx
   └── main.tsx
   ```

### Step 2: API Integration
1. **Create API Service**
   - Simple axios-based service for Flask backend
   - Connect to `http://localhost:5001`
   - Handle all existing endpoints: `/query`, `/health`, `/stats`, `/history`, `/clear-chat`

2. **Backend CORS Setup**
   - Add CORS to Flask backend to allow React frontend
   - Simple CORS configuration (no complex setup needed)

### Step 3: Component Conversion
Convert existing HTML/CSS components to React:
- **Navbar**: Same design, React component
- **Footer**: Same design, React component
- **Chat Interface**: Convert chat HTML to React components
- **Sidebar**: Convert sidebar HTML to React components
- **Styling**: Keep existing CSS, import into React components

### Step 4: State Management
- Use React Context API (simple, built-in)
- Manage chat messages, stats, and history state
- No need for external state management libraries

## Technology Stack

### Core (Minimal)
- **React 18+** with TypeScript
- **Vite** for build tooling
- **Axios** for HTTP requests

### Styling
- Keep existing CSS file
- Import CSS into React components
- No need for Tailwind or other CSS frameworks

### Optional (if needed)
- **React Router** (only if adding multiple pages later)

## Backend Modifications

### Flask CORS Setup
Add CORS to allow React frontend to connect:

```python
from flask_cors import CORS

app = Flask(__name__)
# Allow React frontend (running on port 3000) to access API
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
```

That's it! No other backend changes needed.

## Migration Steps

### Step 1: Setup (Day 1)
- Create React project with Vite
- Install axios
- Set up basic project structure
- Copy existing CSS file

### Step 2: API Service (Day 1-2)
- Create API service module
- Implement all 5 endpoints
- Test API connectivity

### Step 3: Components (Day 2-3)
- Convert Navbar to React component
- Convert Footer to React component
- Convert Chat interface to React components
- Convert Sidebar to React components

### Step 4: Integration (Day 3-4)
- Connect components to API
- Implement state management with Context API
- Test full chat flow
- Test sidebar stats updates

### Step 5: Polish (Day 4-5)
- Fix any styling issues
- Test responsive design
- Ensure all features work as before

## What We're NOT Adding

- No data visualization/charts
- No dark mode
- No export functionality
- No advanced filtering
- No WebSocket/real-time features
- No PWA features
- No complex state management libraries
- No additional UI libraries

## What We're Keeping

- Exact same UI/UX as current frontend
- Same styling and colors
- Same functionality
- Same responsive design
- Same user experience

## Estimated Timeline
- **Total Duration**: 4-5 days
- **Team Size**: 1 developer
- **Complexity**: Low to Medium

## Success Criteria

✅ React frontend displays same UI as current HTML version  
✅ All API endpoints connected and working  
✅ Chat functionality works identically  
✅ Sidebar stats update correctly  
✅ Responsive design maintained  
✅ No functionality lost in migration  
