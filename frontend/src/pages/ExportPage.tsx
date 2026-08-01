// Страница экспорта данных — выбор задачи, период, скачивание xlsx
import { useState, type FormEvent } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Download, FileSpreadsheet, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { useTasks } from '@/hooks/useTasks';
import { exportTask, exportSummary } from '@/api/export';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export default function ExportPage() {
  const [searchParams] = useSearchParams();
  const initialTaskId = searchParams.get('task_id') || '';

  const [selectedTaskId, setSelectedTaskId] = useState(initialTaskId);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [loading, setLoading] = useState(false);

  // Загружаем список задач для селектора
  const { data: tasksData } = useTasks({ per_page: 100 });

  // Скачивание файла — создаем ссылку и кликаем по ней
  function downloadBlob(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // Обработка экспорта
  async function handleExport(e: FormEvent) {
    e.preventDefault();
    setLoading(true);

    try {
      let blob: Blob;
      let filename: string;

      if (selectedTaskId && selectedTaskId !== 'all') {
        blob = await exportTask(
          selectedTaskId,
          dateFrom || undefined,
          dateTo || undefined,
        );
        const task = tasksData?.items.find((t) => t.id === selectedTaskId);
        filename = `export-${task?.name || selectedTaskId}.xlsx`;
      } else {
        blob = await exportSummary();
        filename = 'export-summary.xlsx';
      }

      downloadBlob(blob, filename);
      toast.success('Файл скачан');
    } catch {
      toast.error('Не удалось скачать экспорт');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Экспорт данных</h1>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileSpreadsheet className="h-5 w-5" />
            Выгрузка в Excel
          </CardTitle>
          <CardDescription>
            Выберите задачу и период для выгрузки результатов в формате XLSX
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleExport} className="space-y-4">
            <div className="space-y-2">
              <Label>Задача</Label>
              <Select value={selectedTaskId} onValueChange={setSelectedTaskId}>
                <SelectTrigger>
                  <SelectValue placeholder="Выберите задачу" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Все задачи (сводка)</SelectItem>
                  {tasksData?.items.map((task) => (
                    <SelectItem key={task.id} value={String(task.id)}>
                      {task.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="dateFrom">Дата начала</Label>
                <Input
                  id="dateFrom"
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="dateTo">Дата конца</Label>
                <Input
                  id="dateTo"
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                />
              </div>
            </div>

            <Button type="submit" disabled={loading}>
              {loading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Download className="mr-2 h-4 w-4" />
              )}
              Скачать XLSX
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Что включено в экспорт</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <ul className="list-disc pl-4 space-y-1">
            <li>Результаты всех запусков за выбранный период</li>
            <li>Значения всех полей для каждого запуска</li>
            <li>Статусы запусков и информация об ошибках</li>
            <li>Обнаруженные изменения данных</li>
            <li>AI-сводки (если включен AI-анализ)</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
