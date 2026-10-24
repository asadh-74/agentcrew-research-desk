import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Keep local builds and the UI usable before hosting credentials are configured.
// The API reports a clear readiness error when persistence is unavailable.
export const supabase =
  supabaseUrl && supabaseAnonKey
    ? createClient(supabaseUrl, supabaseAnonKey)
    : null;

export type ResearchSession = {
  id: string;
  topic: string;
  status: "running" | "completed" | "failed";
  result: string | null;
  created_at: string;
};
