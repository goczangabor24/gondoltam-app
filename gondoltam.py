import time
import threading
import streamlit as st
import uuid

st.set_page_config(page_title="Gondoltam", page_icon="🍺", layout="centered")

# Egyedi azonosító a böngészőhöz
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# CSS: Maximális tömörítés és térköz-eltüntetés
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
        margin-bottom: -25px !important; 
        padding-bottom: 0px !important;
    }
    
    /* "Szabályok" felirat alatti és feletti térköz */
    h3 { 
        font-size: 1.1rem !important; 
        margin-top: 0px !important; 
        margin-bottom: -15px !important; 
        padding-bottom: 0px !important;
    }
    
    /* Listaelemek (szabálypontok) közötti hézag */
    p, li { 
        font-size: 0.85rem !important; 
        line
