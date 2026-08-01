// Настройки уведомлений — телеграм бот, чат, тестовая отправка
import { useState, type FormEvent } from 'react';
import { Eye, EyeOff, Send, Loader2, Bot, MessageSquare } from 'lucide-react';
import {
  useNotificationSettings,
  useUpdateNotificationSettings,
  useSendTestNotification,
} from '@/hooks/useNotifications';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Separator } from '@/components/ui/separator';

export default function NotificationsPage() {
  const { data: settings, isLoading } = useNotificationSettings();
  const updateMutation = useUpdateNotificationSettings();
  const testMutation = useSendTestNotification();

  const [botToken, setBotToken] = useState('');
  const [chatId, setChatId] = useState('');
  const [showToken, setShowToken] = useState(false);
  const [synced, setSynced] = useState(false);

  // Заполняем форму данными с сервера (паттерн adjust-state-during-render)
  if (settings && !synced) {
    setBotToken(settings.telegram_bot_token || '');
    setChatId(settings.telegram_chat_id || '');
    setSynced(true);
  }

  // Сохранение настроек
  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    updateMutation.mutate({
      telegram_bot_token: botToken || undefined,
      telegram_chat_id: chatId || undefined,
    });
  }

  // Тестовая отправка
  function handleTest() {
    testMutation.mutate();
  }

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Уведомления</h1>

      {/* Настройки Telegram */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            Telegram Bot
          </CardTitle>
          <CardDescription>
            Настройте бота для получения уведомлений об изменениях и ошибках
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="botToken">Bot Token</Label>
              <div className="relative">
                <Input
                  id="botToken"
                  type={showToken ? 'text' : 'password'}
                  placeholder="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
                  value={botToken}
                  onChange={(e) => setBotToken(e.target.value)}
                  className="pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-full"
                  onClick={() => setShowToken(!showToken)}
                >
                  {showToken ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="chatId">Chat ID</Label>
              <Input
                id="chatId"
                placeholder="-1001234567890"
                value={chatId}
                onChange={(e) => setChatId(e.target.value)}
              />
            </div>

            <div className="flex gap-3">
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                Сохранить
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={handleTest}
                disabled={testMutation.isPending || !botToken || !chatId}
              >
                {testMutation.isPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Send className="mr-2 h-4 w-4" />
                )}
                Тест
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Инструкция по настройке */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Как настроить
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <Separator />
          <ol className="list-decimal pl-4 space-y-2">
            <li>
              Найдите в Telegram бота{' '}
              <span className="font-mono text-foreground">@BotFather</span> и
              создайте нового бота командой{' '}
              <span className="font-mono text-foreground">/newbot</span>
            </li>
            <li>
              Скопируйте полученный токен и вставьте в поле «Bot Token» выше
            </li>
            <li>
              Для получения Chat ID напишите любое сообщение вашему боту, затем
              перейдите по ссылке:{' '}
              <span className="font-mono text-foreground break-all">
                https://api.telegram.org/bot&lt;TOKEN&gt;/getUpdates
              </span>
            </li>
            <li>
              Найдите значение{' '}
              <span className="font-mono text-foreground">chat.id</span> в
              ответе и вставьте его в поле «Chat ID»
            </li>
            <li>
              Нажмите «Тест» для проверки — бот должен отправить тестовое
              сообщение
            </li>
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}
