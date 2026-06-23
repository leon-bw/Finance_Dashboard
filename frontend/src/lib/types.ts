export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_demo: boolean;
  currency_preference: string;
  monthly_budget: number | null;
  created_at: string;
  last_login: string | null;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface RegisterPayload {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  password: string;
  currency_preference?: string;
  monthly_budget?: number;
}

export interface QuickStats {
  total_income: number;
  total_expense: number;
  net_balance: number;
  budget_spent_percentage: number | null;
  budget_remaining: number | null;
}

export interface LearningStats {
  xp_total: number;
  level: number;
  current_streak: number;
  longest_streak: number;
  hearts: number;
  last_activity_date: string | null;
}

// ---- Learning ----

export interface CourseSummary {
  id: string;
  title: string;
  slug: string;
  description: string | null;
  icon: string | null;
  colour: string | null;
  order: number;
  total_lessons: number;
  completed_lessons: number;
  progress_percentage: number;
}

export type LessonStatus = "not_started" | "completed";

export interface LessonSummary {
  id: string;
  title: string;
  order: number;
  xp_reward: number;
  status: LessonStatus;
  score: number | null;
}

export interface Unit {
  id: string;
  title: string;
  description: string | null;
  order: number;
  lessons: LessonSummary[];
}

export interface CourseDetail {
  id: string;
  title: string;
  slug: string;
  description: string | null;
  icon: string | null;
  colour: string | null;
  order: number;
  units: Unit[];
}

export type QuestionType = "multiple_choice" | "true_false";

export interface Question {
  id: string;
  prompt: string;
  type: QuestionType;
  options: string[] | null;
  order: number;
}

export interface Lesson {
  id: string;
  unit_id: string;
  title: string;
  order: number;
  xp_reward: number;
  questions: Question[];
}

export interface QuestionResult {
  question_id: string;
  correct: boolean;
  correct_answer: string;
  explanation: string | null;
}

export interface LessonResult {
  lesson_id: string;
  score: number;
  correct_count: number;
  total_questions: number;
  passed: boolean;
  xp_earned: number;
  results: QuestionResult[];
  stats: LearningStats;
}

// ---- Categories ----

export type EntryType = "income" | "expense";

export interface Category {
  id: string;
  name: string;
  type: EntryType;
  description: string | null;
  colour: string | null;
  icon: string | null;
  user_id: string | null;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

// ---- Transactions ----

export interface Transaction {
  id: string;
  amount: number;
  description: string;
  date: string;
  category: string;
  type: EntryType;
  account: string;
  currency: string;
  status: "completed" | "pending";
  created_at: string;
  updated_at: string;
}

export interface TransactionPayload {
  amount: number;
  description: string;
  date: string | null;
  category: string;
  type: EntryType;
  account: string;
  currency?: string;
}

// ---- Budgets ----

export type BudgetPeriod = "daily" | "weekly" | "monthly" | "yearly";

export interface Budget {
  id: string;
  user_id: string;
  amount: number;
  period: BudgetPeriod;
  category_id: string | null;
  start_date: string;
  end_date: string;
  is_active: boolean;
  alert_threshold: number;
  created_at: string;
  updated_at: string;
}

export interface BudgetPayload {
  amount: number;
  period: BudgetPeriod;
  category_id: string | null;
  start_date: string;
  end_date: string;
  alert_threshold: number;
}

// ---- Notifications ----

export type NotificationType =
  | "lesson_completed"
  | "streak"
  | "level_up"
  | "achievement";

export interface AppNotification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  icon: string | null;
  is_read: boolean;
  created_at: string;
}
