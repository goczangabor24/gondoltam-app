import time
import threading
import streamlit as st
import uuid

st.set_page_config(page_title="Gondoltam", page_icon="🍺", layout="centered")

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

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
    
    h1 { 
        font-size: 1.8rem !important; 
        margin-bottom: 0px !important; 
        padding-bottom: 0px !important;
    }
    
    h3 { 
        font-size: 1.1rem !important; 
        margin-top: 0px !important; 
        margin-bottom: 2px !important; 
        padding-top: 0px !important;
    }
    
    p, li { 
        font-size: 0.85rem !important; 
        line-height: 1.1 !important; 
        margin-bottom: 1px !important;
        margin-top: 0px !important;
    }
    
    .element-container, .stMarkdown {
        margin-bottom: 0px !important;
    }
    
    hr { margin-top: 0.5rem !important; margin-bottom: 0.5rem !important; }
    .stNumberInput, .stTextInput, .stRadio { margin-bottom: -10px !important; }
    
    [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_store():
    return {"lock": threading.Lock(), "rooms": {}}

def ensure_room(room_code):
    store = get_store()
    with store["lock"]:
        if room_code not in store["rooms"]:
            store["rooms"][room_code] = {
                "A": None,
                "B": None,
                "updated": 0,
                "players": {},
                "submitted_roles": {},
                "error": None,
            }

def get_or_assign_role(room_code, user_id):
    ensure_room(room_code)
    store = get_store()
    with store["lock"]:
        room_state = store["rooms"][room_code]
        players = room_state["players"]

        if user_id in players:
            return players[user_id]

        taken_roles = players.values()
        role = "A" if "A" not in taken_roles else ("B" if "B" not in taken_roles else "A")
        players[user_id] = role
        return role

def submit_value(room: str, user_id: str, player: str, value: float):
    ensure_room(room)
    store = get_store()
    with store["lock"]:
        room_state = store["rooms"][room]

        # eltároljuk, ki milyen role-lal küldött be
        room_state["submitted_roles"][user_id] = player

        # eltároljuk a választott számot
        room_state[player] = value
        room_state["updated"] = int(time.time())
        room_state["error"] = None

        submitted_roles = list(room_state["submitted_roles"].values())

        # ha már két külön user küldött be, ellenőrizzük a szerepeket
        if len(room_state["submitted_roles"]) >= 2:
            first_two = submitted_roles[:2]
            if first_two[0] == first_two[1] == "A":
                room_state["A"] = None
                room_state["B"] = None
                room_state["submitted_roles"] = {}
                room_state["updated"] = int(time.time())
                room_state["error"] = "Hülyék, nem lehettek mindketten A játékosok!"
            elif first_two[0] == first_two[1] == "B":
                room_state["A"] = None
                room_state["B"] = None
                room_state["submitted_roles"] = {}
                room_state["updated"] = int(time.time())
                room_state["error"] = "Hülyék, nem lehettek mindketten B játékosok!"

def reset_room(room: str):
    ensure_room(room)
    store = get_store()
    with store["lock"]:
        store["rooms"][room]["A"] = None
        store["rooms"][room]["B"] = None
        store["rooms"][room]["updated"] = int(time.time())
        store["rooms"][room]["submitted_roles"] = {}
        store["rooms"][room]["error"] = None

def get_room(room: str):
    ensure_room(room)
    store = get_store()
    with store["lock"]:
        return dict(store["rooms"][room])

# --- UI ---
st.title("🍺 Gondoltam")

room_input = st.sidebar.text_input("Szoba", value="kecskesajt").strip()
room = room_input

init_key = f"initialized_{room}"
if init_key not in st.session_state:
    reset_room(room)
    st.session_state[init_key] = True

room_state = get_room(room)
a, b = room_state.get("A"), room_state.get("B")
last_update = room_state.get("updated", 0)
error_message = room_state.get("error")
assigned_role = get_or_assign_role(room, st.session_state.user_id)

# --- HIBA NÉZET ---
if error_message:
    st.markdown(f"""
        <div style="text-align:center; margin-top: 60px;">
            <div style="font-size: 80px;">🚫</div>
            <div style="font-size: 28px; font-weight: bold; color: #FF4B4B; margin-top: 20px;">
                {error_message}
            </div>
            <div style="font-size: 18px; margin-top: 20px;">
                Az oldal újratölt...
            </div>
        </div>
    """, unsafe_allow_html=True)

    time.sleep(2)
    reset_room(room)
    st.rerun()

elif a is not None and b is not None:
    # --- EREDMÉNY NÉZET ---
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
        <div style="text-align: center; margin-top: 20px; margin-bottom: 10px;">
            <div style="font-size: 110px; font-weight: bold; line-height: 1; color: #FF4B4B;">{diff_abs}</div>
            <div style="font-size: 22px; margin-top: 10px; margin-bottom: 20px; font-weight: bold;">
                {'Különbség (korty)' if diff_abs != 0 else 'HÚZÓRA!'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("✨ ÚJ KÖR", use_container_width=True, type="primary"):
        reset_room(room)
        st.rerun()
    
    time.sleep(1)
    st.rerun()

else:
    # --- JÁTÉK NÉZET ---
    st.markdown("""
    ### Szabályok:
    1. Ugyanaz a szoba kód legyen a haverotokkal!
    2. Válasszátok ki, ki az A és B játékos!
    3. Az első játékos gondoljon egy számra, **1 és 10** között!
    4. A második játékos próbálja meg kitalálni, ha nem sikerült, a különbséget meg kell innia!
    5. Ha sikerül kitalálni, az első játékosnak kell húzóra meginnia, ami előtte van!
    6. Cserélgessétek felváltva ki gondol és ki tippel!
    """)

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        room = st.text_input("Szoba kódja", value=room).strip()
    with c2:
        role_index = 0 if assigned_role == "A" else 1
        player = st.radio("Te vagy:", ["A", "B"], index=role_index, horizontal=True)

    value = st.number_input(
        "Melyik számra gondoltál? (1-10)",
        min_value=1.0,
        max_value=10.0,
        value=1.0,
        step=1.0,
        format="%.0f"
    )

    if st.button("Gondoltam", use_container_width=True, type="primary"):
        submit_value(room, st.session_state.user_id, player, float(value))
        st.rerun()

    st.divider()
    st.subheader("Állapot")
    s1, s2 = st.columns(2)
    s1.metric(" 'A' játékos", "✅ Kész" if a is not None else "⏳ Mivanmá...?")
    s2.metric(" 'B' játékos", "✅ Kész" if b is not None else "⏳ Mivanmá...?")

    time.sleep(1)
    st.rerun()

