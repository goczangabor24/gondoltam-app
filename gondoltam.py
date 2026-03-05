import time
import threading
import streamlit as st

st.set_page_config(page_title="Gondoltam", page_icon="🍺", layout="centered")

# CSS trükk az elemek elrejtéséhez és a szövegméretekhez
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stStatusWidget"] {display: none !important;}
    /* Kisebb feliratok a státuszhoz */
    .small-status {
        font-size: 0.85rem;
        color: #888;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_store():
    return {
        "lock": threading.Lock(),
        "rooms": {}
    }

def submit_value(room: str, player: str, value: float):
    store = get_store()
    with store["lock"]:
        room_state = store["rooms"].setdefault(room, {"A": None, "B": None, "updated": 0})
        room_state[player] = value
        room_state["updated"] = int(time.time())

def reset_room(room: str):
    store = get_store()
    with store["lock"]:
        store["rooms"][room] = {"A": None, "B": None, "updated": int(time.time())}

def get_room(room: str):
    store = get_store()
    with store["lock"]:
        return dict(store["rooms"].get(room, {"A": None, "B": None, "updated": 0}))

# --- CÍM ---
st.title("🍺 Gondoltam")

# Adatok lekérése
room_input = st.sidebar.text_input("Szoba (ha váltani akarsz)", value="buli-1").strip()
room = room_input
room_state = get_room(room)
a = room_state["A"]
b = room_state["B"]
last_update = room_state.get("updated", 0)

# --- EREDMÉNY NÉZET ---
if a is not None and b is not None:
    diff_abs = int(abs(a - b))
    elapsed = time.time() - last_update

    if elapsed < 2:
        popup_text = "BESZOPTAD!<br>HÚZÓRA! 💀" if diff_abs == 0 else f"Igyál {diff_abs} kortyot! 🍻"
        st.markdown(
            f"""
            <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; position: fixed; top: 0; left: 0; z-index: 9999; pointer-events: none; background-color: rgba(0,0,0,0.9); width: 100vw; height: 100vh;">
                <div style="font-size: 150px; animation: bounce 0.5s infinite alternate;">🍻</div>
                <div style="color: white; font-size: 50px; font-weight: bold; text-align: center; font-family: sans-serif; padding: 20px;">{popup_text}</div>
            </div>
            <style>
            @keyframes bounce {{ from {{ transform: scale(1); }} to {{ transform: scale(1.2); }} }}
            </style>
            """,
            unsafe_allow_html=True
        )

    st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{diff_abs}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>{'Kortyszám' if diff_abs != 0 else 'HÚZÓRA!'}</h3>", unsafe_allow_html=True)
    
    st.write("")
    if st.button("✨ ÚJ KÖR", use_container_width=True, type="primary"):
        reset_room(room)
        st.rerun()
    
    time.sleep(1)
    st.rerun()
    st.stop()

# --- JÁTÉK NÉZET ---

# 1. SZABÁLYOK (Kicsiben)
st.markdown("""
<small>
<b>Szabályok:</b> 1. Közös kód. 2. Szám 1-10 között. 3. Gondoltam gomb. 
4. Soron lévő issza a különbséget. 5. Telitalálatnál húzóra!
</small>
""", unsafe_allow_html=True)

st.divider()

# 2. ÁLLAPOT (Kisebb formátumban, a beviteli mezők előtt)
s1, s2 = st.columns(2)
with s1:
    txt_a = "✅ Kész" if a is not None else "⏳ Mivanmá...?"
    st.markdown(f"<div class='small-status'>'A' játékos: {txt_a}</div>", unsafe_allow_html=True)
with s2:
    txt_b = "✅ Kész" if b is not None else "⏳ Mivanmá...?"
    st.markdown(f"<div class='small-status'>'B' játékos: {txt_b}</div>", unsafe_allow_html=True)

st.write("") # Kis helyköz

# 3. BEVITELI MEZŐK
c1, c2 = st.columns(2)
with c1:
    room = st.text_input("Szoba kódja", value=room).strip()
with c2:
    player = st.radio("Te vagy:", ["A", "B"], horizontal=True)

value = st.number_input("Melyik számra gondoltál? (1-10)", min_value=1.0, max_value=10.0, value=1.0, step=1.0, format="%.0f")

if st.button("Gondoltam", use_container_width=True, type="primary"):
    submit_value(room, player, float(value))
    st.rerun()

# Folyamatos frissítés
time.sleep(1)
st.rerun()
