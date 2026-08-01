// Детальная страница запуска — результаты, изменения, AI сводка
import { useParams, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { ArrowLeft, Brain, AlertCircle } from 'lucide-react';
import { useRun } from '@/hooks/useRuns';
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

// Настройки статусов
const statusConfig: Record<string, { label: string; className: string }> = {
  success: { label: 'Успех', className: 'bg-green-500/15 text-green-500' },
  failed: { label: 'Ошибка', className: 'bg-red-500/15 text-red-500' },
  running: { label: 'В работе', className: 'bg-blue-500/15 text-blue-500' },
  pending: { label: 'Ожидание', className: 'bg-yellow-500/15 text-yellow-500' },
  timeout: { label: 'Таймаут', className: 'bg-orange-500/15 text-orange-500' },
};

// Настройки типов изменений
const changeTypeConfig: Record<string, { label: string; className: string }> = {
  added: { label: 'Добавлено', className: 'bg-green-500/15 text-green-500' },
  removed: { label: 'Удалено', className: 'bg-red-500/15 text-red-500' },
  modified: { label: 'Изменено', className: 'bg-yellow-500/15 text-yellow-500' },
};

function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status] || { label: status, className: '' };
  return <Badge className={config.className}>{config.label}</Badge>;
}

function ChangeTypeBadge({ type }: { type: string }) {
  const config = changeTypeConfig[type] || { label: type, className: '' };
  return <Badge className={config.className}>{config.label}</Badge>;
}

export default function RunDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const runId = id || '';

  const { data: run, isLoading } = useRun(runId);

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-40" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (!run) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Запуск не найден</p>
        <Button variant="outline" className="mt-4" onClick={() => navigate(-1)}>
          Назад
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Навигация */}
      <Button variant="ghost" onClick={() => navigate(`/tasks/${run.task_id}`)}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        К задаче
      </Button>

      <h1 className="text-2xl font-bold">Запуск #{run.id}</h1>

      {/* Информация о запуске */}
      <Card>
        <CardHeader>
          <CardTitle>Информация</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Статус</p>
              <StatusBadge status={run.status} />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Начало</p>
              <p className="text-sm">
                {format(new Date(run.started_at), 'dd.MM.yyyy HH:mm:ss', { locale: ru })}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Длительность</p>
              <p className="text-sm">
                {run.duration_ms ? `${(run.duration_ms / 1000).toFixed(1)} сек` : '-'}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Элементов</p>
              <p className="text-sm">{run.items_count}</p>
            </div>
          </div>

          {/* Ошибка, если есть */}
          {run.error_message && (
            <div className="mt-4 p-3 rounded-lg bg-red-500/10 flex items-start gap-2">
              <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
              <p className="text-sm text-red-500">{run.error_message}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* AI сводка — если есть, выделяем красиво */}
      {run.ai_summary && (
        <Card className="border-blue-500/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-blue-500" />
              AI сводка
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm whitespace-pre-wrap">{run.ai_summary}</p>
          </CardContent>
        </Card>
      )}

      {/* Результаты */}
      <Card>
        <CardHeader>
          <CardTitle>Результаты ({run.results.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {run.results.length === 0 ? (
            <p className="text-center text-muted-foreground py-4">
              Нет данных
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Поле</TableHead>
                  <TableHead>Значение</TableHead>
                  <TableHead className="hidden md:table-cell">Индекс</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {run.results.map((result) => (
                  <TableRow key={result.id}>
                    <TableCell className="font-medium">{result.field_name}</TableCell>
                    <TableCell className="max-w-md break-all">
                      {result.field_value || '-'}
                    </TableCell>
                    <TableCell className="hidden md:table-cell text-muted-foreground">
                      {result.field_index}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Изменения — если есть */}
      {run.has_changes && run.changes.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Изменения ({run.changes.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Тип</TableHead>
                  <TableHead>Поле</TableHead>
                  <TableHead>Старое значение</TableHead>
                  <TableHead>Новое значение</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {run.changes.map((change) => (
                  <TableRow key={change.id}>
                    <TableCell>
                      <ChangeTypeBadge type={change.change_type} />
                    </TableCell>
                    <TableCell className="font-medium">{change.field_name}</TableCell>
                    <TableCell className="max-w-xs break-all text-muted-foreground">
                      {change.old_value || '-'}
                    </TableCell>
                    <TableCell className="max-w-xs break-all">
                      {change.new_value || '-'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
