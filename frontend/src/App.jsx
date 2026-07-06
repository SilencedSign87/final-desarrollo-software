import { BrowserRouter, Route, Routes } from "react-router-dom"
import LoginView from "./views/Loginview"
import { AuthProvider } from "./context/AuthContext"
import DashboardRedirect from "./components/DashboardRedirect"
import ProtectedRoute from "./components/ProtectedRoute"
import EstudianteDashboard from "./views/Estudiante/Dashboard"
import DocenteDashboard from "./views/Docente/Dashboard"
import AdministrativoDashboard from "./views/Administrativo/Dashboard"
import EstudianteShell from "./views/Estudiante/EstudianteShell"
import AdministrativoShell from "./views/Administrativo/AdministraticoShell"

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
            path="/estudiante/*"
            element={<ProtectedRoute allowedRoles={['estudiante']}>
              <EstudianteShell />
            </ProtectedRoute>}
          >
            <Route
              path="dashboard"
              element={<EstudianteDashboard />}
            />
          </Route>
          
          <Route
            path="/administrativo/*"
            element={
              <ProtectedRoute allowedRoles={['administrativo']}>
                <AdministrativoShell />
              </ProtectedRoute>
            }
          >
            <Route
              path="dashboard"
              element={<AdministrativoDashboard />}
            />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
