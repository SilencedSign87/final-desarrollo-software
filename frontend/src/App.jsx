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
import EstudianteRecordAcademico from "./views/Estudiante/EstudianteRecordAcademico"
import AdministrativoShell from "./views/Administrativo/AdministraticoShell"
import DireccionShell from "./views/Direccion/DireccionShell"
import DireccionDashboard from "./views/Direccion/Dashboard"
import DireccionDocumentos from "./views/Direccion/Documentos"
import DireccionAuditorias from "./views/Direccion/Auditorias"
import DireccionNotas from "./views/Direccion/DireccionNotas"
import AdministrativoRecordAcademico from "./views/Administrativo/AdministrativoRecordAcademico"
import DireccionRecordAcademico from "./views/Direccion/DireccionRecordAcademico"
import RegisterView from "./views/RegisterView"
import CursosDocente from "./views/Docente/CursosDocente"
import SeccionesDocente from "./views/Docente/SeccionesDocente"
import NotasDocente from "./views/Docente/NotasDocente"
import EstudianteMatricula from "./views/Estudiante/Matricula"
import AdministrativoMatricula from "./views/Administrativo/Matricula"
import DireccionMatricula from "./views/Direccion/Matricula"
import NotasEstudiante from "./views/Estudiante/NotasEstudiante"
import NotasAdministrativo from "./views/Administrativo/NotasAdministrativo"
import AdministrativoCursos from "./views/Administrativo/Cursos"
import AdministrativoDocentes from "./views/Administrativo/Docentes"
import AdministrativoSecciones from "./views/Administrativo/Secciones"
import DireccionCargaDocente from "./views/Direccion/CargaDocente"
import CumplimientoPlan from "./views/Direccion/CumplimientoPlan"

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Pública */}
          <Route path="/" element={<LoginView />} />
          <Route path="/login" element={<Navigate to="/" />} />
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
            <Route path="matricula" element={<EstudianteMatricula />} />
            <Route path="record-academico" element={<EstudianteRecordAcademico />} />
            <Route path="documentos" element={<EstudianteDocumentos />} />
            <Route path="notas" element={<NotasEstudiante />} />
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
            <Route path="cursos" element={<CursosDocente />} />
            <Route path="secciones" element={<SeccionesDocente />} />
            <Route path="notas" element={<NotasDocente />} />
            <Route path="*" element={<Navigate to="/docente/cursos" />} />
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
            <Route path="matricula" element={<AdministrativoMatricula />} />
            <Route path="cursos" element={<AdministrativoCursos />} />
            <Route path="notas" element={<NotasAdministrativo />} />
            <Route path="record-academico" element={<AdministrativoRecordAcademico />} />
            <Route path="docentes" element={<AdministrativoDocentes />} />
            <Route path="secciones" element={<AdministrativoSecciones />} />
            <Route path="documentos" element={<AdministrativoDocumentos />} />
            <Route path="seguridad" element={<AdministrativoSeguridad />} />
            <Route path="*" element={<Navigate to="/administrador/matricula" />} />
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
            <Route path="matricula" element={<DireccionMatricula />} />
            <Route path="notas" element={<DireccionNotas />} />
            <Route path="record-academico" element={<DireccionRecordAcademico />} />
            <Route path="carga-docente" element={<DireccionCargaDocente />} />
            <Route path="cumplimiento-plan" element={<CumplimientoPlan />} />
            <Route path="documentos" element={<DireccionDocumentos />} />
            <Route path="auditorias" element={<DireccionAuditorias />} />
            <Route path="*" element={<Navigate to="/direccion/matricula" />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App