import { createContext, useCallback, useContext, useState } from "react";
import { api } from "../api/client";

const AuthContext = createContext(null);

/** EX-01: le rôle est fixé à l'inscription ; ce contexte ne fait que le refléter, jamais le modifier. */
export function AuthProvider({ children }) {
  const [role, setRole] = useState(() => localStorage.getItem("role"));
  const [token, setToken] = useState(() => localStorage.getItem("token"));

  const login = useCallback(async (email, password) => {
    const data = await api.post("/api/auth/login", { email, password });
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("role", data.role);
    setToken(data.access_token);
    setRole(data.role);
    return data.role;
  }, []);

  const register = useCallback(
    async (email, password, chosenRole) => {
      await api.post("/api/auth/register", { email, password, role: chosenRole });
      return login(email, password);
    },
    [login],
  );

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    setToken(null);
    setRole(null);
  }, []);

  const value = { role, token, isAuthenticated: Boolean(token), login, register, logout };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth doit être utilisé à l'intérieur d'un AuthProvider.");
  return ctx;
}
