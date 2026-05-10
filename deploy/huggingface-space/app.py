import gradio as gr
import requests
import json
import base64
from PIL import Image
import io

"""
MakeMeDinner — Hugging Face Space Demo
Vision + LLM cooking assistant for AMD Developer Hackathon
"""

API_BASE = "https://your-project.supabase.co/functions/v1"
SCAN_ENDPOINT = f"{API_BASE}/scan-ingredients"
RECIPE_ENDPOINT = f"{API_BASE}/suggest-recipes"

def scan_and_recipe(image, dietary_prefs, meal_type, max_time):
    if image is None:
        return "Please upload an image of your fridge or pantry.", ""

    # Convert PIL image to base64
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    b64 = base64.b64encode(buf.getvalue()).decode()

    # Call scan endpoint (simulated if API unavailable)
    try:
        scan_resp = requests.post(SCAN_ENDPOINT, json={"image_base64": b64, "top_k": 10}, timeout=30)
        ingredients = scan_resp.json().get("ingredients", []) if scan_resp.ok else []
    except Exception:
        # Fallback demo ingredients
        ingredients = [
            {"name": "eggs", "confidence": 0.97},
            {"name": "tomatoes", "confidence": 0.94},
            {"name": "onion", "confidence": 0.91},
            {"name": "cheese", "confidence": 0.88},
            {"name": "spinach", "confidence": 0.85},
        ]

    ing_text = ", ".join([f"{i['name']} ({i['confidence']:.0%})" for i in ingredients])

    # Call recipe endpoint
    try:
        recipe_resp = requests.post(RECIPE_ENDPOINT, json={
            "ingredients": [i["name"] for i in ingredients],
            "dietary_prefs": dietary_prefs.split(",") if dietary_prefs else [],
            "meal_type": meal_type,
            "max_time": max_time,
            "max_recipes": 3
        }, timeout=60)
        recipes = recipe_resp.json().get("recipes", []) if recipe_resp.ok else []
    except Exception:
        recipes = [
            {
                "title": "Veggie Omelette with Spinach",
                "match_percent": 96,
                "time_minutes": 15,
                "steps": ["Dice tomatoes, onion, bell pepper.", "Whisk 3 eggs.", "Saute veggies 3 min.", "Pour eggs, add spinach and cheese.", "Fold and cook 2 min each side."],
                "dietary_tags": ["vegetarian", "gluten-free"]
            },
            {
                "title": "Shakshuka (Eggs in Tomato Sauce)",
                "match_percent": 91,
                "time_minutes": 25,
                "steps": ["Saute onion and bell pepper.", "Add tomatoes and spices, simmer 10 min.", "Make wells, crack eggs in.", "Cover, cook 5-7 min.", "Top with cheese if desired."],
                "dietary_tags": ["vegetarian", "gluten-free"]
            },
        ]

    recipe_md = "## Suggested Recipes\n\n"
    for r in recipes:
        recipe_md += f"### {r['title']} — {r['match_percent']}% match · {r['time_minutes']} min\n"
        recipe_md += f"**Tags:** {', '.join(r.get('dietary_tags', []))}\n\n"
        for i, step in enumerate(r.get("steps", []), 1):
            recipe_md += f"{i}. {step}\n"
        recipe_md += "\n---\n\n"

    return ing_text, recipe_md

demo = gr.Interface(
    fn=scan_and_recipe,
    inputs=[
        gr.Image(type="pil", label="Snap your fridge/pantry"),
        gr.Textbox(label="Dietary Preferences (comma-separated)", placeholder="vegan, gluten-free, keto..."),
        gr.Dropdown(["breakfast", "lunch", "dinner", "snack"], value="dinner", label="Meal Type"),
        gr.Slider(5, 120, value=30, step=5, label="Max Cooking Time (minutes)")
    ],
    outputs=[
        gr.Textbox(label="Detected Ingredients", lines=3),
        gr.Markdown(label="Recipes")
    ],
    title="MakeMeDinner — AI Cooking Assistant",
    description="Upload a photo of your ingredients and get AI-generated recipes you can make right now. Built for the AMD Developer Hackathon.",
    examples=[
        [None, "", "dinner", 30],
    ],
    allow_flagging="never"
)

if __name__ == "__main__":
    demo.launch()
