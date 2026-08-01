// Детальная страница задачи — информация, поля, действия и история запусков
import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { format, formatDistanceToNow } from 'date-fns';
import { ru } from 'date-fns/locale';
import cronstrue from 'cronstrue/i18n';
import {
  ArrowLeft,
  Pencil,
  Trash2,
  Rocket,
  Play,
  Pause,
  Download,
  ExternalLink,
} from 'lucide-react';
import { useTask, useDeleteTask, useToggleTask, useRunTaskNow } from '@/hooks/useTasks';
import { useTaskRuns } from '@/hooks/useRuns';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

// Цвета статусов
const statusConfig: Record<string, { label: string; className: string }> = {
  success: { label: 'Успех', className: 'bg-green-500/15 text-green-500' },
  failed: { label: 'Ошибка', className: 'bg-red-500/15 text-red-500' },
  running: { label: 'В работе', className: 'bg-blue-500/15 text-blue-500' },
  pending: { label: 'Ожидание', className: 'bg-yellow-500/15 text-yellow-500' },
  timeout: { label: 'Таймаут', className: 'bg-orange-500/15 text-orange-500' },
};

function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status] || { label: status, className: '' };
  return <Badge className={config.className}>{config.label}</Badge>;
}

// Человекочитаемый крон
function humanCron(cron: string): string {
  try {
    return cronstrue.toString(cron, { locale: 'ru' });
  } catch {
    return cron;
  }
}

