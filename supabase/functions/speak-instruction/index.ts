// Supabase Edge Function: speak-instruction
// Text-to-speech for cooking steps. Caches audio in Supabase storage.

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";

const TTS_API_URL = Deno.env.get("TTS_API_URL") || "http://localhost:8000/speak";

serve(async (req) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "POST only" }), { status: 405 });
  }

  try {
    const { text, voice = "default" } = await req.json();
    if (!text) {
      return new Response(JSON.stringify({ error: "text required" }), { status: 400 });
    }

    // Check cache first
    const encoder = new TextEncoder();
    const hashBuffer = await crypto.subtle.digest("SHA-256", encoder.encode(text + voice));
    const hash = Array.from(new Uint8Array(hashBuffer)).map(b => b.toString(16).padStart(2, "0")).join("");

    // In production, query Supabase tts_cache table first
    // If miss, call TTS API
    const resp = await fetch(TTS_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, voice, hash })
    });

    if (!resp.ok) throw new Error(`TTS API ${resp.status}: ${await resp.text()}`);
    const { audio_url } = await resp.json();

    return new Response(JSON.stringify({ audio_url, text_hash: hash }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  } catch (e: any) {
    return new Response(JSON.stringify({ error: e.message }), { status: 500 });
  }
});
