# Lovable.dev Script: React.js Frontend for UCLA Basketball RAG

## Project Overview
Convert the existing HTML/CSS frontend to React.js and connect it to the Flask backend API. This is a straightforward conversion - replicate the existing UI exactly, no new features.

## Project Setup Instructions

### Step 1: Initialize React Project
```
Create a new React + TypeScript project using Vite
Project name: ucla-basketball-rag-frontend
Template: react-ts
```

### Step 2: Install Dependencies
```bash
npm install axios
npm install @types/react @types/react-dom
```

That's it! Keep it simple - no need for routing, state management libraries, or UI frameworks.

## Component Specifications

### 1. Layout Components

#### Navbar Component (`src/components/Layout/Navbar.tsx`)
```typescript
- Display UCLA logo and branding (same as current HTML)
- Show "Reset Chat" and "Export Data" buttons
- Responsive mobile menu
- Styling: UCLA blue (#003B5C) and gold (#FFD100) gradient
- Include status indicator showing "Online & Ready"
- Import existing CSS: `import '../styles.css'` (copy current CSS file)
```

#### Footer Component (`src/components/Layout/Footer.tsx`)
```typescript
- Copyright notice: "© 2025 UCLA Women's Basketball Analytics"
- Powered by: "Claude AI & Advanced RAG Technology"
- Dark gradient background with gold accents
- Same styling as current footer
```

### 2. Chat Components

#### ChatContainer (`src/components/Chat/ChatContainer.tsx`)
```typescript
- Main chat interface container
- Two-column layout: Sidebar (left) + Chat Area (right)
- Responsive: Sidebar collapses on mobile
- Use React Context for state management
- Auto-scroll to bottom on new messages
- Same layout as current HTML version
```

#### MessageList (`src/components/Chat/MessageList.tsx`)
```typescript
- Display chat messages in chronological order
- Support message types: user, assistant, system, error
- Same styling as current messages
- Simple list rendering (no virtual scrolling needed)
```

#### MessageBubble (`src/components/Chat/MessageBubble.tsx`)
```typescript
Props:
  - type: 'user' | 'assistant' | 'system' | 'error'
  - content: string
  - timestamp: Date
  - tokens?: number

Features:
  - Different styling per message type (same as current)
  - User messages: Blue gradient, right-aligned
  - Assistant messages: White background, left-aligned with robot avatar
  - System messages: Gold background, centered
  - Error messages: Red background with warning icon
  - Show timestamp
  - Basic markdown rendering (bold, italic, line breaks)
```

#### ChatInput (`src/components/Chat/ChatInput.tsx`)
```typescript
Features:
  - Text input with placeholder: "Ask about UCLA women's basketball..."
  - Send button (circular, blue gradient)
  - Suggestion chips below input (same as current)
  - Auto-focus on mount
  - Enter to submit
  - Loading state during API call
  - Same styling as current input
```

#### TypingIndicator (`src/components/Chat/TypingIndicator.tsx`)
```typescript
- Animated three-dot typing indicator
- Text: "AI is analyzing your query..."
- Same animation as current version
```

### 3. Sidebar Components

#### StatsCard (`src/components/Sidebar/StatsCard.tsx`)
```typescript
Display three stat boxes (same as current):
1. Games Analyzed - Shows total games in database
2. Season Average - Shows average points per game
3. AI Tokens - Shows total tokens used in session

Features:
- Auto-update every 30 seconds (same as current)
- Icon for each stat (calendar, trophy, CPU)
- Gradient backgrounds per stat type
- Same styling as current stats card
```

#### QuickActions (`src/components/Sidebar/QuickActions.tsx`)
```typescript
Grid of 6 quick action buttons (same as current):
1. "Leading Scorer" - "Who is the team's leading scorer this season?"
2. "Betts Stats" - "What are Lauren Betts' season statistics?"
3. "Shooting %" - "Show me the team's shooting percentages"
4. "Top Rebounders" - "Who are the top 3 rebounders on the team?"
5. "Assist Leaders" - "Show me assist leaders and their averages"
6. "Best Game" - "What was our highest scoring game this season?"

Features:
- Click to auto-fill and submit query
- Same hover effects and styling
- Responsive grid (2 columns desktop, 1 column mobile)
```

#### RecentQueries (`src/components/Sidebar/RecentQueries.tsx`)
```typescript
- Display last 8 queries from chat history
- Show timestamp and truncated query text
- Click to re-run query
- Scrollable list
- Empty state: "No chat history yet"
- Same styling as current version
```

### 4. Welcome Message Component

