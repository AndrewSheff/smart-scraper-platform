// Настройки профиля — имя, email, роль, ссылка на смену пароля
import { useState, useEffect, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { User, Lock, Loader2 } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useUpdateProfile } from '@/hooks/useUsers';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';

export default function SettingsPage() {
  const { user, refreshUser } = useAuth();
  const updateProfile = useUpdateProfile();

  const [name, setName] = useState('');
  const [initialized, setInitialized] = useState(false);

  // Заполняем имя из данных пользователя
  useEffect(() => {
    if (user && !initialized) {
      setName(user.name);
      setInitialized(true);
    }
  }, [user, initialized]);

  // Сохранение профиля
  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    updateProfile.mutate(
      { name },
      { onSuccess: () => refreshUser() },
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Настройки</h1>

      {/* Профиль */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Профиль
          </CardTitle>
          <CardDescription>Основная информация о вашем аккаунте</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Имя</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" value={user?.email || ''} disabled />
              <p className="text-xs text-muted-foreground">Email нельзя изменить</p>
            </div>

            <div className="space-y-2">
              <Label>Роль</Label>
              <div>
                <Badge
                  variant={user?.role === 'admin' ? 'default' : 'secondary'}
                  className={
                    user?.role === 'admin'
                      ? 'bg-purple-500/15 text-purple-500'
                      : ''
                  }
                >
                  {user?.role === 'admin' ? 'Администратор' : 'Пользователь'}
                </Badge>
              </div>
            </div>

            <Button type="submit" disabled={updateProfile.isPending}>
              {updateProfile.isPending && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Сохранить
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Безопасность */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lock className="h-5 w-5" />
            Безопасность
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Separator className="mb-4" />
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Пароль</p>
              <p className="text-sm text-muted-foreground">
                Сменить пароль для входа в систему
              </p>
            </div>
            <Button variant="outline" asChild>
              <Link to="/change-password">Сменить пароль</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
