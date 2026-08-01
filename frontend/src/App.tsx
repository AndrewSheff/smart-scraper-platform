// Корневой компонент приложения — роутинг, защищенные маршруты, редиректы
import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import AppLayout from '@/components/layout/AppLayout';
import { Skeleton } from '@/components/ui/skeleton';

// Ленивый импорт страниц — грузим только когда нужно
import LoginPage from '@/pages/LoginPage';
import RegisterPage from '@/pages/RegisterPage';
import ChangePasswordPage from '@/pages/ChangePasswordPage';
import DashboardPage from '@/pages/DashboardPage';
import TasksPage from '@/pages/TasksPage';
import TaskCreatePage from '@/pages/TaskCreatePage';
import TaskDetailPage from '@/pages/TaskDetailPage';
import TaskEditPage from '@/pages/TaskEditPage';
import RunDetailPage from '@/pages/RunDetailPage';
import NotificationsPage from '@/pages/NotificationsPage';
import ExportPage from '@/pages/ExportPage';
import SettingsPage from '@/pages/SettingsPage';
import UsersPage from '@/pages/UsersPage';

// Обертка для защищенных маршрутов — проверяем авторизацию
function ProtectedRoute() {
  const { isAuthenticated, isLoading, user } = useAuth();

  // Пока грузимся, показываем скелетон
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="space-y-4 w-64">
          <Skeleton className="h-8 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </div>
      </div>
    );
  }

  // Не авторизован — на логин
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Нужно сменить пароль — перенаправляем
  if (user?.must_change_password && window.location.pathname !== '/change-password') {
    return <Navigate to="/change-password" replace />;
  }

  return (
    <AppLayout>
      <Outlet />
    </AppLayout>
  );
}

// Обертка для публичных маршрутов — если уже авторизован, кидаем на дашборд
function PublicRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="space-y-4 w-64">
          <Skeleton className="h-8 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}

// Обертка для админских маршрутов
function AdminRoute() {
  const { user } = useAuth();

  if (user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}

function App() {
  return (
    <Routes>
      {/* Публичные маршруты — логин, регистрация */}
      <Route element={<PublicRoute />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      {/* Защищенные маршруты — нужна авторизация */}
      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/tasks" element={<TasksPage />} />
        <Route path="/tasks/new" element={<TaskCreatePage />} />
        <Route path="/tasks/:id" element={<TaskDetailPage />} />
        <Route path="/tasks/:id/edit" element={<TaskEditPage />} />
        <Route path="/runs/:id" element={<RunDetailPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/export" element={<ExportPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/change-password" element={<ChangePasswordPage />} />

        {/* Админские маршруты */}
        <Route element={<AdminRoute />}>
          <Route path="/users" element={<UsersPage />} />
        </Route>
      </Route>

      {/* Корень — редирект на дашборд */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* Все остальное — тоже на дашборд */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
