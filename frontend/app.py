import os
from aiohttp import payload
import requests
import streamlit as st

BACKEND = os.getenv('BACKEND_BASE_URL', 'http://localhost:8000')

st.set_page_config(page_title='Pharma Flashcards', page_icon="💊")
st.title('💊 Pharmacology Flashcards')

if 'backend_id' not in st.session_state:
    st.session_state.backend_id = None
    st.session_state.question = None
    st.session_state.options = []

col1, col2 = st.columns(2)
with col1:
    if st.button('New Card'):
        r = requests.get(f'{BACKEND}/card/random', timeout=30)
        r.raise_for_status()
        card = r.json()
        st.session_state.backend_id = card['backend_id']
        st.session_state.question = card['question']
        st.session_state.options = card['options']

if st.session_state.backend_id is not None:
    st.subheader('Current Card')
    st.write(st.session_state.question)
    idx = st.radio(
        'Your Answer:',
        options=range(len(st.session_state.options)),
        format_func=lambda i: st.session_state.options[i],
    )

    if st.button('Submit Answer'):
        payload = {
            'backend_id': st.session_state.backend_id,
            'user_answer': int(idx)
        }
        r = requests.post(f'{BACKEND}/card/answer', json=payload, timeout=30)
        r.raise_for_status()
        res = r.json()

        if res['correct']:
            st.success(res['message'])
        else:
            st.error(res['message'])
else:
    st.info('Click "New Card" to get your first card')
