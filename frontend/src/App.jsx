import { BrowserRouter, Route, Routes } from "react-router-dom"
import LoginView from "./views/Loginview"
import { AuthProvider } from "./context/AuthContext"
import DashboardRedirect from "./components/DashboardRedirect"
import ProtectedRoute from "./components/ProtectedRoute"
import EstudianteDashboard from "./views/Estudiante/Dashboard"
import DocenteDashboard from "./views/Docente/Dashboard"
import AdministrativoDashboard from "./views/Administrativo/Dashboard"

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Pública */}
          <Route path="/" element={<LoginView />} />
          {/* Rediccion Rol */}
          <Route path="/dashboard" element={<DashboardRedirect />} />
          {/* Rutas protegidas */}
           <Route
            path="/estudiante/dashboard"
            element={
              <ProtectedRoute allowedRoles={['estudiante']}>
                <EstudianteDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/docente/dashboard"
            element={
              <ProtectedRoute allowedRoles={['docente']}>
                <DocenteDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/administrativo/dashboard"
            element={
              <ProtectedRoute allowedRoles={['administrativo']}>
                <AdministrativoDashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
