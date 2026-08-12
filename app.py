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


def run_ai(prompt, action):

    try:

        with st.spinner("🏭 AI is working..."):

            result = ask_ai(prompt)

        if not result.strip():
            raise RuntimeError(
                "The AI returned an empty response."
            )

        if action == "generate":

            if st.session_state.note.strip():
                st.session_state.note += (
                    "\n\n" + result
                )
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
        st.session_state.retry = (
            prompt,
            action,
        )
        st.session_state.page = "error"

        st.rerun()


# ============================================================
# HOME
# ============================================================

if st.session_state.page == "home":

    st.markdown(
        """
        <style>
        .home-title {
            text-align: center;
            font-size: 60px;
            font-weight: 700;
            margin-top: 20vh;
        }

        .home-subtitle {
            text-align: center;
            color: #888;
            font-size: 18px;
            margin-bottom: 30px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="home-title">📝 AIpad</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="home-subtitle">Your AI-powered notepad</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

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
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <h1 style="text-align:center;">
            📝 AIpad
        </h1>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # --------------------------------------------------------
    # AI FIX
    # --------------------------------------------------------

    if st.button(
        "✨ AI Fix",
        use_container_width=True,
    ):

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
            )

    # --------------------------------------------------------
    # GENERATE
    # --------------------------------------------------------

    if st.button(
        "🏭 Generate",
        use_container_width=True,
    ):

        st.session_state.panel