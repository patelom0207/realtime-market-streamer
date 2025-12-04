# Real-Time Market Streamer - React + TypeScript Frontend

Modern React + TypeScript frontend for the Real-Time Market Streamer, featuring WebSocket connectivity and live data visualization.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Backend FastAPI server running on port 8000

### Installation

```bash
cd frontend-react
npm install
```

### Development

```bash
npm run dev
```

The app will be available at **http://localhost:5173**

## 🏗️ Project Structure

```
frontend-react/
├── src/
│   ├── components/          # React components
│   │   ├── Dashboard.tsx    # Main dashboard container
│   │   ├── MetricCard.tsx   # Reusable metric display card
│   │   ├── PriceChart.tsx   # Recharts line chart
│   │   ├── OrderBook.tsx    # Bid/ask order book table
│   │   └── TradesTable.tsx  # Recent trades table
│   ├── hooks/
│   │   └── useMarketData.ts # WebSocket connection hook
│   ├── styles/              # Component-specific CSS
│   ├── utils/
│   │   └── formatters.ts    # Data formatting utilities
│   ├── types.ts             # TypeScript interfaces
│   ├── App.tsx              # Root component
│   └── main.tsx             # Entry point
├── package.json
└── vite.config.ts
```

## 📦 Key Dependencies

- **React 18**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **Recharts**: Charting library
- **Axios**: HTTP client

## 🎯 Features

### Real-Time Data Streaming
- WebSocket connection to FastAPI backend
- Auto-reconnection with 3-second delay
- Real-time updates every 500ms

### Components

#### Dashboard
Main container that orchestrates all sub-components

#### MetricCard
Reusable card component for displaying metrics

#### PriceChart
Interactive line chart using Recharts

#### OrderBook
Order book visualization with top 5 bids and asks

#### TradesTable
Recent trades display with color-coded buy/sell

## 🔧 Configuration

### WebSocket URL
Edit `src/hooks/useMarketData.ts`:
```typescript
const WS_URL = 'ws://localhost:8000/ws/market-data';
```

## 🚀 Running the Full Stack

### Terminal 1: Start Backend
```bash
source venv/bin/activate
export USE_MOCK_DATA=true
python -m uvicorn backend.api_server:app --port 8000
```

### Terminal 2: Start Frontend
```bash
cd frontend-react
npm run dev
```

Then open **http://localhost:5173** in your browser!

---

**Built with ❤️ using React + TypeScript + Vite**
