import streamlit as st
from ollama import Client
import os
import re

# ============================================================
# PAGE SETUP & CONFIG
# ============================================================

st.set_page_config(
    page_title="AIpad",
    page_icon="✏️",
    layout="wide",
)

MODEL = "gpt-oss:20b-cloud"
LOGO_PATH = "welcome-modal-header.png"

SYSTEM_PROMPT = (
    "You are a text/code processing engine embedded in an app. "
    "Output ONLY the requested text or code, with no commentary "
    "before or after it. "
    "Never say things like 'Here is...', 'Sure, I...', 'Ok I...', "
    "or describe what you did. "
    "Do not wrap the output in markdown code fences unless the "
    "user's content itself is a code block that needs them. "
    "Your entire response is inserted directly into the user's "
    "document, so anything you write becomes part of it."
)


# ============================================================
# SESSION STATE
# ============================================================

# Initialize only the variables we actually use
for key in ["note", "error", "retry"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key == "note" else None


# ============================================================
# OLLAMA
# ============================================================

if "ollama_api_key" not in st.secrets:
    st.error("`ollama_api_key` was not found in Streamlit secrets.")
    st.stop()

@st.cache_resource
def get_ai_client(api_key):
    return Client(
        host="https://ollama.com",
        headers={"Authorization": f"Bearer {api_key}"},
    )

ai = get_ai_client(st.secrets["ollama_api_key"])


# ============================================================
# AI FUNCTIONS
# ============================================================

def strip_preamble(text):
    """Clean conversational filler and unnecessary markdown fences."""
    text = text.strip()

    # Strip wrapping markdown code fences safely using Regex
    if text.startswith("```") and text.endswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n|\n```$", "", text).strip()

    lines = text.split("\n")
    preambles = (
        "ok ", "okay ", "sure", "here", "certainly", "of course",
        "got it", "done", "this is", "below is", "the following"
    )

    # Strip leading preamble
    if len(lines) > 1 and lines[0].strip().lower().startswith(preambles) and len(lines[0]) < 120 and lines[1].strip() == "":
        lines = lines[2:]

    # Strip trailing postamble
    if len(lines) > 1 and lines[-1].strip().lower().startswith(preambles) and len(lines[-1]) < 120 and lines[-2].strip() == "":
        lines = lines[:-2]

    return "\n".join(lines).strip()


def run_ai(prompt, action):
    """Handle API requests and directly update the note in session state."""
    try:
        response = ai.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            stream=False # No need to stream since we wait to populate a text_area
        )
        
        result = strip_preamble(response.get("message", {}).get("content", ""))

        if not result:
            raise RuntimeError("The AI returned an empty response.")

        # Update note based on action
        if action == "generate":
            current_note = st.session_state.note.strip()
            st.session_state.note = f"{current_note}\n\n{result}".strip() if current_note else result
        else:
            st.session_state.note = result

        # Clear errors on success
        st.session_state.error = None
        st.session_state.retry = None

    except Exception as error:
        st.session_state.error = str(error)
        st.session_state.retry = (prompt, action)

# Callbacks for text inputs
def handle_generate():
    prompt = st.session_state.gen_input.strip()
    if prompt:
        run_ai(f"Generate the following. Return ONLY the requested text or code.\n\n{prompt}", "generate")
        st.session_state.gen_input = ""

def handle_rewrite():
    prompt = st.session_state.rew_input.strip()
    note = st.session_state.note.strip()
    
    if not note:
        st.warning("Write something first.")
    elif prompt:
        run_ai(f"{prompt}\n\nRewrite this:\n\n{note}", "rewrite")
        st.session_state.rew_input = ""


# ============================================================
# LAYOUT
# ============================================================

controls, editor = st.columns([1, 4], gap="large")

# ============================================================
# CONTROLS COLUMN
# ============================================================

with controls:
    st.subheader("AIPad Notes")

    # AI FIX
    if st.button("✨ AI Fix", use_container_width=True):
        if not st.session_state.note.strip():
            st.warning("Write something first.")
        else:
            run_ai(
                f"Fix the following text or code. Correct errors while preserving the original meaning. Return ONLY the fixed text or code.\n\n{st.session_state.note}",
                "fix"
            )

    # GENERATE
    st.text_input(
        "Generate",
        placeholder="Generate...",
        key="gen_input",
        label_visibility="collapsed",
        on_change=handle_generate,
    )

    # REWRITE
    st.text_input(
        "Rewrite",
        placeholder="Rewrite...",
        key="rew_input",
        label_visibility="collapsed",
        on_change=handle_rewrite,
    )

    # CLEAR
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.note = ""

    # LOGO
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.caption(f"Place an image at `{LOGO_PATH}` to show it here.")

    # ERROR PANEL
    if st.session_state.error:
        st.divider()
        st.error("AI request failed.")
        
        with st.expander("Details"):
            st.code(st.session_state.error)
            
        if st.session_state.retry:
            if st.button("🔄 Retry", use_container_width=True):
                prompt, action = st.session_state.retry
                st.session_state.error = None
                run_ai(prompt, action)
                st.rerun()


# ============================================================
# EDITOR COLUMN
# ============================================================

with editor:
    st.text_area(
        "Your note",
        height=330,
        placeholder="Start writing here...",
        key="note",
        label_visibility="collapsed",
    )