import streamlit as st
from ollama import Client


# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="AIpad",
    page_icon="📝",
    layout="centered",
)


# ============================================================
# CONSTANTS
# ============================================================

MODEL = "gpt-oss:20b-cloud"


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "page": "home",
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
    """
    Create the Ollama client once and reuse it
    across Streamlit reruns.
    """
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

def ask_ai(prompt):
    """
    Stream the AI response and return the final text.
    """

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
        content = chunk.get("message", {}).get("content", "")

        if content:
            result += content

    return result


def run_ai(prompt, action):
    """
    Execute an AI operation and update the note.
    """

    try:

        with st.spinner("🏭 AI is working..."):

            result = ask_ai(prompt)

        if not result.strip():
            raise RuntimeError(
                "The AI returned an empty response."
            )

        # Generate appends to the existing note.
        if action == "generate":

            if st.session_state.note.strip():

                st.session_state.note += (
                    "\n\n" + result
                )

            else:

                st.session_state.note = result

        # Fix / Rewrite replace the note.
        else:

            st.session_state.note = result

        # Reset UI state.
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

        st.session_state.page = "error"

        st.rerun()


# ============================================================
# HOME PAGE
# ============================================================

if st.session_state.page == "home":

    st.title("📝 AIpad")

    st.divider()

    if st.button(
        "🚀 Launch",
        use_container_width=True,
        type="primary",
    ):

        st.session_state.page = "main"

        st.rerun()

    st.stop()


# ============================================================
# ERROR PAGE
# ============================================================

if st.session_state.page == "error":

    st.title("⚠️ Something went wrong")

    st.error(
        "AIpad couldn't complete that request."
    )

    with st.expander("Show error details"):

        st.code(
            st.session_state.error
            or "Unknown error"
        )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🔄 Retry",
            use_container_width=True,
            type="primary",
        ):

            if st.session_state.retry:

                prompt, action = (
                    st.session_state.retry
                )

                # Return to main page before retrying.
                st.session_state.page = "main"

                run_ai(
                    prompt,
                    action,
                )

    with col2:

        if st.button(
            "🏠 Home",
            use_container_width=True,
        ):

            st.session_state.page = "home"
            st.session_state.panel = None
            st.session_state.error = None
            st.session_state.retry = None

            st.rerun()

    st.stop()


# ============================================================
# MAIN PAGE
# ============================================================

st.title("📝 AIpad")


# ============================================================
# EDITOR
# ============================================================

st.text_area(
    "Note",
    height=350,
    placeholder="Write something here...",
    label_visibility="collapsed",
    key="note",
)


# ============================================================
# MAIN BUTTONS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


# ------------------------------------------------------------
# AI FIX
# ------------------------------------------------------------

with col1:

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


# ------------------------------------------------------------
# GENERATE
# ------------------------------------------------------------

with col2:

    if st.button(
        "🏭 Generate",
        use_container_width=True,
    ):

        st.session_state.panel = "generate"


# ------------------------------------------------------------
# CLEAR
# ------------------------------------------------------------

with col3:

    if st.button(
        "🗑️ Clear",
        use_container_width=True,
    ):

        st.session_state.note = ""
        st.session_state.panel = None


# ------------------------------------------------------------
# REWRITE
# ------------------------------------------------------------

with col4:

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


# ============================================================
# GENERATE PANEL
# ============================================================

if st.session_state.panel == "generate":

    st.divider()

    st.subheader("🏭 Generate")

    with st.form("generate_form"):

        prompt = st.text_input(
            "Prompt",
            placeholder="What do you want to create?",
            label_visibility="collapsed",
        )

        col1, col2 = st.columns(2)

        with col1:

            submitted = st.form_submit_button(
                "✨ Generate",
                use_container_width=True,
                type="primary",
            )

        with col2:

            cancelled = st.form_submit_button(
                "Cancel",
                use_container_width=True,
            )

    if cancelled:

        st.session_state.panel = None
        st.rerun()

    if submitted:

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
            "Instructions",
            placeholder=(
                "Example: Make it shorter "
                "and professional..."
            ),
        )

        col1, col2 = st.columns(2)

        with col1:

            submitted = st.form_submit_button(
                "🔄 Apply Rewrite",
                use_container_width=True,
                type="primary",
            )

        with col2:

            cancelled = st.form_submit_button(
                "Cancel",
                use_container_width=True,
            )

    if cancelled:

        st.session_state.panel = None
        st.rerun()

    if submitted:

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


# ============================================================
# HOME BUTTON
# ============================================================

st.divider()

if st.button(
    "🏠 Home",
    use_container_width=True,
):

    st.session_state.page = "home"
    st.session_state.panel = None

    st.rerun()
