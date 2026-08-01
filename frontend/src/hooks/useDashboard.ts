// Хуки для дашборда — статистика, графики, последние запуски
import { useQuery } from '@tanstack/react-query';
import { getStats, getChart, getRecentRuns } from '@/api/dashboard';

// Общая статистика
export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: getStats,
  });
}

// Данные для графика
export function useDashboardChart(days: number = 7) {
  return useQuery({
    queryKey: ['dashboard', 'chart', days],
    queryFn: () => getChart(days),
  });
}

// Последние запуски
export function useRecentRuns(limit: number = 10) {
  return useQuery({
    queryKey: ['dashboard', 'recent-runs', limit],
    queryFn: () => getRecentRuns(limit),
  });
}
