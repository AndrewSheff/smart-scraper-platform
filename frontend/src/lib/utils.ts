import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

// утилита для мержа tailwind классов — склеивает и разруливает конфликты
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
