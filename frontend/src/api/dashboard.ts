// API для дашборда — статистика, графики, последние запуски
import apiClient from './client';
import type { DashboardStats, ChartResponse, RecentRunsResponse } from './types';

// Получить общую статистику по задачам и запускам
export async function getStats(): Promise<DashboardStats> {
  const { data } = await apiClient.get<DashboardStats>('/dashboard/stats');
  return data;
}

// Получить данные для графика за определенный период
export async function getChart(days: number = 7): Promise<ChartResponse> {
  const { data } = await apiClient.get<ChartResponse>('/dashboard/chart', {
    params: { period_days: days },
  });
  return data;
}

// Получить последние запуски для дашборда
export async function getRecentRuns(limit: number = 10): Promise<RecentRunsResponse> {
  const { data } = await apiClient.get<RecentRunsResponse>('/dashboard/recent-runs', {
    params: { limit },
  });
  return data;
}
