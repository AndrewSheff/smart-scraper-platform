// Контекст авторизации — хранит пользователя, токены и все что нужно для auth
import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { login as apiLogin, register as apiRegister, getMe, changePassword as apiChangePassword } from '@/api/auth';
import type { User } from '@/api/types';

const TOKEN_KEY = 'auth_token';
const REFRESH_KEY = 'refresh_token';

// Результат логина — отдаем юзера наверх
export interface LoginResult {
  user: User;
}

// Декодируем JWT без сторонних библиотек — просто base64 пейлоад
function decodeJwt(token: string): Record<string, unknown> {
  const payload = token.split('.')[1];
  return JSON.parse(atob(payload));
}

// Достаем юзера из JWT-токена (если можем)
function extractUserFromToken(token: string): Partial<User> | null {
  try {
    const decoded = decodeJwt(token);
    return {
      id: decoded.sub as string,
      email: decoded.email as string,
      name: decoded.name as string,
      role: decoded.role as string,
      must_change_password: decoded.must_change_password as boolean,
    };
  } catch {
    return null;
  }
}

interface AuthContextValue {
  token: string | null;
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
  mustChangePassword: boolean;
  login: (email: string, password: string) => Promise<LoginResult>;
  register: (email: string, password: string, name: string) => Promise<LoginResult>;
  changePassword: (currentPassword: string, newPassword: string, confirmPassword: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  setUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

// Провайдер — оборачивает все приложение и дает доступ к auth
export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState<User | null>(() => {
    // Пробуем достать юзера из токена сразу, чтобы не мигало
    const savedToken = localStorage.getItem(TOKEN_KEY);
    if (!savedToken) return null;
    return extractUserFromToken(savedToken) as User | null;
  });
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // Сохраняем токены в localStorage и стейт
  const saveTokens = useCallback((accessToken: string, refreshToken?: string) => {
    localStorage.setItem(TOKEN_KEY, accessToken);
    if (refreshToken) {
      localStorage.setItem(REFRESH_KEY, refreshToken);
    }
    setToken(accessToken);
  }, []);

  // При монтировании пытаемся загрузить текущего пользователя
  const loadUser = useCallback(async () => {
    const savedToken = localStorage.getItem(TOKEN_KEY);
    if (!savedToken) {
      setIsLoading(false);
      return;
    }
    try {
      const userData = await getMe();
      setUser(userData);
    } catch {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(REFRESH_KEY);
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  // Логин — сохраняем токены и загружаем пользователя
  const login = useCallback(async (email: string, password: string): Promise<LoginResult> => {
    const tokens = await apiLogin(email, password);
    saveTokens(tokens.access_token, tokens.refresh_token);
    const userData = await getMe();
    setUser(userData);
    return { user: userData };
  }, [saveTokens]);

  // Регистрация — тоже сохраняем токены
  const register = useCallback(async (
    email: string,
    password: string,
    name: string,
  ): Promise<LoginResult> => {
    const tokens = await apiRegister(email, password, name);
    saveTokens(tokens.access_token, tokens.refresh_token);
    const userData = await getMe();
    setUser(userData);
    return { user: userData };
  }, [saveTokens]);

  // Смена пароля
  const changePassword = useCallback(async (
    currentPassword: string,
    newPassword: string,
    confirmPassword: string,
  ) => {
    await apiChangePassword(currentPassword, newPassword, confirmPassword);
    // Перезагружаем пользователя — must_change_password мог измениться
    const userData = await getMe();
    setUser(userData);
  }, []);

  // Выход — чистим все и кидаем на логин
  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    setToken(null);
    setUser(null);
    navigate('/login');
  }, [navigate]);

  // Перезагрузить данные пользователя
  const refreshUser = useCallback(async () => {
    const userData = await getMe();
    setUser(userData);
  }, []);

  // Вычисляемые свойства — для удобства в компонентах
  const isAuthenticated = !!token && !!user;
  const isAdmin = user?.role === 'admin';
  const mustChangePassword = user?.must_change_password ?? false;

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        isLoading,
        isAuthenticated,
        isAdmin,
        mustChangePassword,
        login,
        register,
        changePassword,
        logout,
        refreshUser,
        setUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// Хук для доступа к контексту авторизации — кидает ошибку, если без провайдера
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth нужно использовать внутри AuthProvider');
  }
  return context;
}

export default AuthContext;