#### WelcomeMessage (`src/components/Chat/WelcomeMessage.tsx`)
```typescript
Display on initial load (same as current):
- Title: "🏀 Welcome to UCLA Women's Basketball Analytics!"
- Description: "I'm your AI-powered basketball assistant. Ask me anything about:"
- Feature list with checkmarks:
  * Player statistics and performance
  * Game analysis and results
  * Team comparisons and trends
  * Season highlights and records
- Example queries: "Try asking: 'Who scored the most points against USC?' or 'Compare Rice and Jones' assist numbers'"
- Gold gradient background with blue text
```

## State Management

### Simple Context API (`src/context/AppContext.tsx`)
```typescript
State:
- messages: Message[]
- isLoading: boolean
- error: string | null
- stats: { gamesCount, avgPoints, totalTokens }
- history: HistoryItem[]

Actions:
- sendMessage(query: string): Promise<void>
- clearChat(): void
- loadHistory(): Promise<void>
- fetchStats(): Promise<void>
```

No need for external state management - React Context is sufficient.

## API Service Layer

### API Service (`src/services/api.ts`)
```typescript
Base URL: http://localhost:5001

Endpoints (same as current Flask backend):
1. POST /query
   Body: { query: string }
   Response: { response: string, tokens: number, total_tokens: number }

2. GET /health
   Response: { status: string, database: string, records: number, version: string }

3. GET /stats
   Response: { total_tokens: number, chat_sessions: number, games_in_db: number, players_tracked: number, rag_status: string }

4. GET /history
   Response: Array<{ timestamp: string, query: string, response: string, tokens: number }>

5. POST /clear-chat
   Response: { success: boolean }

Error Handling:
- Network errors: Show user-friendly message in chat
- API errors: Display error message
- Simple error handling (no retry logic needed)
```

## Styling

### Approach
1. **Copy existing CSS file** to `src/styles.css`
2. **Import in main.tsx**: `import './styles.css'`
3. **Use same class names** in React components
4. **No changes to styling** - keep it exactly the same

### Color Palette (from existing CSS)
```css
--ucla-blue: #003B5C
--ucla-gold: #FFD100
--ucla-light-blue: #00A5E5
--primary-gradient: linear-gradient(135deg, #003B5C 0%, #00558C 50%, #00A5E5 100%)
--gold-gradient: linear-gradient(135deg, #FFD100 0%, #FFC107 50%, #FF9800 100%)
```

## Responsive Design

### Breakpoints (same as current)
- Mobile: < 768px (single column, collapsed sidebar)
- Tablet: 768px - 1200px (adjusted grid)
- Desktop: > 1200px (full layout)

### Mobile Behavior (same as current)
- Sidebar collapses or becomes drawer
- Chat input fixed at bottom
- Same responsive behavior as current version

## Implementation Steps

### Step 1: Setup
1. Create React project with Vite
2. Install axios
3. Copy `static/css/style.css` to `src/styles.css`
4. Import CSS in `main.tsx`

### Step 2: Create API Service
1. Create `src/services/api.ts`
2. Implement all 5 endpoints
3. Test with Postman/curl first

### Step 3: Create Context
1. Create `src/context/AppContext.tsx`
2. Set up state and actions
3. Wrap App with Context Provider

### Step 4: Create Components
1. Layout components (Navbar, Footer)
2. Chat components (Container, Messages, Input)
3. Sidebar components (Stats, Quick Actions, Recent Queries)
4. Welcome message component

### Step 5: Connect Everything
1. Connect components to Context
2. Connect Context to API service
3. Test full flow
4. Fix any styling issues

## Backend Requirements

### Flask CORS Setup
Add to `app.py`:

```python
from flask_cors import CORS

app = Flask(__name__)
# Allow React frontend to access API
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
```

For production, update origins to your domain:
```python
CORS(app, resources={r"/*": {"origins": ["https://yourdomain.com"]}})
```

## Testing Checklist

- [ ] Chat interface displays correctly
- [ ] Can send messages and receive responses
- [ ] Sidebar stats display and update
- [ ] Quick action buttons work
- [ ] Recent queries display correctly
- [ ] Clear chat functionality works
- [ ] Responsive design works on mobile
- [ ] All styling matches current version
- [ ] Error handling works (test with backend off)

## Notes for Lovable.dev

- **Keep it simple**: Just convert HTML to React, no new features
- Use TypeScript for type safety
- Use functional components with hooks
- Import existing CSS file (don't rewrite styles)
- Use same class names from current HTML
- Test each component as you build it
- Ensure exact same UI/UX as current version

## What NOT to Add

- ❌ Data visualization/charts
- ❌ Dark mode
- ❌ Export functionality
- ❌ Advanced state management (Redux, Zustand, etc.)
- ❌ UI component libraries (Chakra, Material-UI, etc.)
- ❌ Routing (single page app)
- ❌ Complex animations
- ❌ PWA features
- ❌ WebSocket connections

## What to Keep

- ✅ Exact same UI design
- ✅ Same CSS styling
- ✅ Same functionality
- ✅ Same user experience
- ✅ Same responsive behavior
