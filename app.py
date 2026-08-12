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
# CONSTANTS
# ============================================================

MODEL = "gpt-oss:20b-cloud"


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "note": "",
    "panel": None,
    "error": None,
    "retry": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# OLLAMA CLIENT
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
# AI FUNCTION
# ============================================================

def ask_ai(prompt):

    response = ai.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        stream=True,
    )

    result = ""

    for chunk in response:

        content = chunk.get(
            "message",
            {}
        ).get(
            "content",
            ""
        )

        if content:
            result += content

    return result


# ============================================================
# RUN AI
# ============================================================

def run_ai(prompt, action):

    try:

        with st.spinner("🏭 AI is working..."):

            result = ask_ai(prompt)

        if not result.strip():
            raise RuntimeError(
                "The AI returned an empty response."
            )

        # Generate adds to the note.
        if action == "generate":

            if st.session_state.note.strip():

                st.session_state.note += (
                    "\n\n" + result
                )

            else:

                st.session_state.note = result

        # Fix and Rewrite replace the note.
        else:

            st.session_state.note = result

        st.session_state.panel = None
        st.session_state.error = None
        st.session_state.retry = None

        st.rerun()

    except Exception as error:

        st.session_state.error = str(error)

        st.session_state.retry = (
            prompt,
            action,
        )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main page */

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 30px;
    }


    /* Sidebar */

    section[data-testid="stSidebar"] {
        min-width: 230px;
        max-width: 230px;
    }


    /* Sidebar title */

    .sidebar-title {
        text-align: center;
        font-size: 25px;
        font-weight: 700;
        margin-bottom: 20px;
    }


    /* Editor */

    div[data-testid="stTextArea"] textarea {
        font-size: 17px;
        line-height: 1.6;
        padding: 18px;
        border-radius: 10px;
    }


    /* Remove text area label spacing */

    div[data-testid="stTextArea"] {
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">📝 AIpad</div>',
        unsafe_allow_html=True,
    )

    st.divider()


    # ========================================================
    # AI FIX
    # ========================================================

    if st.button(
        "✨ AI Fix",
        use_container_width=True,
    ):

        note = st.session_state.note.strip()

        if not note:

            st.warning(
                "Write something first."
            )

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
            )


    # ========================================================
    # GENERATE
    # ========================================================

    if st.button(
        "🏭 Generate",
        use_container_width=True,
    ):

        st.session_state.panel = "generate"


    # ========================================================
    # REWRITE
    # ========================================================

    if st.button(
        "🔄 Rewrite",
        use_container_width=True,
    ):

        if st.session_state.note.strip():

            st.session_state.panel = "rewrite"

        else:

            st.warning(
                "Write something first."
            )


    # ========================================================
    # CLEAR
    # ========================================================

    if st.button(
        "🗑️ Clear",
        use_container_width=True,
    ):

        st.session_state.note = ""
        st.session_state.panel = None
        st.session_state.error = None


    st.divider()


    # ========================================================
    # ERROR
    # ========================================================

    if st.session_state.error:

        st.error(
            "AI request failed."
        )

        with st.expander("Details"):

            st.code(
                st.session_state.error
            )

        if st.button(
            "🔄 Retry",
            use_container_width=True,
        ):

            if st.session_state.retry:

                prompt, action = (
                    st.session_state.retry
                )

                st.session_state.error = None

                run_ai(
                    prompt,
                    action,
                )


# ============================================================
# MAIN TITLE
# ============================================================

st.markdown(
    '<div class="main-title">📝 AIpad</div>',
    unsafe_allow_html=True,
)


# ============================================================
# MAIN TEXT EDITOR
# ============================================================

st.text_area(
    "Your note",
    height=550,
    placeholder=(
        "Start writing here..."
    ),
    key="note",
)


# ============================================================
# GENERATE PANEL
# ============================================================

if st.session_state.panel == "generate":

    st.divider()

    st.subheader("🏭 Generate")

    with st.form("generate_form"):

        prompt = st.text_input(
            "What should AI generate?",
            placeholder=(
                "Example: Write a Python function "
                "that sorts a list..."
            ),
        )

        col1, col2 = st.columns(2)

        with col1:

            generate = st.form_submit_button(
                "✨ Generate",
                use_container_width=True,
                type="primary",
            )

        with col2:

            cancel = st.form_submit_button(
                "Cancel",
                use_container_width=True,
            )


    if cancel:

        st.session_state.panel = None
        st.rerun()


    if generate:

        if not prompt.strip():

            st.warning(
                "Enter a prompt first."
            )

        else:

            run_ai(
                (
                    "Generate the following. "
                    "Return ONLY the requested "
                    "text or code.\n\n"
                    + prompt
                ),
                "generate",
            )


# ============================================================
# REWRITE PANEL
# ============================================================

if st.session_state.panel == "rewrite":

    st.divider()

    st.subheader("🔄 Rewrite")

    with st.form("rewrite_form"):

        prompt = st.text_input(
            "How should AI rewrite it?",
            placeholder=(
                "Example: Make it shorter "
                "and more professional..."
            ),
        )

        col1, col2 = st.columns(2)

        with col1:

            rewrite = st.form_submit_button(
                "🔄 Apply Rewrite",
                use_container_width=True,
                type="primary",
            )

        with col2:

            cancel = st.form_submit_button(
                "Cancel",
                use_container_width=True,
            )


    if cancel:

        st.session_state.panel = None
        st.rerun()


    if rewrite:

        note = st.session_state.note.strip()

        if not note:

            st.warning(
                "Write something first."
            )

        elif not prompt.strip():

            st.warning(
                "Tell AI how you want it rewritten."
            )

        else:

            run_ai(
                (
                    prompt
                    + "\n\nRewrite this:\n\n"
                    + note
                ),
                "rewrite",
            )
