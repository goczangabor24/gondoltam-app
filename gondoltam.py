import time
import threading
import streamlit as st

st.set_page_config(page_title="Gondoltam", page_icon="🍺", layout="centered")

# Egyedi böngésző azonosító létrehozása
if "user_id" not in st.session_state:
    st.session_state.user_id = str(time.time())

# CSS: Tömörítés
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stStatusWidget"] {display: none !important;}
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    h1 { font-size: 1.8rem !important; margin-bottom: 0.5rem !important; }
    h3 { font-size: 1.1rem !important; margin-top: 0.5rem !important; margin-bottom: 0.5rem !important; }
    p, li { font-size: 0.85rem !important; line-height: 1.2 !important; }
    hr { margin-top: 0.5rem !important; margin-bottom: 0.5rem !important; }
    .stNumberInput, .stTextInput, .stRadio { margin-bottom: -15px !important; }
    [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_store():
    return {"lock": threading.Lock(), "rooms": {}}

def get_assigned_role(room_code, user_id):
    store = get_store()
    with store["lock"]:
        # Szoba inicializálása ha nem létezik
        if room_code not in store["rooms"]:
            store["rooms"][room_code] = {"A": None, "B": None, "updated": 0, "players": {}}
        
        room_data = store["rooms"][room_code]
        
        # Ha a felhasználónak már van kiosztott szerepe, azt adjuk vissza
        if user_id in room_data["players"]:
            return room_data["players"][user_id]
        
        # Kiosztás: ki foglalt már helyet?
        assigned = room_data["players"].values()
        if "A" not in assigned:
            role = "A"
        elif "B" not in assigned:
            role = "B"
        else:
            role = "A" # Harmadik embernek alapértelmezett, de manuálisan válthat
            
        room_data["players"][user_id] = role
        return role

def submit_value(room: str, player: str, value: float):
    store = get_store()
    with store["lock"]:
        room_state = store["rooms"].setdefault(room, {"A": None, "B": None, "updated": 0, "players": {}})
        room_state[player] = value
        room_state["updated"] = int(time.time())

def reset_room(room: str):
    store = get_store()
    with store["lock"]:
        if room in store["rooms"]:
            store["rooms"][room]["A"] = None
            store["rooms"][room]["B"] = None
            store["rooms"][room]["updated"] = int(time.time())

def get_room_status(room: str):
    store = get_store()
    with store["lock"]:
        return dict(store["rooms"].get(room, {"A": None, "B": None, "updated": 0, "players": {}}))

# --- UI ---
st.title("🍺 Gondoltam")

# Szoba kezelése
room = st.sidebar.text_input("Szoba", value="buli-1").strip()
if not room:
    st.warning("Adj meg egy szobakódot!")
    st.stop()

# Szerep kiosztása
assigned_role = get_assigned_role(room, st.session_state.user_id)
room_state = get_room_status(room)
a = room_state.get("A")
b = room_state.get("B")

# --- EREDMÉNY NÉZET ---
if a is not None and b is not None:
    diff_abs = int(abs(a - b))
    if int(time.time()) - room_state.get("updated", 0) < 2:
        popup_text = "BESZOPTAD!<br>HÚZÓRA! 💀" if diff_abs == 0 else f"Igyál {diff_abs} kortyot! 🍻"
        st.markdown(f"""
            <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; position: fixed; top: 0; left: 0; z-index: 9999; pointer-events: none; background-color: rgba(0,0,0,0.9); width: 100vw; height: 100vh;">
                <div style="font-size: 150px; animation: bounce 0.5s infinite alternate;">🍻</div>
                <div style="color: white; font-size: 50px; font-weight: bold; text-align: center; font-family: sans-serif; padding: 20px;">{popup_text}</div>
            </div>
            <style> @keyframes bounce {{ from {{ transform: scale(1); }} to {{ transform: scale(1.2); }} }} </style>
            """, unsafe_allow_html=True)

    st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{diff_abs}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>{'Különbség (korty)' if diff_abs != 0 else 'HÚZÓRA!'}</h3>", unsafe_allow_html=True)
    
    if st.button("✨ ÚJ KÖR", use_container_width=True, type="primary"):
        reset_room(room)
        st.rerun()
    st.stop()

# --- JÁTÉK NÉZET ---
st.markdown("### Szabályok:\n1. Közös kód. 2. Szám 1-10. 3. Gondoltam gomb. 4. Különbség = korty. 5. Telitalálat = Húzóra!")
st.divider()

c1, c2 = st.columns(2)
with c1:
    room_display = st.text_input("Szoba kódja", value=room).strip()
with c2:
    # Itt dől el az automata kiosztás:
    role_idx = 0 if assigned_role == "A" else 1
    player = st.radio("Te vagy:", ["A", "B"], index=role_idx, horizontal=True)

value = st.number_input("Melyik számra gondoltál? (1-10)", min_value=1.0, max_value=10.0, value=1.0, step=1.0, format="%.0f")

if st.button("Gondoltam", use_container_width=True, type="primary"):
    submit_value(room, player, float(value))
    st.rerun()

st.divider()
st.subheader("Állapot")
s1, s2 = st.columns(2)
s1.metric("'A' játékos", "✅ Kész" if a is not None else "⏳ Mivanmá...?")
s2.metric("'B' játékos", "✅ Kész" if b is not None else "⏳ Mivanmá...?")

time.sleep(1)
st.rerun()
