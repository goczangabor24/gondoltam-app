import time
import threading
import streamlit as st

st.set_page_config(page_title="Gondoltam", page_icon="🍺", layout="centered")

# CSS trükk az elemek elrejtéséhez
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stStatusWidget"] {display: none !important;}
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

# --- CÍM (Ez mindig látszik) ---
st.title("🍺 Gondoltam")

# Adatok lekérése az elején
room_input = st.sidebar.text_input("Szoba (ha váltani akarsz)", value="buli-1").strip()
room = room_input # Használjuk a bemenetet
room_state = get_room(room)
a = room_state["A"]
b = room_state["B"]
last_update = room_state.get("updated", 0)

# --- EREDMÉNY NÉZET ---
# Ha mindketten beküldték, ez a blokk veszi át az irányítást
if a is not None and b is not None:
    diff_abs = int(abs(a - b))
    elapsed = time.time() - last_update

    # 1. ANIMÁCIÓ (Csak az első 2 másodpercben)
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

    # 2. TISZTA OLDAL (Csak a különbség és az új kör gomb)
    st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{diff_abs}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>{'Különbség (korty)' if diff_abs != 0 else 'HÚZÓRA!'}</h3>", unsafe_allow_html=True)
    
    st.write("")
    if st.button("✨ ÚJ KÖR", use_container_width=True, type="primary"):
        reset_room(room)
        st.rerun()
    
    # Itt megállítjuk a futást, így nem rajzolja ki a szabályokat és az inputokat
    time.sleep(1)
    st.rerun()
    st.stop()

# --- JÁTÉK NÉZET (Csak akkor látszik, ha nincs kész az eredmény) ---
st.markdown("""
### Szabályok:
1. Válassz egy kódot és oszd meg a haveroddal.
2. Mindketten írjatok be egy számot **1 és 10** között.
3. Nyomjátok meg a **Gondoltam** gombot.
""")

st.divider()

c1, c2 = st.columns(2)
with c1:
    # A szobakódot itt is megjelenítjük az elején
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
s1.metric(" 'A' játékos", "✅ Kész" if a is not None else "⏳ Vár...")
s2.metric(" 'B' játékos", "✅ Kész" if b is not None else "⏳ Vár...")

# Folyamatos frissítés, amíg várunk
time.sleep(1)
st.rerun()
