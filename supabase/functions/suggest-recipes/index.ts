// Supabase Edge Function: suggest-recipes
// Takes ingredient list + prefs, calls LLM on AMD MI300X for recipe matching

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";

const LLM_API_URL = Deno.env.get("LLM_API_URL") || "http://localhost:8000/v1/chat/completions";
const MODEL = Deno.env.get("LLM_MODEL") || "meta-llama/Llama-3.1-8B-Instruct";

serve(async (req) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "POST only" }), { status: 405 });
  }

  try {
    const { ingredients, dietary_prefs = [], meal_type = "dinner", max_time = 60, max_recipes = 3 } = await req.json();

    const systemPrompt = `You are ChefMMI, a multimodal AI cooking assistant. Given available ingredients and dietary preferences, suggest realistic recipes with numbered steps.
Output ONLY valid JSON in this format:
{"recipes":[{"title":"...","match_percent":95,"time_minutes":20,"difficulty":"Easy","voice_summary":"...","ingredients_needed":["..."],"shopping_list":["..."],"steps":["..."],"dietary_tags":["..."]}]}`;

    const userPrompt = `Available ingredients: ${ingredients.join(", ")}
Dietary preferences: ${dietary_prefs.join(", ") || "none"}
Meal type: ${meal_type}
Max cooking time: ${max_time} minutes
Suggest ${max_recipes} recipes.`;

    const resp = await fetch(LLM_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: MODEL,
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt }
        ],
        temperature: 0.7,
        max_tokens: 2048
      })
    });

    if (!resp.ok) throw new Error(`LLM API ${resp.status}: ${await resp.text()}`);
    const llmData = await resp.json();
    const content = llmData.choices?.[0]?.message?.content || "{}";

    let recipes;
    try {
      recipes = JSON.parse(content);
    } catch {
      // Fallback extraction if JSON is malformed
      const match = content.match(/\{[\s\S]*\}/);
      recipes = match ? JSON.parse(match[0]) : { recipes: [] };
    }

    return new Response(JSON.stringify(recipes), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  } catch (e: any) {
    return new Response(JSON.stringify({ error: e.message, recipes: [] }), { status: 500 });
  }
});
