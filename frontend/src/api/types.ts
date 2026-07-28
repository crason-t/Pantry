export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Ingredient {
  id: number;
  position: number;
  quantity: string | null;
  unit: string | null;
  name: string;
  notes: string | null;
  raw_text: string;
}

export interface RecipeStep {
  id: number;
  position: number;
  instruction: string;
}

export interface Recipe {
  id: number;
  title: string;
  servings: number | null;
  prep_time: string | null;
  cook_time: string | null;
  total_time: string | null;
  equipment: string[];
  source_url: string | null;
  created_by_user_id: number;
  created_at: string;
  ingredients: Ingredient[];
  steps: RecipeStep[];
}

export interface RecipeSummary {
  id: number;
  title: string;
  servings: number | null;
  total_time: string | null;
  saved_at: string;
}
