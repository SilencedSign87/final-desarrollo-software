import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import LoginView from "./views/Loginview"
import { AuthProvider } from "./context/AuthContext"
import DashboardRedirect from "./components/DashboardRedirect"
import ProtectedRoute from "./components/ProtectedRoute"
import EstudianteDashboard from "./views/Estudiante/Dashboard"
import EstudianteDocumentos from "./views/Estudiante/Documentos"
import DocenteDashboard from "./views/Docente/Dashboard"
import DocenteShell from "./views/Docente/DocenteShell"
import AdministrativoDashboard from "./views/Administrativo/Dashboard"
import AdministrativoDocumentos from "./views/Administrativo/Documentos"
import AdministrativoSeguridad from "./views/Administrativo/Seguridad"
import EstudianteShell from "./views/Estudiante/EstudianteShell"
import AdministrativoShell from "./views/Administrativo/AdministraticoShell"
import DireccionShell from "./views/Direccion/DireccionShell"
import DireccionDashboard from "./views/Direccion/Dashboard"
import DireccionDocumentos from "./views/Direccion/Documentos"
import DireccionAuditorias from "./views/Direccion/Auditorias"
import RegisterView from "./views/RegisterView"
import CursosDocente from "./views/Docente/CursosDocente"
import SeccionesDocente from "./views/Docente/SeccionesDocente"
import NotasDocente from "./views/Docente/NotasDocente"
import EstudianteMatricula from "./views/Estudiante/Matricula"

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Pública */}
          <Route path="/" element={<LoginView />} />
          <Route path="/login" element={<Navigate to="/" />} />
          <Route path="/register" element={<RegisterView />} />
          {/* Redireccion Rol */}
          <Route path="/dashboard" element={<DashboardRedirect />} />
          {/* Rutas protegidas */}

          {/* Estudiante */}
          <Route
            path="/estudiante/*"
            element={
              <ProtectedRoute allowedRoles={['estudiante']}>
                <EstudianteShell />
              </ProtectedRoute>
            }
          >
            <Route path="dashboard" element={<EstudianteDashboard />} />
            <Route path="matricula" element={<EstudianteMatricula />} />
            <Route path="documentos" element={<EstudianteDocumentos />} />
          </Route>

          {/* Docente */}
          <Route
            path="/docente/*"
            element={
              <ProtectedRoute allowedRoles={['docente']}>
                <DocenteShell />
              </ProtectedRoute>
            }
          >
            <Route path="dashboard" element={<DocenteDashboard />} />
            <Route path="cursos" element={<CursosDocente />} />
            <Route path="secciones" element={<SeccionesDocente />} />
            <Route path="notas" element={<NotasDocente />} />
          </Route>

          {/* Administrador */}
          <Route
            path="/administrador/*"
            element={
              <ProtectedRoute allowedRoles={['administrador']}>
                <AdministrativoShell />
              </ProtectedRoute>
            }
          >
            <Route path="dashboard" element={<AdministrativoDashboard />} />
            <Route path="documentos" element={<AdministrativoDocumentos />} />
            <Route path="seguridad" element={<AdministrativoSeguridad />} />
          </Route>

          {/* Director */}
          <Route
            path="/direccion/*"
            element={
              <ProtectedRoute allowedRoles={['direccion']}>
                <DireccionShell />
              </ProtectedRoute>
            }
          >
            <Route path="dashboard" element={<DireccionDashboard />} />
            <Route path="documentos" element={<DireccionDocumentos />} />
            <Route path="auditorias" element={<DireccionAuditorias />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App