// Дашборд — статистика, графики, последние запуски. Главная страница после логина
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { format, formatDistanceToNow } from 'date-fns';
import { ru } from 'date-fns/locale';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { ListChecks, Activity, CheckCircle2, AlertTriangle } from 'lucide-react';
import { useDashboardStats, useDashboardChart, useRecentRuns } from '@/hooks/useDashboard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

// Цвета для бейджей статусов
const statusConfig: Record<string, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline'; className: string }> = {
  success: { label: 'Успех', variant: 'default', className: 'bg-green-500/15 text-green-500 hover:bg-green-500/25' },
  failed: { label: 'Ошибка', variant: 'destructive', className: 'bg-red-500/15 text-red-500 hover:bg-red-500/25' },
  running: { label: 'В работе', variant: 'default', className: 'bg-blue-500/15 text-blue-500 hover:bg-blue-500/25' },
  pending: { label: 'Ожидание', variant: 'secondary', className: 'bg-yellow-500/15 text-yellow-500 hover:bg-yellow-500/25' },
  timeout: { label: 'Таймаут', variant: 'default', className: 'bg-orange-500/15 text-orange-500 hover:bg-orange-500/25' },
};

// Бейдж статуса запуска
function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status] || { label: status, variant: 'outline' as const, className: '' };
  return (
    <Badge variant={config.variant} className={config.className}>
      {config.label}
    </Badge>
  );
}

export default function DashboardPage() {
  const [chartDays, setChartDays] = useState(7);
  const navigate = useNavigate();

  const { data: stats, isLoading: statsLoading } = useDashboardStats();
  const { data: chartData, isLoading: chartLoading } = useDashboardChart(chartDays);
  const { data: recentRuns, isLoading: runsLoading } = useRecentRuns(10);

  // Карточки статистики — массив для удобного рендера
  const statCards = [
    {
      title: 'Всего задач',
      value: stats?.total_tasks ?? 0,
      icon: ListChecks,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
    },
    {
      title: 'Активных задач',
      value: stats?.active_tasks ?? 0,
      icon: Activity,
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
    },
    {
      title: 'Запусков сегодня',
      value: stats?.runs_today ?? 0,
      icon: CheckCircle2,
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10',
    },
    {
      title: 'Ошибок сегодня',
      value: stats?.errors_today ?? 0,
      icon: AlertTriangle,
      color: 'text-red-500',
      bgColor: 'bg-red-500/10',
    },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Дашборд</h1>

      {/* Карточки статистики */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <Card key={card.title}>
              <CardContent className="pt-6">
                {statsLoading ? (
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-8 w-16" />
                  </div>
                ) : (
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">{card.title}</p>
                      <p className="text-3xl font-bold mt-1">{card.value}</p>
                    </div>
                    <div className={`p-3 rounded-lg ${card.bgColor}`}>
                      <Icon className={`h-6 w-6 ${card.color}`} />
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* График запусков */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Запуски по дням</CardTitle>
            <div className="flex gap-1">
              {[7, 30].map((days) => (
                <Button
                  key={days}
                  variant={chartDays === days ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setChartDays(days)}
                >
                  {days}д
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {chartLoading ? (
            <Skeleton className="h-[300px] w-full" />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData?.data ?? []}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(val) => format(new Date(val), 'dd.MM')}
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={12}
                />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                    color: 'hsl(var(--foreground))',
                  }}
                  labelFormatter={(val) => format(new Date(String(val)), 'dd MMMM yyyy', { locale: ru })}
                />
                <Legend />
                <Bar dataKey="success" name="Успешных" fill="#22c55e" radius={[4, 4, 0, 0]} />
                <Bar dataKey="failed" name="С ошибкой" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {/* Последние запуски */}
      <Card>
        <CardHeader>
          <CardTitle>Последние запуски</CardTitle>
        </CardHeader>
        <CardContent>
          {runsLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : !recentRuns?.items.length ? (
            <p className="text-center text-muted-foreground py-8">
              Пока нет запусков. Создайте задачу и запустите её!
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Задача</TableHead>
                  <TableHead>Статус</TableHead>
                  <TableHead className="hidden md:table-cell">Время</TableHead>
                  <TableHead className="hidden md:table-cell">Длительность</TableHead>
                  <TableHead className="hidden sm:table-cell">Изменения</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentRuns.items.map((run) => (
                  <TableRow
                    key={run.id}
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => navigate(`/runs/${run.id}`)}
                  >
                    <TableCell className="font-medium">
                      {run.task_name || 'Задача'}
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={run.status} />
                    </TableCell>
                    <TableCell className="hidden md:table-cell text-muted-foreground">
                      {formatDistanceToNow(new Date(run.started_at), {
                        addSuffix: true,
                        locale: ru,
                      })}
                    </TableCell>
                    <TableCell className="hidden md:table-cell text-muted-foreground">
                      {run.duration_ms ? `${(run.duration_ms / 1000).toFixed(1)}с` : '-'}
                    </TableCell>
                    <TableCell className="hidden sm:table-cell">
                      {run.has_changes ? (
                        <Badge variant="outline" className="bg-yellow-500/15 text-yellow-500">
                          Есть
                        </Badge>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
