import time
import threading
import streamlit as st
import uuid

st.set_page_config(page_title="Gondoltam", page_icon="🍺", layout="centered")

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# CSS: Tömörítés és egyedi térközök
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stStatusWidget"] {display: none !important;}
    
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Cím alatti térköz */
    h1 { 
        font-size: 1.8rem !important; 
        margin-bottom: -15px !important; 
    }
    
    /* "Szabályok" felirat alatti extrém szűkítés */
    h3 { 
        font-size: 1.1rem !important; 
        margin-top: 0px !important; 
        margin-bottom: -12px !important; 
        padding-bottom: 0px !important;
    }
    
    /* Listaelemek (szabálypontok) */
    p, li { 
        font-size: 0.85rem !important; 
        line-height: 1.2 !important; 
        margin-bottom: 2px !important;
    }
    
    hr { margin-top: 0.3rem !important; margin-bottom: 0.3rem !important; }
    .stNumberInput, .stTextInput, .stRadio { margin-bottom: -15px !important; }
    
    [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_store():
    return {"lock": threading.Lock(), "rooms": {}}

def get_or_assign_role(room_code, user_id):
    store = get_store()
    with store["lock"]:
        if room_code not in store["rooms"]:
            store["rooms"][room_code] = {"A": None, "B": None, "updated": 0, "players": {}}
        room_state = store["rooms"][room_code]
        if "players" not in room_state: room_state["players"] = {}
        players = room_state["players"]
        if user_id in players: return players[user_id]
        taken_roles = players.values()
        role = "A" if "A" not in taken_roles else ("B" if "B" not in taken_roles else "A")
        players[user_id] = role
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

def get_room(room: str):
    store = get_store()
    with store["lock"]:
        return dict(store["rooms"].get(room, {"A": None, "B": None, "updated": 0, "players": {}}))

# --- FŐ LOGIKA ---
st.title("🍺 Gondoltam")

room_input = st.sidebar.text_input("Szoba", value="buli-1").strip()
room = room_input
room_state = get_room(room)
a, b = room_state.get("A"), room_state.get("B")
last_update = room_state.get("updated", 0)
assigned_role = get_or_assign_role(room, st.session_state.user_id)

# --- 1. ESET: VAN EREDMÉNY ---
if a is not None and b is not None:
    diff_abs = int(abs(a - b))
    elapsed = time.time() - last_update

    if elapsed < 2:
        popup_text = "BESZOPTAD!<br>HÚZÓRA! 💀" if diff_abs == 0 else f"Igyál {diff_abs} kortyot! 🍻"
        st.markdown(f"""
            <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; position: fixed; top: 0; left: 0; z-index: 9999; pointer-events: none; background-color: rgba(0,0,0,0.9); width: 100vw; height: 100vh;">
                <div style="font-size: 150px; animation: bounce 0.5s infinite alternate;">🍻</div>
                <div style="color: white; font-size: 50px; font-weight: bold; text-align: center; font-family: sans-serif; padding: 20px;">{popup_text}</div>
            </div>
            <style> @keyframes bounce {{ from {{ transform: scale(1); }} to {{ transform: scale(1.2); }} }} </style>
            """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="text-align: center; margin-top: 30px; margin-bottom: 10px;">
            <div style="font-size: 110px; font-weight: bold; line-height: 1; color: #FF4B4B;">{diff_abs}</div>
            <div style="font-size: 22px; margin-top: 15px; margin-bottom: 25px; font-weight: bold;">
                {'Különbség (korty)' if diff_abs != 0 else 'HÚZÓRA!'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("✨ ÚJ KÖR", use_container_width=True, type="primary"):
        reset_room(room)
        st.rerun()
    
    time.sleep(1)
    st.rerun()

# --- 2. ESET: JÁTÉK FOLYAMATBAN ---
else:
    st.markdown("""
    ### Szabályok:
    1. Ugyanaz a kód legyen a haverotokkal!
    2. Válasszátok ki, ki az A és B játékos!
    3. Mindketten írjatok be egy számot **1 és 10** között!
    4. Nyomjátok meg a **Gondoltam** gombot!
    5. Aki épp soron van, a különbséget meg kell, hogy igya!
    """)

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        room = st.text_input("Szoba kódja", value=room).strip()
    with c2:
        role_index = 0 if assigned_role == "A" else 1
        player = st.radio("Te vagy:", ["A", "B"], index=role_index, horizontal=True)

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
