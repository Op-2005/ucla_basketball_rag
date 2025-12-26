# React Frontend Integration Guide

## ✅ Integration Complete!

The React frontend has been successfully integrated with the Flask backend. Here's what was done:

### Changes Made

1. **Flask Backend (`app.py`)**
   - ✅ Added CORS support to allow React frontend to access API
   - ✅ Updated `/stats` endpoint to include `avg_points` calculation
   - ✅ CORS configured for ports: 5173, 3000, 8080

2. **Dependencies (`requirements.txt`)**
   - ✅ Added `flask-cors==4.0.0`

3. **React Frontend**
   - ✅ Updated `AppContext.tsx` to use `avg_points` from API
   - ✅ Updated TypeScript types to include `avg_points` in `StatsResponse`

## 🚀 How to Run

### Step 1: Install Flask Dependencies

```bash
cd ucla-basketball-rag
pip install -r requirements.txt
```

### Step 2: Start Flask Backend

```bash
python app.py
```

The Flask server will start on `http://localhost:5001`

### Step 3: Install React Dependencies

```bash
cd ucla-basketball-chat-main
npm install
```

### Step 4: Start React Frontend

```bash
npm run dev
```

The React app will start on `http://localhost:8080` (or check the terminal for the actual port)

## 🧪 Testing the Integration

1. **Verify Flask Backend is Running**
   - Open `http://localhost:5001/health` in browser
   - Should return: `{"status": "healthy", "database": "connected", ...}`

2. **Verify React Frontend is Running**
   - Open `http://localhost:8080` in browser
   - Should see the UCLA Basketball chat interface

3. **Test Chat Functionality**
   - Type a query like "Who is the leading scorer?"
   - Should receive a response from the RAG pipeline
   - Check browser console for any errors

4. **Test Stats**
   - Sidebar should show:
     - Games Analyzed (from database)
     - Season Average (calculated from team totals)
     - AI Tokens (from session)

5. **Test Quick Actions**
   - Click any quick action button
   - Should auto-fill and send the query
   - Should receive a response

## 📁 Project Structure

```
ucla-basketball-rag/
├── app.py                          # Flask backend (with CORS)
├── requirements.txt                # Python dependencies (includes flask-cors)
├── src/                            # RAG pipeline code
├── data/                           # Database
└── ucla-basketball-chat-main/      # React frontend
    ├── src/
    │   ├── components/             # React components
    │   ├── context/                # AppContext for state
    │   ├── services/               # API service (calls Flask)
    │   └── types/                  # TypeScript types
    └── package.json                # Node dependencies
```

## 🔧 Configuration

### API Endpoint

The React frontend is configured to call the Flask backend at:
- **Development**: `http://localhost:5001`
- **File**: `ucla-basketball-chat-main/src/services/api.ts`

To change the API URL, edit:
```typescript
const API_BASE_URL = 'http://localhost:5001';
```

### CORS Origins

Flask CORS is configured to allow requests from:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (Create React App default)
- `http://localhost:8080` (Vite custom port)

To add more origins, edit `app.py`:
```python
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://localhost:8080", ...],
        ...
    }
})
```

## 🐛 Troubleshooting

### CORS Errors

**Problem**: Browser shows CORS error when React tries to call Flask API

**Solution**: 
- Verify Flask backend is running
- Check that CORS origins include your React dev server port
- Check browser console for specific CORS error message

### API Connection Errors

**Problem**: React shows "Failed to get response" error

**Solution**:
- Verify Flask backend is running on port 5001
- Check `http://localhost:5001/health` in browser
- Verify API_BASE_URL in `api.ts` matches Flask port
- Check Flask terminal for error messages

### Stats Not Updating

**Problem**: Sidebar stats show 0 or don't update

**Solution**:
- Check browser console for API errors
- Verify `/stats` endpoint returns data: `http://localhost:5001/stats`
- Check that database file exists: `data/ucla_wbb.db`

### Port Conflicts

**Problem**: Port already in use

**Solution**:
- Change Flask port in `app.py`: `app.run(..., port=5002)`
- Update React API URL to match new port
- Or change React port in `vite.config.ts`

## 📝 Next Steps

1. **Test all features**:
   - Chat queries
   - Quick actions
   - Stats updates
   - History loading
   - Clear chat

2. **Customize if needed**:
   - Update quick action queries
   - Adjust styling/colors
   - Add new features

3. **Production deployment**:
   - Build React: `npm run build`
   - Configure production API URL
   - Set up proper CORS for production domain
   - Deploy Flask backend
   - Deploy React frontend (or serve from Flask static folder)

## ✨ Features Working

- ✅ Chat interface with message history
- ✅ RAG pipeline integration
- ✅ Sidebar statistics (auto-updates every 30s)
- ✅ Quick action buttons
- ✅ Recent queries sidebar
- ✅ Token counter
- ✅ Error handling
- ✅ Responsive design

## 🎉 Success!

Your React frontend is now fully integrated with the Flask backend. Both servers can run independently and communicate via the REST API.

