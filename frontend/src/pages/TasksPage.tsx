// Список задач — карточки/таблица с поиском, фильтрацией и пагинацией
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import cronstrue from 'cronstrue/i18n';
import {
  Plus,
  Search,
  Play,
  Pause,
  Pencil,
  Trash2,
  Rocket,
  ExternalLink,
} from 'lucide-react';
import { useTasks, useDeleteTask, useToggleTask, useRunTaskNow } from '@/hooks/useTasks';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

// Человекочитаемый крон — обернули чтобы не падало при кривом выражении
function humanCron(cron: string): string {
  try {
    return cronstrue.toString(cron, { locale: 'ru' });
  } catch {
    return cron;
  }
}

export default function TasksPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [activeOnly, setActiveOnly] = useState(false);
  const [page, setPage] = useState(1);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const perPage = 12;

  const { data, isLoading } = useTasks({
    page,
    per_page: perPage,
    search: search || undefined,
    is_active: activeOnly ? true : undefined,
  });

  const deleteMutation = useDeleteTask();
  const toggleMutation = useToggleTask();
  const runNowMutation = useRunTaskNow();

  const totalPages = data ? Math.ceil(data.total / perPage) : 0;

  // Подтверждение удаления задачи
  function handleDelete() {
    if (deleteTarget) {
      deleteMutation.mutate(deleteTarget, {
        onSuccess: () => setDeleteTarget(null),
      });
    }
  }

  return (
    <div className="space-y-6">
      {/* Заголовок и кнопка создания */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Задачи</h1>
        <Button asChild>
          <Link to="/tasks/new">
            <Plus className="mr-2 h-4 w-4" />
            Новая задача
          </Link>
        </Button>
      </div>

      {/* Поиск и фильтр */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Поиск по названию или URL..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="pl-10"
          />
        </div>
        <div className="flex gap-2">
          <Button
            variant={activeOnly ? 'default' : 'outline'}
            size="sm"
            onClick={() => {
              setActiveOnly(!activeOnly);
              setPage(1);
            }}
          >
            Только активные
          </Button>
        </div>
      </div>

      {/* Список задач */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      ) : !data?.items.length ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground text-lg mb-2">Задач пока нет</p>
            <p className="text-sm text-muted-foreground mb-4">
              Создайте первую задачу для скрапинга данных
            </p>
            <Button asChild>
              <Link to="/tasks/new">
                <Plus className="mr-2 h-4 w-4" />
                Создать задачу
              </Link>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.items.map((task) => {
            const successRate =
              task.total_runs > 0
                ? Math.round((task.success_runs / task.total_runs) * 100)
                : 0;

            return (
              <Card
                key={task.id}
                className="hover:border-blue-500/50 transition-colors cursor-pointer"
                onClick={() => navigate(`/tasks/${task.id}`)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-base line-clamp-1">
                      {task.name}
                    </CardTitle>
                    <Badge
                      variant={task.is_active ? 'default' : 'secondary'}
                      className={
                        task.is_active
                          ? 'bg-green-500/15 text-green-500'
                          : 'bg-gray-500/15 text-gray-400'
                      }
                    >
                      {task.is_active ? 'Активна' : 'Пауза'}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  {/* URL задачи — обрезаем длинные */}
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <ExternalLink className="h-3 w-3 shrink-0" />
                    <span className="truncate">{task.url}</span>
                  </div>

                  {/* Расписание */}
                  <p className="text-xs text-muted-foreground">
                    {humanCron(task.schedule_cron)}
                  </p>

                  {/* Статистика */}
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>
                      Запусков: {task.total_runs} | Успех: {successRate}%
                    </span>
                    {task.last_run_at && (
                      <span>
                        {format(new Date(task.last_run_at), 'dd.MM HH:mm', {
                          locale: ru,
                        })}
                      </span>
                    )}
                  </div>

                  {/* Действия — стоп-пропагация чтобы не переходить на детали */}
                  <div
                    className="flex items-center gap-1 pt-2 border-t"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      title="Запустить сейчас"
                      disabled={runNowMutation.isPending}
                      onClick={() => runNowMutation.mutate(task.id)}
                    >
                      <Rocket className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      title={task.is_active ? 'Поставить на паузу' : 'Активировать'}
                      disabled={toggleMutation.isPending}
                      onClick={() => toggleMutation.mutate(task.id)}
                    >
                      {task.is_active ? (
                        <Pause className="h-4 w-4" />
                      ) : (
                        <Play className="h-4 w-4" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      title="Редактировать"
                      onClick={() => navigate(`/tasks/${task.id}/edit`)}
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-red-500 hover:text-red-600"
                      title="Удалить"
                      onClick={() => setDeleteTarget(task.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Пагинация */}
      {totalPages > 1 && (
        <div className="flex justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
          >
            Назад
          </Button>
          <span className="flex items-center text-sm text-muted-foreground px-3">
            {page} / {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => setPage(page + 1)}
          >
            Далее
          </Button>
        </div>
      )}

      {/* Диалог подтверждения удаления */}
      <Dialog open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Удалить задачу?</DialogTitle>
            <DialogDescription>
              Это действие нельзя отменить. Все данные запусков и результаты будут
              удалены.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>
              Отмена
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
            >
              Удалить
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
