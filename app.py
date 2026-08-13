import streamlit as st
from ollama import Client

# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="AIpad",
    page_icon="📝",
    layout="wide",
)

# ============================================================
# CONFIG
# ============================================================

MODEL_OPTIONS = {
    "Nvidia Nemotron 3 Nano": "nemotron-3-nano:30b-cloud",
    "ChatGPT-OSS": "gpt-oss:20b-cloud",
    "Google Gemma 4": "gemma4:31b-cloud",
}
DEFAULT_MODEL_LABEL = "Nvidia Nemotron 3 Nano"

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

defaults = {
    "note": "",
    "panel": None,
    "error": None,
    "retry": None,
    "trigger_generate": None,
    "trigger_rewrite": None,
    "model_label": DEFAULT_MODEL_LABEL,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# OLLAMA
# ============================================================

if "ollama_api_key" not in st.secrets:
    st.error("`ollama_api_key` was not found in Streamlit secrets.")
    st.stop()

OLLAMA_API_KEY = st.secrets["ollama_api_key"]

@st.cache_resource
def get_ai_client(api_key):
    return Client(
        host="https://ollama.com",
        headers={
            "Authorization": f"Bearer {api_key}"
        },
    )

ai = get_ai_client(OLLAMA_API_KEY)

# ============================================================
# AI
# ============================================================

def strip_preamble(text):
    """Remove a leading/trailing conversational line that some models
    add despite instructions, e.g. 'Ok I humanized it.' Only strips
    a line that is clearly its own paragraph (separated by a blank
    line from the real content), so real content is never touched."""
    text = text.strip()

    preamble_starts = (
        "ok ", "okay ", "sure", "here", "certainly", "of course",
        "got it", "done", "this is", "below is", "the following",
    )

    lines = text.split("\n")

    # Leading preamble: first line matches AND is followed by a blank line
    if (
        len(lines) > 1
        and lines[0].strip().lower().startswith(preamble_starts)
        and len(lines[0]) < 120
        and lines[1].strip() == ""
    ):
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines.pop(0)

    # Trailing postamble: last line matches AND is preceded by a blank line
    if (
        len(lines) > 1
        and lines[-1].strip().lower().startswith(preamble_starts)
        and len(lines[-1]) < 120
        and lines[-2].strip() == ""
    ):
        lines = lines[:-1]
        while lines and not lines[-1].strip():
            lines.pop()

    text = "\n".join(lines).strip()

    # Strip a single wrapping ```...``` fence if the whole response is one
    if text.startswith("```") and text.endswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:-3].strip()

    return text

def ask_ai(prompt):
    response = ai.chat(
        model=MODEL_OPTIONS[st.session_state.model_label],
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        stream=True,
    )

    result = ""
    for chunk in response:
        content = chunk.get("message", {}).get("content", "")
        if content:
            result += content

    return strip_preamble(result)

def run_ai(prompt, action, title_placeholder=None):
    try:
        if title_placeholder is not None:
            with title_placeholder.container():
                with st.spinner("📝 AIpad"):
                    result = ask_ai(prompt)
            title_placeholder.subheader("📝 AIpad")
        else:
            result = ask_ai(prompt)

        if not result.strip():
            raise RuntimeError("The AI returned an empty response.")

        if action == "generate":
            if st.session_state.note.strip():
                st.session_state.note += "\n\n" + result
            else:
                st.session_state.note = result
        else:
            st.session_state.note = result

        st.session_state.panel = None
        st.session_state.error = None
        st.session_state.retry = None

        st.rerun()

    except Exception as error:
        st.session_state.error = str(error)
        st.session_state.retry = (prompt, action)

# ============================================================
# LAYOUT
# ============================================================

controls, editor = st.columns(
    [1, 4],
    gap="large",
)

# ============================================================
# CONTROLS (Left Sidebar)
# ============================================================

with controls:
    title_placeholder = st.empty()
    title_placeholder.subheader("📝 AIpad")

    # ========================================================
    # MODEL SELECTOR
    # ========================================================
    st.selectbox(
        "Model",
        options=list(MODEL_OPTIONS.keys()),
        key="model_label",
        label_visibility="collapsed",
    )

    # ========================================================
    # AI FIX
    # ========================================================
    if st.button("✨ AI Fix", use_container_width=True):
        note = st.session_state.note.strip()
        if not note:
            st.warning("Write something first.")
        else:
            run_ai(
                (
                    "Fix the following text or code. "
                    "Correct errors while preserving "
                    "the original meaning. "
                    "Return ONLY the fixed text or code.\n\n"
                    + note
                ),
                "fix",
                title_placeholder,
            )

    # ========================================================
    # GENERATE
    # ========================================================
    def handle_generate():
        prompt = st.session_state.generate_input_box.strip()
        if prompt:
            st.session_state.trigger_generate = prompt
        st.session_state.generate_input_box = ""

    st.text_input(
        "Generate",
        placeholder="Generate...",
        key="generate_input_box",
        label_visibility="collapsed",
        on_change=handle_generate,
    )

    if st.session_state.trigger_generate:
        prompt_to_run = st.session_state.trigger_generate
        st.session_state.trigger_generate = None  # Reset flag immediately
        run_ai(
            (
                "Generate the following. "
                "Return ONLY the requested "
                "text or code.\n\n"
                + prompt_to_run
            ),
            "generate",
            title_placeholder,
        )

    # ========================================================
    # REWRITE
    # ========================================================
    def handle_rewrite():
        prompt = st.session_state.rewrite_input_box.strip()
        if prompt:
            st.session_state.trigger_rewrite = prompt
        st.session_state.rewrite_input_box = ""

    st.text_input(
        "Rewrite",
        placeholder="Rewrite...",
        key="rewrite_input_box",
        label_visibility="collapsed",
        on_change=handle_rewrite,
    )

    if st.session_state.trigger_rewrite:
        instructions = st.session_state.trigger_rewrite
        st.session_state.trigger_rewrite = None  # Reset flag immediately
        note = st.session_state.note.strip()

        if not note:
            st.warning("Write something first.")
        else:
            run_ai(
                (
                    instructions
                    + "\n\nRewrite this:\n\n"
                    + note
                ),
                "rewrite",
                title_placeholder,
            )

    # ========================================================
    # CLEAR
    # ========================================================
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.note = ""
        st.session_state.panel = None

    # ========================================================
    # ERROR PANEL
    # ========================================================
    if st.session_state.error:
        st.divider()
        st.error("AI request failed.")

        with st.expander("Details"):
            st.code(st.session_state.error)

        if st.session_state.retry:
            if st.button("🔄 Retry", use_container_width=True):
                prompt, action = st.session_state.retry
                st.session_state.error = None
                run_ai(prompt, action, title_placeholder)

# ============================================================
# EDITOR (Right Main Area)
# ============================================================

with editor:
    st.text_area(
        "Your note",
        height=330,
        placeholder="Start writing here...",
        key="note",
        label_visibility="collapsed",
    )