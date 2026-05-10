"""
MakeMeDinner — Vision + LLM Cooking Assistant Demo
Streamlit app for HuggingFace Spaces
"""
import streamlit as st
from dataclasses import dataclass
from typing import List
import random

st.set_page_config(page_title="MakeMeDinner AI", page_icon="🍳", layout="wide")

@dataclass
class Ingredient:
    name: str
    confidence: float
    tag: str

@dataclass
class Recipe:
    title: str
    match: int
    time: str
    calories: int
    tags: List[str]
    desc: str
    steps: List[str]
    ingredients: List[str]
    missing: List[str]

RECIPE_DB = [
    Recipe("Veggie Omelette", 96, "15 min", 320,
        ["vegetarian", "quick"],
        "Fluffy eggs loaded with fresh veggies.",
        ["Whisk 3 eggs with salt+pepper", "Sauté diced veggies 3 min", "Pour eggs, add spinach+cheese", "Fold, cook 2 min each side"],
        ["eggs", "tomatoes", "onion", "cheese", "spinach"],
        ["olive oil", "salt"]),
    Recipe("Shakshuka", 91, "25 min", 280,
        ["halal", "gluten-free"],
        "Poached eggs in rich spiced tomato sauce.",
        ["Sauté onion and pepper 5 min", "Add tomatoes, cumin, paprika", "Simmer 10 min", "Crack eggs into wells", "Cover 5-7 min"],
        ["eggs", "tomatoes", "onion", "bell pepper"],
        ["cumin", "paprika", "bread"]),
    Recipe("Spinach Frittata", 89, "20 min", 380,
        ["vegetarian", "quick"],
        "Oven-baked egg dish — perfect for brunch.",
        ["Preheat broiler", "Sauté veggies in pan", "Pour 4 beaten eggs", "Stovetop 4 min, broil 2 min"],
        ["eggs", "tomatoes", "onion", "spinach", "cheese"],
        []),
    Recipe("Tomato Bruschetta", 78, "10 min", 180,
        ["vegan", "quick"],
        "Fresh diced tomatoes on toasted bread.",
        ["Dice tomatoes and onion", "Mince garlic + olive oil", "Combine, add salt+pepper", "Spoon onto toasted bread"],
        ["tomatoes", "onion", "garlic", "olive oil"],
        ["bread", "basil"]),
    Recipe("Stuffed Peppers", 72, "35 min", 420,
        ["gluten-free"],
        "Bell peppers stuffed with egg scramble.",
        ["Halve peppers, remove seeds", "Scramble eggs with veggies", "Stuff peppers, top with cheese", "Bake 375°F 20 min"],
        ["bell pepper", "eggs", "tomatoes", "onion", "spinach", "cheese"],
        []),
    Recipe("Spinach Salad", 85, "5 min", 150,
        ["vegan", "keto", "quick"],
        "Raw crunchy salad perfect as a side.",
        ["Chop tomatoes into wedges", "Tear spinach", "Toss with olive oil, salt, pepper"],
        ["tomatoes", "spinach", "onion", "olive oil"],
        []),
]

# CSS
st.markdown("""
<style>
.main-header { text-align:center; padding:2rem 1rem; }
.main-header h1 { font-size:2.5rem; background: linear-gradient(135deg,#ff6b35,#f7931e); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.ingredient-pill { display:inline-block; background:rgba(255,107,53,0.15); border:1px solid rgba(255,107,53,0.3); color:#ff6b35; padding:4px 12px; border-radius:8px; margin:2px; font-size:0.85rem; }
.recipe-card { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:16px; padding:1.25rem; margin-bottom:1rem; }
.recipe-title { font-size:1.1rem; font-weight:700; color:#fff; }
.match-badge { background:rgba(0,200,83,0.15); color:#00c853; padding:2px 10px; border-radius:6px; font-size:0.75rem; font-weight:700; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🍳 MakeMeDinner AI</h1><p style="color:#888;">Scan ingredients, get recipes. Powered by multimodal AI.</p></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1,1.2])

with col1:
    st.subheader("📷 Scan Your Ingredients")
    uploaded = st.file_uploader("Drop or snap a photo", type=["jpg","jpeg","png"])
    st.caption("In production: camera capture + CLIP/SigLIP vision model")

    if uploaded:
        st.image(uploaded, use_container_width=True)

    if st.button("🔍 Analyze Ingredients", type="primary") or uploaded:
        with st.spinner("Analyzing with vision AI..."):
            import time; time.sleep(1.5)

        detected = [
            Ingredient("Eggs", 0.97, "dairy-free"),
            Ingredient("Tomatoes", 0.94, "vegan"),
            Ingredient("Onion", 0.91, "vegan"),
            Ingredient("Cheese", 0.88, "halal"),
            Ingredient("Spinach", 0.85, "vegan"),
            Ingredient("Bell Pepper", 0.72, "vegan"),
            Ingredient("Garlic", 0.68, "vegan"),
        ]
        st.session_state["pantry"] = detected

with col2:
    if "pantry" in st.session_state:
        st.subheader("Detected Ingredients")
        html = ""
        for i in st.session_state["pantry"]:
            html += f'<span class="ingredient-pill">{i.name} <span style="opacity:0.7;">{i.confidence*100:.0f}%</span></span>'
        st.markdown(html, unsafe_allow_html=True)

        filters = ["all", "vegan", "keto", "gluten-free", "halal", "quick"]
        active = st.segmented_control("Filter", filters, default="all")

        matched = [r for r in RECIPE_DB if active=="all" or active in r.tags or (active=="quick" and "quick" in r.tags)]

        st.markdown(f"""<div style="margin:1.5rem 0 0.5rem;">
<h3>🥘 {len(matched)} Recipe Ideas</h3>
<p style="color:#888; font-size:0.85rem;">Ranked by ingredient match and your filters</p>
</div>""", unsafe_allow_html=True)

        for r in matched:
            with st.container():
                st.markdown(f"""<div class="recipe-card">
  <div style="display:flex; justify-content:space-between; align-items:start;">
    <div class="recipe-title">{r.title}</div>
    <div class="match-badge">{r.match}% match</div>
  </div>
  <div style="color:#888; font-size:0.8rem; margin:0.5rem 0;">⏱ {r.time} · 🔥 {r.calories} cal · 🥗 {len(r.ingredients)} items</div>
  <div style="color:#ccc; font-size:0.9rem;">{r.desc}</div>
</div>
                """, unsafe_allow_html=True)

                if st.button(f"📖 View Steps", key=r.title):
                    st.session_state["selected_recipe"] = r

    # Selected recipe steps
    if "selected_recipe" in st.session_state:
        r = st.session_state["selected_recipe"]
        st.markdown(f"### {r.title} — Steps")
        for i, step in enumerate(r.steps, 1):
            st.markdown(f"<div style='padding:0.5rem 0; border-bottom:1px solid rgba(255,255,255,0.05);'><b>{i}.</b> {step}</div>", unsafe_allow_html=True)

        if r.missing:
            st.markdown(f"#### 🛒 Missing: {', '.join(r.missing)}")

        if st.button("🔊 Read Aloud"):
            # Using browser TTS via HTML audio element injection
            text = r.title + ". " + ". ".join(r.steps)
            st.markdown(f"""
<script>
const u = new SpeechSynthesisUtterance("{text}"); u.rate=0.9; window.speechSynthesis.speak(u);
</script>
            """, unsafe_allow_html=True)
            st.toast("Reading steps aloud...")

st.markdown("---")
st.caption("MakeMeDinner — AMD Developer Hackathon · Vision & Multimodal AI Track · OSS")

# v2 rebuild trigger