export default function TaskDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const taskId = id || '';

  const { data: task, isLoading: taskLoading } = useTask(taskId);
  const [runsPage, setRunsPage] = useState(1);
  const { data: runsData, isLoading: runsLoading } = useTaskRuns(taskId, {
    page: runsPage,
    per_page: 10,
  });
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const deleteMutation = useDeleteTask();
  const toggleMutation = useToggleTask();
  const runNowMutation = useRunTaskNow();

  const totalRunsPages = runsData ? Math.ceil(runsData.total / 10) : 0;

  // Удаление задачи
  function handleDelete() {
    deleteMutation.mutate(taskId, {
      onSuccess: () => navigate('/tasks'),
    });
  }

  if (taskLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!task) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Задача не найдена</p>
        <Button variant="outline" className="mt-4" onClick={() => navigate('/tasks')}>
          К задачам
        </Button>
      </div>
    );
  }

  const successRate =
    task.total_runs > 0
      ? Math.round((task.success_runs / task.total_runs) * 100)
      : 0;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Навигация назад */}
      <Button variant="ghost" onClick={() => navigate('/tasks')}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        К задачам
      </Button>

      {/* Заголовок и действия */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold">{task.name}</h1>
          <Badge
            className={
              task.is_active
                ? 'bg-green-500/15 text-green-500'
                : 'bg-gray-500/15 text-gray-400'
            }
          >
            {task.is_active ? 'Активна' : 'Пауза'}
          </Badge>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => runNowMutation.mutate(taskId)}
            disabled={runNowMutation.isPending}
          >
            <Rocket className="mr-1 h-4 w-4" />
            Запустить
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => toggleMutation.mutate(taskId)}
            disabled={toggleMutation.isPending}
          >
            {task.is_active ? (
              <>
                <Pause className="mr-1 h-4 w-4" /> Пауза
              </>
            ) : (
              <>
                <Play className="mr-1 h-4 w-4" /> Включить
              </>
            )}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(`/tasks/${taskId}/edit`)}
          >
            <Pencil className="mr-1 h-4 w-4" />
            Редактировать
          </Button>
          <Button
            variant="outline"
            size="sm"
            asChild
          >
            <Link to={`/export?task_id=${taskId}`}>
              <Download className="mr-1 h-4 w-4" />
              Экспорт
            </Link>
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={() => setShowDeleteDialog(true)}
          >
            <Trash2 className="mr-1 h-4 w-4" />
            Удалить
          </Button>
        </div>
      </div>

      {/* Информация о задаче */}
      <Card>
        <CardHeader>
          <CardTitle>Информация</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">URL</p>
              <a
                href={task.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 hover:underline flex items-center gap-1 break-all"
              >
                {task.url}
                <ExternalLink className="h-3 w-3 shrink-0" />
              </a>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Расписание</p>
              <p>{humanCron(task.schedule_cron)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Всего запусков</p>
              <p>{task.total_runs}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Успешность</p>
              <p>{successRate}%</p>
            </div>
            {task.last_run_at && (
              <div>
                <p className="text-sm text-muted-foreground">Последний запуск</p>
                <p>
                  {format(new Date(task.last_run_at), 'dd.MM.yyyy HH:mm', { locale: ru })}
                </p>
              </div>
            )}
            {task.description && (
              <div className="md:col-span-2">
                <p className="text-sm text-muted-foreground">Описание</p>
                <p>{task.description}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Поля */}
      <Card>
        <CardHeader>
          <CardTitle>Поля для извлечения</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Название</TableHead>
                <TableHead>Селектор</TableHead>
                <TableHead>Тип</TableHead>
                <TableHead>Список</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {task.fields.map((field) => (
                <TableRow key={field.id}>
                  <TableCell className="font-medium">{field.name}</TableCell>
                  <TableCell className="font-mono text-sm text-muted-foreground">
                    {field.selector}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{field.selector_type}/{field.data_type}</Badge>
                  </TableCell>
                  <TableCell>{field.is_list ? 'Да' : 'Нет'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* История запусков */}
      <Card>
        <CardHeader>
          <CardTitle>История запусков</CardTitle>
        </CardHeader>
        <CardContent>
          {runsLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : !runsData?.items.length ? (
            <p className="text-center text-muted-foreground py-8">
              Запусков пока нет
            </p>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Статус</TableHead>
                    <TableHead>Время</TableHead>
                    <TableHead className="hidden md:table-cell">Длительность</TableHead>
                    <TableHead className="hidden md:table-cell">Элементов</TableHead>
                    <TableHead className="hidden sm:table-cell">Изменения</TableHead>
                    <TableHead className="hidden lg:table-cell">AI сводка</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {runsData.items.map((run) => (
                    <TableRow
                      key={run.id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => navigate(`/runs/${run.id}`)}
                    >
                      <TableCell>
                        <StatusBadge status={run.status} />
                      </TableCell>
                      <TableCell>
                        {formatDistanceToNow(new Date(run.started_at), {
                          addSuffix: true,
                          locale: ru,
                        })}
                      </TableCell>
                      <TableCell className="hidden md:table-cell text-muted-foreground">
                        {run.duration_ms
                          ? `${(run.duration_ms / 1000).toFixed(1)}с`
                          : '-'}
                      </TableCell>
                      <TableCell className="hidden md:table-cell">
                        {run.items_count}
                      </TableCell>
                      <TableCell className="hidden sm:table-cell">
                        {run.has_changes ? (
                          <Badge variant="outline" className="bg-yellow-500/15 text-yellow-500">
                            Есть
                          </Badge>
                        ) : (
                          '-'
                        )}
                      </TableCell>
                      <TableCell className="hidden lg:table-cell max-w-xs truncate text-muted-foreground">
                        {run.ai_summary || '-'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Пагинация запусков */}
              {totalRunsPages > 1 && (
                <div className="flex justify-center gap-2 mt-4">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={runsPage <= 1}
                    onClick={() => setRunsPage(runsPage - 1)}
                  >
                    Назад
                  </Button>
                  <span className="flex items-center text-sm text-muted-foreground px-3">
                    {runsPage} / {totalRunsPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={runsPage >= totalRunsPages}
                    onClick={() => setRunsPage(runsPage + 1)}
                  >
                    Далее
                  </Button>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Диалог подтверждения удаления */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Удалить задачу "{task.name}"?</DialogTitle>
            <DialogDescription>
              Все данные запусков и результаты будут безвозвратно удалены.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
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
