# ECVI Frontend

Modern, minimalist frontend for Enterprise Company Verification Intelligence built with React, TypeScript, and Tailwind CSS.

## Features

- 🎨 **Minimalist Design** - Clean, uncluttered interface following latest UI/UX best practices
- 📱 **Responsive** - Works seamlessly on desktop, tablet, and mobile devices
- ⚡ **Fast** - Built with Vite for lightning-fast development and production builds
- 🔒 **Secure** - JWT-based authentication with secure token storage
- ♿ **Accessible** - WCAG 2.1 Level AA compliant with keyboard navigation and screen reader support

## Tech Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Vite** - Next-generation build tool
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Zustand** - Lightweight state management
- **Axios** - HTTP client
- **Lucide React** - Beautiful icon library
- **React Hot Toast** - Elegant toast notifications

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The app will be available at `http://localhost:5173`

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── Layout.tsx
│   │   └── RiskScoreBadge.tsx
│   ├── pages/          # Page components
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── CompanyList.tsx
│   │   └── CompanyDetail.tsx
│   ├── services/       # API services
│   │   └── api.ts
│   ├── store/          # State management
│   │   └── authStore.ts
│   ├── utils/          # Utility functions
│   │   └── toast.tsx
│   ├── App.tsx         # Main app component
│   ├── main.tsx        # Entry point
│   └── index.css       # Global styles
├── public/             # Static assets
├── index.html          # HTML template
└── package.json        # Dependencies
```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

## Development

The frontend is configured to proxy API requests to the backend running on `http://localhost:8000`. Make sure the backend is running before starting the frontend.

## Building for Production

```bash
npm run build
```

The production build will be in the `dist/` directory, ready to be deployed to any static hosting service.

## Design Principles

- **Minimalist** - Clean, uncluttered interface with plenty of white space
- **User-Friendly** - Intuitive navigation and clear visual hierarchy
- **Accessible** - WCAG 2.1 Level AA compliant
- **Responsive** - Mobile-first design that works on all screen sizes
- **Fast** - Optimized for performance with code splitting and lazy loading

