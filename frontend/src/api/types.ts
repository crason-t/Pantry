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
  colloquial_quantity: string | null;
  name: string;
  notes: string | null;
  raw_text: string;
  component: string | null;
}

export interface RecipeStep {
  id: number;
  position: number;
  instruction: string;
}

export type GlossaryCategory = "flavor" | "technique" | "reaction";

export interface GlossaryTerm {
  slug: string;
  category: GlossaryCategory;
  name: string;
  definition: string;
}

export interface RecipeInsight {
  id: number;
  glossary_term: GlossaryTerm;
  note: string | null;
  step_id: number | null;
  ingredient_id: number | null;
  position: number;
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
  insights: RecipeInsight[];
}

export interface RecipeSummary {
  id: number;
  title: string;
  servings: number | null;
  total_time: string | null;
  saved_at: string;
}
