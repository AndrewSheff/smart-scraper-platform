// Создание задачи — большая форма с динамическими полями, превью и всякими настройками
import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import cronstrue from 'cronstrue/i18n';
import { Plus, Trash2, Eye, Loader2, ArrowLeft } from 'lucide-react';
import { useCreateTask, usePreviewTask } from '@/hooks/useTasks';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import type { TaskFieldCreate } from '@/api/types';

// Пустое поле — шаблон для добавления новых
function emptyField(): TaskFieldCreate {
  return {
    name: '',
    selector: '',
    selector_type: 'css',
    data_type: 'text',
    is_list: false,
    attribute: '',
  };
}

// Человекочитаемый крон
function humanCron(cron: string): string {
  try {
    return cronstrue.toString(cron, { locale: 'ru' });
  } catch {
    return '';
  }
}

export default function TaskCreatePage() {
  const navigate = useNavigate();
  const createMutation = useCreateTask();
  const previewMutation = usePreviewTask();

  // Основные поля формы
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [description, setDescription] = useState('');
  const [scheduleCron, setScheduleCron] = useState('0 */6 * * *');
  const [timeoutSeconds, setTimeoutSeconds] = useState(30);
  const [maxRetries, setMaxRetries] = useState(3);
  const [notifyOnChange, setNotifyOnChange] = useState(true);
  const [notifyOnError, setNotifyOnError] = useState(true);
  const [aiPrompt, setAiPrompt] = useState('');
  const [headersJson, setHeadersJson] = useState('');
  const [fields, setFields] = useState<TaskFieldCreate[]>([emptyField()]);
  const [showPreview, setShowPreview] = useState(false);

  // Добавить поле
  function addField() {
    setFields([...fields, emptyField()]);
  }

  // Удалить поле
  function removeField(index: number) {
    setFields(fields.filter((_, i) => i !== index));
  }

  // Обновить поле
  function updateField(index: number, updates: Partial<TaskFieldCreate>) {
    setFields(fields.map((f, i) => (i === index ? { ...f, ...updates } : f)));
  }

  // Парсинг заголовков из JSON
  function parseHeaders(): Record<string, string> | undefined {
    if (!headersJson.trim()) return undefined;
    try {
      return JSON.parse(headersJson);
    } catch {
      return undefined;
    }
  }

  // Сабмит формы — создаем задачу
  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const headers = parseHeaders();
    createMutation.mutate(
      {
        name,
        url,
        description: description || undefined,
        schedule_cron: scheduleCron,
        timeout_seconds: timeoutSeconds,
        max_retries: maxRetries,
        notify_on_change: notifyOnChange,
        notify_on_error: notifyOnError,
        ai_prompt: aiPrompt || undefined,
        headers,
        fields: fields
          .filter((f) => f.name && f.selector)
          .map((f, i) => ({ ...f, position: i })),
      },
      {
        onSuccess: (task) => navigate(`/tasks/${task.id}`),
      },
    );
  }

  // Превью — проверяем как работают селекторы
  function handlePreview() {
    const headers = parseHeaders();
    previewMutation.mutate(
      {
        url,
        fields: fields.filter((f) => f.name && f.selector),
        headers,
        timeout_seconds: timeoutSeconds,
      },
      {
        onSuccess: () => setShowPreview(true),
      },
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Кнопка назад */}
      <Button variant="ghost" onClick={() => navigate('/tasks')}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        К задачам
      </Button>

      <h1 className="text-2xl font-bold">Новая задача</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Основное */}
        <Card>
          <CardHeader>
            <CardTitle>Основная информация</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Название</Label>
              <Input
                id="name"
                placeholder="Мониторинг цен на товары"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="url">URL страницы</Label>
              <Input
                id="url"
                type="url"
                placeholder="https://example.com/products"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Описание</Label>
              <Textarea
                id="description"
                placeholder="Что делает эта задача..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
              />
            </div>
          </CardContent>
        </Card>

        {/* Расписание */}
        <Card>
          <CardHeader>
            <CardTitle>Расписание</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="cron">Cron-выражение</Label>
              <Input
                id="cron"
                placeholder="0 */6 * * *"
                value={scheduleCron}
                onChange={(e) => setScheduleCron(e.target.value)}
                required
              />
              {scheduleCron && (
                <p className="text-sm text-muted-foreground">
                  {humanCron(scheduleCron) || 'Некорректное выражение'}
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Поля для скрапинга */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Поля для извлечения</CardTitle>
              <Button type="button" variant="outline" size="sm" onClick={addField}>
                <Plus className="mr-1 h-4 w-4" />
                Добавить
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {fields.map((field, index) => (
              <div key={index} className="space-y-3 p-4 border rounded-lg relative">
                {fields.length > 1 && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute top-2 right-2 h-7 w-7 text-red-500"
                    onClick={() => removeField(index)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label>Название поля</Label>
                    <Input
                      placeholder="price"
                      value={field.name}
                      onChange={(e) => updateField(index, { name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Селектор</Label>
                    <Input
                      placeholder=".product-price"
                      value={field.selector}
                      onChange={(e) => updateField(index, { selector: e.target.value })}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="space-y-1">
                    <Label>Тип селектора</Label>
                    <Select
                      value={field.selector_type || 'css'}
                      onValueChange={(val) => updateField(index, { selector_type: val })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="css">CSS</SelectItem>
                        <SelectItem value="xpath">XPath</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label>Тип данных</Label>
                    <Select
                      value={field.data_type || 'text'}
                      onValueChange={(val) => updateField(index, { data_type: val })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="text">Текст</SelectItem>
                        <SelectItem value="number">Число</SelectItem>
                        <SelectItem value="url">URL</SelectItem>
                        <SelectItem value="image">Изображение</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label>Атрибут</Label>
                    <Input
                      placeholder="href, src..."
                      value={field.attribute || ''}
                      onChange={(e) => updateField(index, { attribute: e.target.value })}
                    />
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Switch
                    checked={field.is_list ?? false}
                    onCheckedChange={(checked) => updateField(index, { is_list: checked })}
                  />
                  <Label>Список (несколько элементов)</Label>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Дополнительные настройки */}
        <Card>
          <CardHeader>
            <CardTitle>Дополнительно</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="headers">HTTP-заголовки (JSON)</Label>
              <Textarea
                id="headers"
                placeholder='{"User-Agent": "Mozilla/5.0..."}'
                value={headersJson}
                onChange={(e) => setHeadersJson(e.target.value)}
                rows={3}
                className="font-mono text-sm"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="timeout">Таймаут (сек)</Label>
                <Input
                  id="timeout"
                  type="number"
                  min={5}
                  max={120}
                  value={timeoutSeconds}
                  onChange={(e) => setTimeoutSeconds(Number(e.target.value))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="retries">Макс. повторов</Label>
                <Input
                  id="retries"
                  type="number"
                  min={0}
                  max={10}
                  value={maxRetries}
                  onChange={(e) => setMaxRetries(Number(e.target.value))}
                />
              </div>
            </div>

            <Separator />

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Уведомлять при изменениях</Label>
                <Switch
                  checked={notifyOnChange}
                  onCheckedChange={setNotifyOnChange}
                />
              </div>
              <div className="flex items-center justify-between">
                <Label>Уведомлять при ошибках</Label>
                <Switch
                  checked={notifyOnError}
                  onCheckedChange={setNotifyOnError}
                />
              </div>
            </div>

            <Separator />

            <div className="space-y-2">
              <Label htmlFor="aiPrompt">AI промпт (опционально)</Label>
              <Textarea
                id="aiPrompt"
                placeholder="Проанализируй изменения цен и дай краткую сводку..."
                value={aiPrompt}
                onChange={(e) => setAiPrompt(e.target.value)}
                rows={3}
              />
              <p className="text-xs text-muted-foreground">
                Промпт для AI-анализа результатов после каждого запуска
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Кнопки действий */}
        <div className="flex gap-3">
          <Button type="submit" disabled={createMutation.isPending}>
            {createMutation.isPending && (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            )}
            Создать задачу
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={handlePreview}
            disabled={!url || previewMutation.isPending}
          >
            {previewMutation.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Eye className="mr-2 h-4 w-4" />
            )}
            Превью
          </Button>
        </div>
      </form>

      {/* Диалог с превью результатов */}
      <Dialog open={showPreview} onOpenChange={setShowPreview}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-auto">
          <DialogHeader>
            <DialogTitle>Результат превью</DialogTitle>
          </DialogHeader>
          {previewMutation.data ? (
            <div className="space-y-3">
              {previewMutation.data.success ? (
                <>
                  <p className="text-sm text-green-500">
                    Выполнено за {(previewMutation.data.duration_ms / 1000).toFixed(1)}с
                  </p>
                  <pre className="p-4 bg-muted rounded-lg text-sm overflow-auto max-h-96 font-mono">
                    {JSON.stringify(previewMutation.data.data, null, 2)}
                  </pre>
                </>
              ) : (
                <p className="text-red-500">{previewMutation.data.error}</p>
              )}
            </div>
          ) : null}
        </DialogContent>
      </Dialog>
    </div>
  );
}
