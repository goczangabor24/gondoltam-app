import time
import threading
import streamlit as st
import uuid

st.set_page_config(page_title="Gondoltam", page_icon="🍺", layout="centered")

# Egyedi azonosító a böngészőhöz
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# CSS: Csak a tömörítés marad, az egymás mellett tartást kivettem
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stStatusWidget"] {display: none !important;}
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    h1 { font-size: 1.8rem !important; margin-bottom: 0.5rem !important; }
    h3 { font-size: 1.1rem !important; margin-top: 0.5rem !important; margin-bottom: 0.5rem !important; }
    p, li { font-size: 0.85rem !important; line-height: 1.2 !important; }
    div.stMarkdown { margin-bottom: -10px !important; }
    
    hr { margin-top: 0.5rem !important; margin-bottom: 0.5rem !important; }
    .stNumberInput, .stTextInput, .stRadio { margin-bottom: -15px !important; }
    
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

def get_or_assign_role(room_code, user_id):
    store = get_store()
    with store["lock"]:
        # Biztonságos inicializálás
        if room_code not in store["rooms"]:
            store["rooms"][room_code] = {"A": None, "B": None, "updated": 0, "players": {}}
        
        room_state = store["rooms"][room_code]
        
        # Ha a szoba létezett régebbről, de nem volt players kulcsa, létrehozzuk
        if "players" not in room_state:
            room_state["players"] = {}
            
        players = room_state["players"]
        
        if user_id in players:
            return players[user_id]
        
        taken_roles = players.values()
        if "A" not in taken_roles:
            players[user_id] = "A"
        elif "B" not in taken_roles:
            players[user_id] = "B"
        else:
            players[user_id] = "A"
        
        return players[user_id]

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
            store["rooms"][room]["updated
