import streamlit as st
from typing import List, Dict
import datetime
from collections import Counter
from grocery_app.openai_agents.ingredient_extractor import get_ingredient_extractor_agent

# --- CONFIG ---
st.set_page_config(page_title="AI Meal Planner", layout="wide")

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Day selection
    num_days = st.slider(
        "📅 Number of Days to Plan",
        min_value=1,
        max_value=7,
        value=5,
        help="Choose how many days you want to plan meals for (1-7 days)"
    )
    
    # Meal selection
    st.subheader("🍽️ Meals to Include")
    include_breakfast = st.checkbox("Breakfast", value=True)
    include_lunch = st.checkbox("Lunch", value=True)
    include_dinner = st.checkbox("Dinner", value=True)
    
    # Only show meals that are selected
    meals = []
    if include_breakfast:
        meals.append("Breakfast")
    if include_lunch:
        meals.append("Lunch")
    if include_dinner:
        meals.append("Dinner")
    
    # Validation
    if not meals:
        st.error("Please select at least one meal type!")
        st.stop()
    
    st.markdown("---")
    st.caption(f"📊 Planning {num_days} days with {len(meals)} meals per day")

# --- MAIN APP ---
st.title("🍽️ AI Meal Planner: Pick Your Dishes!")
st.write("Select or type the dishes you want for each meal. The AI will generate your shopping list!")

def get_default_days(num_days: int):
    """Generate list of days based on user selection"""
    today = datetime.date.today()
    return [(today + datetime.timedelta(days=i)).strftime("%A") for i in range(num_days)]

days = get_default_days(num_days)

# --- SESSION STATE ---
if "dish_plan" not in st.session_state:
    st.session_state["dish_plan"] = {day: {meal: "" for meal in meals} for day in days}
if "view_mode" not in st.session_state:
    st.session_state["view_mode"] = "day_by_day"  # or 'master'
if "current_day_idx" not in st.session_state:
    st.session_state["current_day_idx"] = 0

# Reset session state if configuration changes
current_config = (num_days, tuple(meals))
if "last_config" not in st.session_state or st.session_state["last_config"] != current_config:
    st.session_state["dish_plan"] = {day: {meal: "" for meal in meals} for day in days}
    st.session_state["current_day_idx"] = 0
    st.session_state["last_config"] = current_config

# --- VIEW TOGGLE BUTTON ---
colA, colB = st.columns([2, 1])
with colA:
    st.caption(":star: You can fill your plan day-by-day or all at once!")
with colB:
    if st.session_state["view_mode"] == "day_by_day":
        if st.button("Switch to Master View (All Days)"):
            st.session_state["view_mode"] = "master"
    else:
        if st.button("Switch to Day-by-Day View"):
            st.session_state["view_mode"] = "day_by_day"

# --- DAY-BY-DAY VIEW ---
if st.session_state["view_mode"] == "day_by_day":
    idx = st.session_state["current_day_idx"]
    day = days[idx]
    st.subheader(f"🗓️ {day}")
    st.progress((idx + 1) / len(days), text=f"Day {idx + 1} of {len(days)}")
    with st.form(f"form_{day}"):
        cols = st.columns(len(meals))
        for i, meal in enumerate(meals):
            key = f"{day}_{meal}"
            st.session_state["dish_plan"][day][meal] = cols[i].text_input(f"{meal}", value=st.session_state["dish_plan"][day][meal], key=key)
        nav_cols = st.columns([1, 1, 2])
        prev_disabled = idx == 0
        next_disabled = idx == len(days) - 1
        with nav_cols[0]:
            prev = st.form_submit_button("⬅️ Previous Day", disabled=prev_disabled)
        with nav_cols[1]:
            next_ = st.form_submit_button("Next Day ➡️", disabled=next_disabled)
        with nav_cols[2]:
            finish = st.form_submit_button("Finish & Generate Shopping List")
            if finish:
                if not any(st.session_state["dish_plan"][d][m] for d in days for m in meals):
                    st.error("Please fill at least one meal before generating the shopping list.")
                else:
                    st.session_state["current_day_idx"] = 0
                    st.session_state["view_mode"] = "summary"
                    st.rerun()
    if prev:
        st.session_state["current_day_idx"] = max(0, idx - 1)
        st.rerun()
    if next_:
        st.session_state["current_day_idx"] = min(len(days) - 1, idx + 1)
        st.rerun()

# --- MASTER VIEW (ALL DAYS AT ONCE) ---
elif st.session_state["view_mode"] == "master":
    st.subheader(f"📝 {num_days}-Day Meal Selection (All Days)")
    with st.form("meal_plan_form"):
        for day in days:
            st.markdown(f"**{day}**")
            cols = st.columns(len(meals))
            for i, meal in enumerate(meals):
                key = f"{day}_{meal}"
                st.session_state["dish_plan"][day][meal] = cols[i].text_input(f"{day} - {meal}", value=st.session_state["dish_plan"][day][meal], key=key)
        submitted = st.form_submit_button("Plan My Week!")
    if submitted:
        st.session_state["view_mode"] = "summary"
        st.rerun()

# --- SUMMARY & SHOPPING LIST GENERATION ---
if st.session_state["view_mode"] == "summary":
    st.subheader("✅ Your Meal Plan Summary")
    for day in days:
        st.write(f"**{day}:**")
        st.write(", ".join([f"{meal}: {st.session_state['dish_plan'][day][meal]}" for meal in meals if st.session_state['dish_plan'][day][meal]]))
    st.markdown("---")
    st.info("🤖 Generating your shopping list with AI... (this may take a few seconds)")
    ingredient_agent = get_ingredient_extractor_agent()
    all_ingredients = []
    for day in days:
        for meal in meals:
            dish = st.session_state["dish_plan"][day][meal].strip()
            if dish:
                with st.spinner(f"🧠 AI is extracting ingredients for '{dish}'..."):
                    ingredients = ingredient_agent.extract_ingredients(dish)
                all_ingredients.extend(ingredients)
    ingredient_counts = Counter(all_ingredients)
    st.success("🎉 Here's your AI-generated shopping list:")
    st.write("**Shopping List:**")
    for ingredient, count in ingredient_counts.items():
        st.write(f"- {ingredient} x{count}")
    st.write("🧠 Powered by OpenAI GPT-4o-mini for intelligent ingredient extraction!")
    st.button("🔄 Start Over", on_click=lambda: st.session_state.update({"view_mode": "day_by_day", "current_day_idx": 0})) 