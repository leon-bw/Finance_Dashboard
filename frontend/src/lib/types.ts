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
