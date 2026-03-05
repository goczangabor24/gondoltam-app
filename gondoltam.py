import time
import threading
import streamlit as st

st.set_page_config(page_title="Gondoltam", page_icon="🍺", layout="centered")

@st.cache_resource
def get_store():
    # Közös tárhely a szerveren minden session számára
    return {
        "lock": threading.Lock(),
        "rooms": {}  # room_code -> {"A": float|None, "B": float|None, "updated": int}
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

# Egyszerű lista a lenyíló fül helyett
st.markdown("""
### Szabályok:
1. Válassz egy kódot és oszd meg a haveroddal.
2. Mindketten írjatok be egy számot 1 és 10 között.
3. Nyomjátok meg a **Gondoltam** gombot.
4. A különbséget a soron következőnek meg kell innia! 🍻
""")

st.divider()

c1, c2 = st.columns(2)
with c1:
    room = st.text_input("Szoba kódja", value="buli-1").strip()
with c2:
    player = st.radio("Te vagy:", ["A", "B"], horizontal=True)

if not room:
    st.warning("Adj meg egy szobakódot!")
    st.stop()

# Itt korlátoztam 1 és 10 közé a választást
value = st.number_input("Melyik számra gondoltál? (1-10)", min_value=1.0, max_value=10.0, value=1.0, step=1.0, format="%.0f")

col_submit, col_reset = st.columns([2, 1])

with col_submit:
    if st.button("Gondoltam", use_container_width=True, type="primary"):
        submit_value(room, player, float(value))
        st.success("Szám rögzítve!")
        time.sleep(1)
        st.rerun()

with col_reset:
    if st.button("Új kör", use_container_width=True):
        reset_room(room)
        st.rerun()

st.divider()

# Adatok lekérése
room_state = get_room(room)
a = room_state["A"]
b = room_state["B"]

st.subheader("Állapot")
s1, s2 = st.columns(2)

# Jelzés, ha valaki már beküldte
s1.metric(" 'A' játékos", "✅ Kész" if a is not None else "⏳ Mivanmá?")
s2.metric(" 'B' játékos", "✅ Kész" if b is not None else "⏳ Mivanmá?")

st.divider()

# Eredmény megjelenítése
if a is not None and b is not None:
    diff_abs = abs(a - b)
    
    res1, res2, res3 = st.columns(3)
    res1.write(f"**A** száma: {a:g}")
    res2.write(f"**B** száma: {b:g}")
    res3.write(f"**Különbség:** {diff_abs:g}")
    
    st.balloons()
    st.success(f"A különbség **{diff_abs:g}**! Egészségedre! 🍻")
else:
    st.info("Innék...")

# Automatikus frissítés a háttérben (1 másodpercenként)
time.sleep(1)
st.rerun()