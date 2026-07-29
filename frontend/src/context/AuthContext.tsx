import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { apiGet, apiPostForm, apiPostJson, clearToken, getToken, setToken } from "../api/client";
import type { Token, User } from "../api/types";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (identifier: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!getToken()) {
      setIsLoading(false);
      return;
    }
    apiGet<User>("/auth/me")
      .then(setUser)
      .catch(() => clearToken())
      .finally(() => setIsLoading(false));
  }, []);

  async function login(identifier: string, password: string) {
    const body = new URLSearchParams({ username: identifier, password });
    const token = await apiPostForm<Token>("/auth/login", body);
    setToken(token.access_token);
    const me = await apiGet<User>("/auth/me");
    setUser(me);
  }

  async function register(email: string, username: string, password: string) {
    await apiPostJson<User>("/auth/register", { email, username, password });
    await login(email, password);
  }

  function logout() {
    clearToken();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
