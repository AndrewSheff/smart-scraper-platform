// Экспорт данных в xlsx — скачивание файлов через blob
import apiClient from './client';

// Выгрузить результаты задачи в xlsx (можно указать период)
export async function exportTask(
  taskId: string,
  dateFrom?: string,
  dateTo?: string,
): Promise<Blob> {
  const { data } = await apiClient.get(`/export/task/${taskId}`, {
    params: { date_from: dateFrom, date_to: dateTo },
    responseType: 'blob',
  });
  return data;
}

// Выгрузить сводку по всем задачам в xlsx
export async function exportSummary(): Promise<Blob> {
  const { data } = await apiClient.get('/export/summary', {
    responseType: 'blob',
  });
  return data;
}
