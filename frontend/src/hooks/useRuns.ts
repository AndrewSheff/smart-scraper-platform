// Хуки для работы с запусками задач
import { useQuery } from '@tanstack/react-query';
import { getTaskRuns, getRun } from '@/api/runs';

// Получить список запусков задачи
export function useTaskRuns(
  taskId: string,
  params?: { page?: number; per_page?: number },
) {
  return useQuery({
    queryKey: ['runs', taskId, params],
    queryFn: () => getTaskRuns(taskId, params),
    enabled: !!taskId,
  });
}

// Получить детали конкретного запуска
export function useRun(runId: string) {
  return useQuery({
    queryKey: ['runs', 'detail', runId],
    queryFn: () => getRun(runId),
    enabled: !!runId,
  });
}
