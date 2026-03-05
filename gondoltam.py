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

# --- UI ---
st.title("🍺 Gondoltam")

st.markdown("""
### Szabályok:
1. Válassz egy kódot és oszd meg a haveroddal.
2. Mindketten írjatok be egy számot **1 és 10** között.
3. Nyomjátok meg a **Gondoltam** gombot.
""")

st.divider()

# Szoba és játékos választás
c1, c2 = st.columns(2)
with c1:
    room = st.text_input("Szoba kódja", value="buli-1").strip()
with c2:
    player = st.radio("Te vagy:", ["A", "B"], horizontal=True)

if not room:
    st.warning("Adj meg egy szobakódot!")
    st.stop()

room_state = get_room(room)
a = room_state["A"]
b = room_state["B"]
last_update = room_state.get("updated", 0)

# Szám bevitele - Csak akkor látszik, ha még nincs meg mindkét eredmény
if a is None or b is None:
    value = st.number_input("Melyik számra gondoltál? (1-10)", min_value=1.0, max_value=10.0, value=1.0, step=1.0, format="%.0f")
    if st.button("Gondoltam", use_container_width=True, type="primary"):
        submit_value(room, player, float(value))
        st.rerun()

st.divider()

st.subheader("Állapot")
s1, s2 = st.columns(2)
s1.metric(" 'A' játékos", "✅ Kész" if a is not None else "⏳ Vár...")
s2.metric(" 'B' játékos", "✅ Kész" if b is not None else "⏳ Vár...")

# EREDMÉNY ÉS ANIMÁCIÓ
if a is not None and b is not None:
    st.divider()
    diff_abs = int(abs(a - b))
    
    # Felugró animáció szövege
    if diff_abs == 0:
        popup_text = "BESZOPTAD!<br>HÚZÓRA! 💀"
    else:
        popup_text = f"Igyál {diff_abs} kortyot! 🍻"
    
    # Animáció megjelenítése (3 másodpercig)
    if int(time.time()) - last_update < 3:
        st.markdown(
            f"""
            <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; position: fixed; top: 0; left: 0; z-index: 9999; pointer-events: none; background-color: rgba(0,0,0,0.85); width: 100vw; height: 100vh;">
                <div style="font-size: 150px; animation: bounce 0.5s infinite alternate;">🍻</div>
                <div style="color: white; font-size: 50px; font-weight: bold; text-align: center; font-family: sans-serif; padding: 20px;">{popup_text}</div>
            </div>
            <style>
            @keyframes bounce {{
                from {{ transform: scale(1); }}
                to {{ transform: scale(1.2); }}
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

    # Részletes eredmények
    res1, res2, res3 = st.columns(3)
    res1.write(f"**A** száma: **{a:g}**")
    res2.write(f"**B** száma: **{b:g}**")
    res3.write(f"**Különbség:** **{diff_abs}**")
    
    if diff_abs == 0:
        st.error("### BESZOPTAD, HÚZÓRA! 💀")
    else:
        st.success(f"Igyál {diff_abs} kortyot! 🍻")

    # ÚJ KÖR GOMB - Csak az eredmény után ugrik fel
    st.write("") 
    if st.button("✨ Új kör", use_container_width=True):
        reset_room(room)
        st.rerun()
else:
    st.info("Várakozás a másikra...")

# Automatikus frissítés
time.sleep(1)
st.rerun()
