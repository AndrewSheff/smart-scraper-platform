// Типы данных для всего приложения — тут живут все интерфейсы

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
  must_change_password: boolean;
  telegram_bot_token?: string;
  telegram_chat_id?: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  url: string;
  schedule_cron: string;
  is_active: boolean;
  headers?: Record<string, string>;
  timeout_seconds: number;
  max_retries: number;
  notify_on_change: boolean;
  notify_on_error: boolean;
  ai_prompt?: string;
  last_run_at?: string;
  last_status?: string;
  total_runs: number;
  success_runs: number;
  fields: TaskField[];
  created_at: string;
  updated_at: string;
}

export interface TaskField {
  id: string;
  name: string;
  selector: string;
  selector_type: string;
  data_type: string;
  is_list: boolean;
  attribute?: string;
  position: number;
}

export interface TaskFieldCreate {
  name: string;
  selector: string;
  selector_type?: string;
  data_type?: string;
  is_list?: boolean;
  attribute?: string;
  position?: number;
}

export interface TaskRun {
  id: string;
  task_id: string;
  status: string;
  started_at: string;
  finished_at?: string;
  duration_ms?: number;
  items_count: number;
  error_message?: string;
  ai_summary?: string;
  has_changes: boolean;
  created_at: string;
}

export interface TaskRunDetail extends TaskRun {
  results: RunResult[];
  changes: TaskChange[];
}

export interface RunResult {
  id: string;
  field_name: string;
  field_value?: string;
  field_index: number;
}

export interface TaskChange {
  id: string;
  change_type: string;
  field_name: string;
  old_value?: string;
  new_value?: string;
  item_index: number;
}

export interface DashboardStats {
  total_tasks: number;
  active_tasks: number;
  runs_today: number;
  errors_today: number;
  success_rate: number;
}

export interface ChartDataPoint {
  date: string;
  success: number;
  failed: number;
  total: number;
}

export interface ChartResponse {
  data: ChartDataPoint[];
}

// Элемент списка последних запусков — с названием задачи, чтоб не показывать UUID
export interface RecentRunItem {
  id: string;
  task_id: string;
  task_name: string;
  status: string;
  started_at: string;
  duration_ms?: number;
  has_changes: boolean;
  items_count: number;
}

export interface RecentRunsResponse {
  items: RecentRunItem[];
}

export interface PreviewResponse {
  success: boolean;
  data?: Record<string, unknown>;
  error?: string;
  duration_ms: number;
}

export interface NotificationSettings {
  telegram_bot_token?: string;
  telegram_chat_id?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginResult {
  user: User;
}

// Данные для создания/обновления задачи
export interface TaskCreate {
  name: string;
  description?: string;
  url: string;
  schedule_cron: string;
  is_active?: boolean;
  headers?: Record<string, string>;
  timeout_seconds?: number;
  max_retries?: number;
  notify_on_change?: boolean;
  notify_on_error?: boolean;
  ai_prompt?: string;
  fields: TaskFieldCreate[];
}

export interface TaskUpdate {
  name?: string;
  description?: string;
  url?: string;
  schedule_cron?: string;
  is_active?: boolean;
  headers?: Record<string, string>;
  timeout_seconds?: number;
  max_retries?: number;
  notify_on_change?: boolean;
  notify_on_error?: boolean;
  ai_prompt?: string;
  fields?: TaskFieldCreate[];
}

// Данные для создания/обновления пользователя
export interface UserCreate {
  email: string;
  password: string;
  name: string;
  role?: string;
}

export interface UserUpdate {
  email?: string;
  name?: string;
  role?: string;
  is_active?: boolean;
}
