"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  clearToken,
  getMe,
  getToken,
  login as apiLogin,
  register as apiRegister,
  setToken,
} from "@/lib/api";
import type { RegisterPayload, User } from "@/lib/types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    try {
      if (getToken()) {
        setUser(await getMe());
      } else {
        setUser(null);
      }
    } catch {
      clearToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Resolve a microtask first so state updates never run synchronously
    // inside the effect body.
    void Promise.resolve().then(loadUser);
  }, [loadUser]);

  const login = useCallback(async (username: string, password: string) => {
    const token = await apiLogin(username, password);
    setToken(token.access_token);
    setUser(await getMe());
  }, []);

  const register = useCallback(
    async (payload: RegisterPayload) => {
      await apiRegister(payload);
      await login(payload.username, payload.password);
    },
    [login],
  );

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, register, logout }),
    [user, loading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
