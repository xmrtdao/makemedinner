// Supabase Edge Function: scan-ingredients
// Accepts base64 image, runs CLIP-based vision model inference
// Deployed to AMD Developer Cloud + Supabase Edge

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";

const VISION_API_URL = Deno.env.get("VISION_API_URL") || "http://localhost:8000/predict";
const SUPABASE_SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

serve(async (req) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "POST only" }), { status: 405 });
  }

  try {
    const { image_base64, top_k = 10 } = await req.json();
    if (!image_base64) {
      return new Response(JSON.stringify({ error: "image_base64 required" }), { status: 400 });
    }

    // Forward to AMD-hosted vision inference container
    const resp = await fetch(VISION_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_base64, top_k })
    });

    if (!resp.ok) throw new Error(`Vision API ${resp.status}: ${await resp.text()}`);
    const detected = await resp.json();

    // Filter by confidence threshold
    const threshold = 0.60;
    const ingredients = detected.filter((d: any) => d.confidence >= threshold);

    return new Response(JSON.stringify({
      ingredients,
      raw: detected,
      count: ingredients.length
    }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  } catch (e: any) {
    return new Response(JSON.stringify({ error: e.message }), { status: 500 });
  }
});
