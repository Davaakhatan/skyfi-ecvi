import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import { ToastProvider } from './utils/toast'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import CompanyList from './pages/CompanyList'
import CompanyDetail from './pages/CompanyDetail'

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
            <Route index element={<Dashboard />} />
            <Route path="companies" element={<CompanyList />} />
            <Route path="companies/:id" element={<CompanyDetail />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App

