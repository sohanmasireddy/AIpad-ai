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
# THEME / CSS  (Dark Emerald "Liquid Glass")
# ============================================================


st.markdown(
    """
    <style>

    /* ---------- Base palette ---------- */
    :root {
        --emerald-950: #021b12;
        --emerald-900: #04281a;
        --emerald-800: #063c26;
        --emerald-700: #0a5233;
        --emerald-600: #0f6b42;
        --emerald-500: #168a55;
        --emerald-400: #2fb377;
        --emerald-glass: rgba(20, 120, 80, 0.18);
        --emerald-glass-strong: rgba(30, 150, 100, 0.30);
        --text-bright: #f2fbf6;
        --text-soft: #d6ede1;
        --border-glass: rgba(255, 255, 255, 0.14);
    }

    /* ---------- App background ---------- */
    .stApp {
        background: radial-gradient(circle at 15% 0%, #0a3a25 0%, #021b12 55%, #010f0a 100%);
        color: var(--text-bright);
    }

    /* ---------- Kill default streamlit header, replace with our own ---------- */
    [data-testid="stHeader"] {
        background: transparent;
        height: 0px;
    }
    [data-testid="stToolbar"] {
        right: 1rem;
    }

    /* ---------- Custom top nav bar ---------- */
    .aipad-topbar {
        position: relative;
        margin: -1rem -1rem 1.5rem -1rem;
        padding: 1.1rem 2rem;
        background:
            linear-gradient(120deg, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0.0) 30%),
            linear-gradient(100deg, #0d5c39 0%, #0a4a2e 35%, #063622 65%, #042c1c 100%);
        border-bottom: 1px solid rgba(255,255,255,0.10);
        box-shadow:
            0 4px 18px rgba(0, 0, 0, 0.45),
            inset 0 1px 0 rgba(255,255,255,0.18),
            inset 0 -1px 0 rgba(0,0,0,0.25);
        display: flex;
        align-items: center;
        justify-content: space-between;
        overflow: hidden;
    }
    .aipad-topbar::before {
        content: "";
        position: absolute;
        top: -60%;
        left: -10%;
        width: 60%;
        height: 220%;
        background: linear-gradient(
            120deg,
            rgba(255,255,255,0.16) 0%,
            rgba(255,255,255,0.05) 35%,
            rgba(255,255,255,0.0) 60%
        );
        transform: rotate(12deg);
        pointer-events: none;
    }
    .aipad-topbar h1 {
        position: relative;
        z-index: 1;
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: 0.01em;
        color: var(--text-bright);
        text-shadow: 0 1px 2px rgba(0,0,0,0.35);
    }
    .aipad-topbar span.subtitle {
        position: relative;
        z-index: 1;
        font-size: 0.85rem;
        font-weight: 400;
        color: var(--text-soft);
        opacity: 0.85;
        margin-left: 0.75rem;
    }

    /* ---------- Left "sidebar" (controls column) ---------- */
    div[data-testid="stColumn"]:has(div.aipad-controls-anchor) {
        background: linear-gradient(180deg, #052b1c 0%, #031e14 60%, #02150e 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 1.25rem 1rem 1.5rem 1rem;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.06),
            0 8px 24px rgba(0,0,0,0.35);
    }

    /* All text inside the controls column: bright, readable */
    div[data-testid="stColumn"]:has(div.aipad-controls-anchor) * {
        color: var(--text-bright) !important;
    }
    div[data-testid="stColumn"]:has(div.aipad-controls-anchor) label,
    div[data-testid="stColumn"]:has(div.aipad-controls-anchor) .stMarkdown,
    div[data-testid="stColumn"]:has(div.aipad-controls-anchor) h3 {
        color: var(--text-bright) !important;
    }

    /* ---------- Editor column ---------- */
    div[data-testid="stColumn"]:has(div.aipad-editor-anchor) {
        padding: 0.5rem 0.5rem 0.5rem 1.5rem;
    }

    /* ---------- Text area (the note) ---------- */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 14px !important;
        color: var(--text-bright) !important;
        backdrop-filter: blur(6px);
        box-shadow: inset 0 1px 4px rgba(0,0,0,0.3);
        transition: border-color 0.25s ease, box-shadow 0.25s ease;
        font-size: 0.98rem;
    }
    .stTextArea textarea:focus {
        border-color: var(--emerald-400) !important;
        box-shadow:
            0 0 0 3px rgba(47, 179, 119, 0.25),
            inset 0 1px 4px rgba(0,0,0,0.3) !important;
    }
    .stTextArea textarea::placeholder {
        color: rgba(214, 237, 225, 0.45) !important;
    }

    /* ---------- Text inputs (Generate / Rewrite) ---------- */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 12px !important;
        color: var(--text-bright) !important;
        backdrop-filter: blur(8px);
        transition: border-color 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
    }
    .stTextInput input:focus {
        border-color: var(--emerald-400) !important;
        background: rgba(255, 255, 255, 0.09) !important;
        box-shadow: 0 0 0 3px rgba(47, 179, 119, 0.22) !important;
    }
    .stTextInput input::placeholder {
        color: rgba(214, 237, 225, 0.45) !important;
    }

    /* ---------- Selectbox (Model picker) ---------- */
    .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 12px !important;
        color: var(--text-bright) !important;
        backdrop-filter: blur(8px);
        transition: border-color 0.25s ease, box-shadow 0.25s ease;
    }
    .stSelectbox div[data-baseweb="select"] > div:hover {
        border-color: var(--emerald-400) !important;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] {
        background: #052b1c !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 10px !important;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] li {
        color: var(--text-bright) !important;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] li:hover {
        background: var(--emerald-glass-strong) !important;
    }

    /* ---------- Liquid-glass buttons ---------- */
    .stButton > button {
        width: 100%;
        position: relative;
        overflow: hidden;
        background: linear-gradient(
            160deg,
            rgba(255,255,255,0.16) 0%,
            rgba(255,255,255,0.05) 40%,
            var(--emerald-glass) 100%
        );
        border: 1px solid var(--border-glass);
        border-radius: 14px;
        color: var(--text-bright) !important;
        font-weight: 600;
        letter-spacing: 0.01em;
        padding: 0.55rem 1rem;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow:
            0 4px 14px rgba(0, 0, 0, 0.30),
            inset 0 1px 0 rgba(255,255,255,0.25),
            inset 0 -1px 0 rgba(0,0,0,0.15);
        transition: transform 0.18s ease, box-shadow 0.25s ease, background 0.25s ease, border-color 0.25s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        border-color: rgba(255,255,255,0.28);
        background: linear-gradient(
            160deg,
            rgba(255,255,255,0.22) 0%,
            rgba(255,255,255,0.07) 40%,
            var(--emerald-glass-strong) 100%
        );
        box-shadow:
            0 6px 20px rgba(0, 0, 0, 0.38),
            inset 0 1px 0 rgba(255,255,255,0.30),
            0 0 0 3px rgba(47, 179, 119, 0.15);
    }
    .stButton > button:active {
        transform: translateY(0px) scale(0.985);
        box-shadow:
            0 2px 8px rgba(0, 0, 0, 0.35),
            inset 0 1px 3px rgba(0,0,0,0.25);
    }
    .stButton > button:focus:not(:active) {
        outline: none;
        box-shadow:
            0 4px 14px rgba(0, 0, 0, 0.30),
            0 0 0 3px rgba(47, 179, 119, 0.35);
    }
    .stButton > button p {
        color: var(--text-bright) !important;
        font-weight: 600;
    }

    /* ---------- Divider ---------- */
    div[data-testid="stColumn"]:has(div.aipad-controls-anchor) hr {
        border-color: rgba(255,255,255,0.12) !important;
        margin: 1rem 0;
    }

    /* ---------- Error / expander / code panels ---------- */
    div[data-testid="stAlert"] {
        background: rgba(200, 60, 60, 0.15) !important;
        border: 1px solid rgba(255, 120, 120, 0.35) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(6px);
    }
    .stExpander {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(6px);
    }
    .stExpander summary {
        color: var(--text-bright) !important;
    }
    div[data-testid="stCodeBlock"] {
        border-radius: 10px !important;
        border: 1px solid var(--border-glass) !important;
    }

    /* ---------- Warning ---------- */
    div[data-testid="stAlertContentWarning"] {
        color: var(--text-bright) !important;
    }

    /* ---------- Scrollbar polish ---------- */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(47, 179, 119, 0.35);
        border-radius: 8px;
        border: 2px solid transparent;
        background-clip: padding-box;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(47, 179, 119, 0.55);
        background-clip: padding-box;
    }

    /* ---------- Responsive tweaks ---------- */
    @media (max-width: 768px) {
        .aipad-topbar {
            padding: 0.85rem 1.1rem;
            flex-direction: column;
            align-items: flex-start;
            gap: 0.15rem;
        }
        .aipad-topbar h1 {
            font-size: 1.2rem;
        }
        div[data-testid="stColumn"]:has(div.aipad-controls-anchor) {
            border-radius: 14px;
            padding: 1rem 0.75rem;
        }
        div[data-testid="stColumn"]:has(div.aipad-editor-anchor) {
            padding: 0.5rem 0.25rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TOP NAV BAR
# ============================================================


st.markdown(
    """
    <div class="aipad-topbar">
        <div>
            <h1>📝 AIpad<span class="subtitle">AI-assisted notes &amp; code</span></h1>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
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
    # Invisible anchor so the CSS `:has()` selector can target this
    # specific column and style it like a sidebar.
    st.markdown('<div class="aipad-controls-anchor"></div>', unsafe_allow_html=True)

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
    # Invisible anchor so the CSS `:has()` selector can target this
    # specific column and give the editor its own spacing/styling.
    st.markdown('<div class="aipad-editor-anchor"></div>', unsafe_allow_html=True)

    st.text_area(
        "Your note",
        height=330,
        placeholder="Start writing here...",
        key="note",
        label_visibility="collapsed",
    )