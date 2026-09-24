import { useHashRoute } from './hooks/useHashRoute'
import ProjectDetail from './pages/ProjectDetail'
import ProjectsGallery from './pages/ProjectsGallery'

export default function App() {
  const { route, navigate } = useHashRoute()
  const goHome = () => navigate('/')
  const openProject = (projectId) => navigate(`/projects/${encodeURIComponent(projectId)}`)

  return (
    <div className="h-screen overflow-hidden">
      {route.name === 'detail' ? (
        <ProjectDetail projectId={route.projectId} onNavigateHome={goHome} />
      ) : (
        <ProjectsGallery onOpenProject={openProject} />
      )}
    </div>
  )
}
