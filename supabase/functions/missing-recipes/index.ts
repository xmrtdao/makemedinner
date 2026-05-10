// Supabase Edge Function: missing-recipes
// Return recipes that need only 1-2 more ingredients

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";

const LLM_API_URL = Deno.env.get("LLM_API_URL") || "http://localhost:8000/v1/chat/completions";

serve(async (req) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "POST only" }), { status: 405 });
  }

  try {
    const { ingredients, max_missing = 2 } = await req.json();

    const systemPrompt = `You are ChefMMI. Suggest recipes where the user is only missing ${max_missing} ingredients from what they have. Output ONLY valid JSON.`;
    const userPrompt = `Available: ${ingredients.join(", ")}. Suggest 3 recipes with exactly the missing items listed.`;

    const resp = await fetch(LLM_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "meta-llama/Llama-3.1-8B-Instruct",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt }
        ],
        temperature: 0.7,
        max_tokens: 1024
      })
    });

    if (!resp.ok) throw new Error(`LLM API ${resp.status}`);
    const llmData = await resp.json();
    const content = llmData.choices?.[0]?.message?.content || "{}";

    let result;
    try { result = JSON.parse(content); } catch { result = { recipes: [] }; }

    return new Response(JSON.stringify(result), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  } catch (e: any) {
    return new Response(JSON.stringify({ error: e.message, recipes: [] }), { status: 500 });
  }
});
