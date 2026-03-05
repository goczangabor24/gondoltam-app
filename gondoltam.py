import time
import threading
import streamlit as st

st.set_page_config(page_title="Gondoltam", page_icon="🍺", layout="centered")

# CSS trükk a tömörítéshez: margók, paddingek és betűméretek csökkentése
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stStatusWidget"] {display: none !important;}
    
    /* Teljes oldal margójának nullázása */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Cím és szövegek méretének csökkentése */
    h1 { font-size: 1.8rem !important; margin-bottom: 0.5rem !important; }
    h3 { font-size: 1.1rem !important; margin-top: 0.5rem !important; margin-bottom: 0.5rem !important; }
    p, li { font-size: 0.85rem !important; line-height: 1.2 !important; }
    div.stMarkdown { margin-bottom: -10px !important; }
    
    /* Divider közének csökkentése */
    hr { margin-top: 0.5rem !important; margin-bottom: 0.5rem !important; }
    
    /* Inputok és gombok közötti távolság */
    .stNumberInput, .stTextInput, .stRadio { margin-bottom: -15px !important; }
    
    /* Metric widgetek zsugorítása */
    [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
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
    st.markdown(f"<h3 style='text-align: center;'>{'Különbség (korty)' if diff_abs != 0 else 'HÚZÓRA!'}</h3>", unsafe_allow_html=True)
    
    if st.button("✨ ÚJ KÖR", use_container_width=True, type="primary"):
        reset_room(room)
        st.rerun()
    
    time.sleep(1)
    st.rerun()
    st.stop()

# --- JÁTÉK NÉZET ---
st.markdown("""
### Szabályok:
1. Ugyanaz a kód legyen a haverotokkal!
2. Mindketten írjatok be egy számot **1 és 10** között.
3. Nyomjátok meg a **Gondoltam** gombot.
4. Aki épp soron van, a különbséget meg kell, hogy igya.
5. Ha eltalálja mire gondolt a másik, húzóra kell meginnia, annak, aki gondolt.
""")

st.divider()

c1, c2 = st.columns(2)
with c1:
    room = st.text_input("Szoba kódja", value=room).strip()
with c2:
    player = st.radio("Te vagy:", ["A", "B"], horizontal=True)

value = st.number_input("Melyik számra gondoltál? (1-10)", min_value=1.0, max_value=10.0, value=1.0, step=1.0, format="%.0f")

if st.button("Gondoltam", use_container_width=True, type="primary"):
    submit_value(room, player, float(value))
    st.rerun()

st.divider()
st.subheader("Állapot")
s1, s2 = st.columns(2)
s1.metric(" 'A' játékos", "✅ Kész" if a is not None else "⏳ Mivanmá...?")
s2.metric(" 'B' játékos", "✅ Kész" if b is not None else "⏳ Mivanmá...?")

time.sleep(1)
st.rerun()
