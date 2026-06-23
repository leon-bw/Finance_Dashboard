import type {
  AppNotification,
  Budget,
  BudgetPayload,
  Category,
  CourseDetail,
  CourseSummary,
  LearningStats,
  Lesson,
  LessonResult,
  QuickStats,
  RegisterPayload,
  Token,
  Transaction,
  TransactionPayload,
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

// ---- Learning ----

export async function getCourses(): Promise<CourseSummary[]> {
  return apiFetch<CourseSummary[]>("/learn/courses");
}

export async function getCourse(id: string): Promise<CourseDetail> {
  return apiFetch<CourseDetail>(`/learn/courses/${id}`);
}

export async function getLesson(id: string): Promise<Lesson> {
  return apiFetch<Lesson>(`/learn/lessons/${id}`);
}

export async function submitLesson(
  id: string,
  answers: { question_id: string; answer: string }[],
): Promise<LessonResult> {
  return apiFetch<LessonResult>(`/learn/lessons/${id}/submit`, {
    method: "POST",
    body: JSON.stringify({ answers }),
  });
}

// ---- Categories ----

export async function getCategories(): Promise<Category[]> {
  return apiFetch<Category[]>("/categories/");
}

// ---- Transactions ----

export async function getTransactions(): Promise<Transaction[]> {
  return apiFetch<Transaction[]>("/transactions/");
}

export async function createTransaction(
  payload: TransactionPayload,
): Promise<Transaction> {
  return apiFetch<Transaction>("/transactions/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateTransaction(
  id: string,
  payload: Partial<TransactionPayload>,
): Promise<Transaction> {
  return apiFetch<Transaction>(`/transactions/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteTransaction(id: string): Promise<void> {
  return apiFetch<void>(`/transactions/${id}`, { method: "DELETE" });
}

// ---- Budgets ----

export async function getBudgets(): Promise<Budget[]> {
  return apiFetch<Budget[]>("/budgets/");
}

export async function createBudget(payload: BudgetPayload): Promise<Budget> {
  return apiFetch<Budget>("/budgets/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateBudget(
  id: string,
  payload: Partial<BudgetPayload> & { is_active?: boolean },
): Promise<Budget> {
  return apiFetch<Budget>(`/budgets/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteBudget(id: string): Promise<void> {
  return apiFetch<void>(`/budgets/${id}`, { method: "DELETE" });
}

// ---- Notifications ----

export async function getNotifications(
  unreadOnly = false,
): Promise<AppNotification[]> {
  const query = unreadOnly ? "?unread_only=true" : "";
  return apiFetch<AppNotification[]>(`/notifications/${query}`);
}

export async function getUnreadCount(): Promise<number> {
  const data = await apiFetch<{ unread: number }>(
    "/notifications/unread-count",
  );
  return data.unread;
}

export async function markNotificationRead(
  id: string,
): Promise<AppNotification> {
  return apiFetch<AppNotification>(`/notifications/${id}/read`, {
    method: "POST",
  });
}

export async function markAllNotificationsRead(): Promise<void> {
  return apiFetch<void>("/notifications/read-all", { method: "POST" });
}
