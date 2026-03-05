import time
import threading
import streamlit as st

st.set_page_config(page_title="Gondoltam", page_icon="🍺", layout="centered")

# CSS trükk: Tömörítés + Oszlopok egymás mellett tartása mobilon
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stStatusWidget"] {display: none !important;}
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    
    h1 { font-size: 1.6rem !important; margin-bottom: 0.3rem !important; }
    h3 { font-size: 1rem !important; margin-top: 0.3rem !important; }
    p, li { font-size: 0.8rem !important; line-height: 1.1 !important; }
    
    /* Ez kényszeríti az oszlopokat egymás mellé mobilon is */
    [data-testid="column"] {
        width: 48% !important;
        flex: 1 1 45% !important;
        min-width: 45% !important;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 10px !important;
    }

    /* Metric zsugorítás */
    [data-testid="stMetricValue"] { font-size: 1rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
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
room_input = st.sidebar.text_input("Szoba", value="buli-1").strip()
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
                <div style="font-size: 120px; animation: bounce 0.5s infinite alternate;">🍻</div>
                <div style="color: white; font-size: 40px; font-weight: bold; text-align: center; font-family: sans-serif; padding: 20px;">{popup_text}</div>
            </div>
            <style>
            @keyframes bounce {{ from {{ transform: scale(1); }} to {{ transform: scale(1.2); }} }}
            </style>
            """,
            unsafe_allow_html=True
        )

    st.markdown(f"<h1 style='text-align: center; font-size: 70px; margin-top: 10px;'>{diff_abs}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; margin-bottom: 20px;'>{'Különbség (korty)' if diff_abs != 0 else 'HÚZÓRA!'}</h3>", unsafe_allow_html=True)
    
    if st.button("✨ ÚJ KÖR", use_container_width=True, type="primary"):
        reset_room(room)
        st.rerun()
    
    time.sleep(1)
    st.rerun()
    st.stop()

# --- JÁTÉK NÉZET ---
st.markdown("""
### Szabályok:
1. Ugyanaz a kód! 2. Szám 1-10 között. 3. Gondoltam gomb. 4. Soron lévő issza a különbséget. 5. Telitalálatnál húzóra!
""")

st.divider()

# ÁLLAPOT - Most már kényszerítve egymás mellé
s1, s2 = st.columns(2)
s1.metric(" 'A' játékos", "✅ Kész" if a is not None else "⏳ Vár...")
s2.metric(" 'B' játékos", "✅ Kész" if b is not None else "⏳ Vár...")

st.divider()

c1, c2 = st.columns(2)
with c1:
    room = st.text_input("Szoba kódja", value=room).strip()
with c2:
    player = st.radio("Te vagy:", ["A", "B"], horizontal=True)

value = st.number_input("Szám (1-10)", min_value=1.0, max_value=10.0, value=1.0, step=1.0, format="%.0f")

if st.button("Gondoltam", use_container_width=True, type="primary"):
    submit_value(room, player, float(value))
    st.rerun()

time.sleep(1)
st.rerun()
