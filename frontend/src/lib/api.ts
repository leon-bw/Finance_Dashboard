import type {
  LearningStats,
  QuickStats,
  RegisterPayload,
  Token,
  User,
} from "./types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

const TOKEN_KEY = "fw_access_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function parseError(response: Response): Promise<string> {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail) && data.detail[0]?.msg) {
      return data.detail[0].msg;
    }
    return response.statusText;
  } catch {
    return response.statusText;
  }
}

/**
 * Authenticated JSON request to the API.
 */
export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!response.ok) {
    throw new ApiError(await parseError(response), response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export async function login(
  username: string,
  password: string,
): Promise<Token> {
  // The login endpoint expects form-encoded credentials (OAuth2 password flow).
  const body = new URLSearchParams({ username, password });
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  if (!response.ok) {
    throw new ApiError(await parseError(response), response.status);
  }

  return (await response.json()) as Token;
}

export async function register(payload: RegisterPayload): Promise<User> {
  return apiFetch<User>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getMe(): Promise<User> {
  return apiFetch<User>("/auth/me");
}

export async function getQuickStats(): Promise<QuickStats> {
  return apiFetch<QuickStats>("/dashboard/quick-stats");
}

export async function getLearningStats(): Promise<LearningStats> {
  return apiFetch<LearningStats>("/learn/me/stats");
}
