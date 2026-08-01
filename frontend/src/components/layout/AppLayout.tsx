// Основной лейаут приложения — боковая панель + хедер + контент
import { useState, type ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  ListChecks,
  Download,
  Bell,
  Settings,
  Users,
  LogOut,
  Menu,
  X,
  Bug,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

// Навигационные пункты — иконка, текст, путь
const navItems = [
  { icon: LayoutDashboard, label: 'Дашборд', path: '/dashboard' },
  { icon: ListChecks, label: 'Задачи', path: '/tasks' },
  { icon: Download, label: 'Экспорт', path: '/export' },
  { icon: Bell, label: 'Уведомления', path: '/notifications' },
  { icon: Settings, label: 'Настройки', path: '/settings' },
];

// Пункт для админов
const adminItem = { icon: Users, label: 'Пользователи', path: '/users' };

// Получить инициалы из имени пользователя
function getInitials(name: string): string {
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

// Сайдбар с навигацией — используется и в десктопе, и в мобильном sheet
function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const { user } = useAuth();
  const location = useLocation();
  const isAdmin = user?.role === 'admin';

  const allItems = isAdmin ? [...navItems, adminItem] : navItems;

  return (
    <div className="flex flex-col h-full">
      {/* Логотип и название */}
      <div className="flex items-center gap-2 px-4 py-5">
        <Bug className="h-6 w-6 text-blue-400" />
        <span className="text-lg font-bold text-white">Smart Scraper</span>
      </div>

      <Separator className="bg-gray-700" />

      {/* Навигация */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {allItems.map((item) => {
          const isActive =
            location.pathname === item.path ||
            (item.path !== '/dashboard' && location.pathname.startsWith(item.path));
          const Icon = item.icon;
          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={onNavigate}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-600/20 text-blue-400'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800',
              )}
            >
              <Icon className="h-5 w-5 shrink-0" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}

export default function AppLayout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex h-screen bg-background">
      {/* Десктопный сайдбар — скрыт на мобильных */}
      <aside className="hidden lg:flex lg:flex-col w-64 bg-gray-900 border-r border-gray-800 shrink-0">
        <SidebarContent />
      </aside>

      {/* Основной контент */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Верхняя панель */}
        <header className="flex items-center justify-between h-16 px-4 lg:px-6 border-b bg-card">
          {/* Мобильное меню */}
          <div className="lg:hidden">
            <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon">
                  {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-64 p-0 bg-gray-900 border-gray-800">
                <SidebarContent onNavigate={() => setMobileOpen(false)} />
              </SheetContent>
            </Sheet>
          </div>

          {/* Название на десктопе */}
          <div className="hidden lg:block" />

          {/* Пользовательское меню */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex items-center gap-2">
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-blue-600 text-white text-xs">
                    {user ? getInitials(user.name) : '??'}
                  </AvatarFallback>
                </Avatar>
                <span className="hidden sm:inline text-sm font-medium">
                  {user?.name}
                </span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <DropdownMenuItem asChild>
                <Link to="/settings" className="cursor-pointer">
                  <Settings className="mr-2 h-4 w-4" />
                  Настройки
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={logout} className="cursor-pointer text-red-500">
                <LogOut className="mr-2 h-4 w-4" />
                Выйти
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </header>

        {/* Контент страницы */}
        <main className="flex-1 overflow-auto p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
