// API для работы с запусками (ранами) задач
import apiClient from './client';
import type { TaskRun, TaskRunDetail, PaginatedResponse } from './types';

// Получить список запусков конкретной задачи
export async function getTaskRuns(
  taskId: string,
  params?: { page?: number; per_page?: number },
): Promise<PaginatedResponse<TaskRun>> {
  const { data } = await apiClient.get<PaginatedResponse<TaskRun>>(
    `/runs/task/${taskId}`,
    { params },
  );
  return data;
}

// Получить детали конкретного запуска — с результатами и изменениями
export async function getRun(runId: string): Promise<TaskRunDetail> {
  const { data } = await apiClient.get<TaskRunDetail>(`/runs/${runId}`);
  return data;
}
