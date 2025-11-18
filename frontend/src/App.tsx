import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import { ToastProvider } from './utils/toast'
import Layout from './components/Layout'
import Login from './pages/Login'

// Lazy load pages for better performance
const Dashboard = lazy(() => import('./pages/Dashboard'))
const CompanyList = lazy(() => import('./pages/CompanyList'))
const CompanyDetail = lazy(() => import('./pages/CompanyDetail'))

// Loading component
function PageLoader() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  )
}

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function App() {
  return (
    <>
      <ToastProvider />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Layout />
              </PrivateRoute>
            }
          >
            <Route
              index
              element={
                <Suspense fallback={<PageLoader />}>
                  <Dashboard />
                </Suspense>
              }
            />
            <Route
              path="companies"
              element={
                <Suspense fallback={<PageLoader />}>
                  <CompanyList />
                </Suspense>
              }
            />
            <Route
              path="companies/:id"
              element={
                <Suspense fallback={<PageLoader />}>
                  <CompanyDetail />
                </Suspense>
              }
            />
          </Route>
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App

