import streamlit as st
from ollama import Client

# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="AIpad",
    page_icon="📝"
)

# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "page": "home",
    "note": "",
    "panel": None,
    "error": None,
    "retry": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# AI SETUP
# ============================================================

if "ollama_api_key" not in st.secrets:
    st.error(
        "`ollama_api_key` was not found in Streamlit secrets."
    )
    st.stop()

ollama_api_key = st.secrets["ollama_api_key"]

ai = Client(
    host="https://ollama.com",
    headers={
        "Authorization": f"Bearer {ollama_api_key}"
    }
)

MODEL = "gpt-oss:20b-cloud"


# ============================================================
# AI FUNCTION
# ============================================================

def ask(prompt):
    response = ai.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# ============================================================
# RUN AI
# ============================================================

def run_ai(prompt, action):
    try:
        with st.spinner("🤖 AI is working..."):
            result = ask(prompt)

        if not result:
            raise Exception("The AI returned an empty response.")

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

    except Exception as e:
        st.session_state.error = str(e)
        st.session_state.retry = (prompt, action)
        st.session_state.page = "error"

        st.rerun()


# ============================================================
# HOME PAGE
# ============================================================

if st.session_state.page == "home":

    st.title("📝 AIpad")
    st.write("Your AI-powered notepad.")

    st.divider()

    st.subheader("Welcome to AIpad")

    st.write(
        "Write, generate, fix, and rewrite text or code."
    )

    if st.button(
        "🚀 Open AIpad",
        use_container_width=True
    ):
        st.session_state.page = "main"
        st.rerun()

    st.stop()


# ============================================================
# ERROR PAGE
# ============================================================

if st.session_state.page == "error":

    st.title("⚠️ AI Error")

    st.error(
        "AIpad couldn't get a response from Ollama."
    )

    with st.expander("Show error details"):
        st.code(
            st.session_state.error or "Unknown error"
        )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🔄 Retry",
            use_container_width=True
        ):
            if st.session_state.retry:
                prompt, action = st.session_state.retry
                run_ai(prompt, action)

    with col2:
        if st.button(
            "🏠 Home",
            use_container_width=True
        ):
            st.session_state.page = "home"
            st.session_state.error = None
            st.rerun()

    st.stop()


# ============================================================
# MAIN PAGE
# ============================================================

st.title("📝 AIpad")
st.write("Write Here")


# Text editor
st.session_state.note = st.text_area(
    "Your note",
    value=st.session_state.note,
    height=350,
    placeholder="Write something here..."
)


# ============================================================
# MAIN BUTTONS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


# ---------------- AI FIX ----------------

with col1:

    if st.button(
        "✨ AI Fix",
        use_container_width=True
    ):

        if st.session_state.note.strip():

            run_ai(
                (
                    "Fix the following text or code. "
                    "Correct errors while preserving the "
                    "original meaning. Return ONLY the "
                    "fixed text or code.\n\n"
                    + st.session_state.note
                ),
                "fix"
            )

        else:
            st.warning("Write something first.")


# ---------------- GENERATE ----------------

with col2:

    if st.button(
        "🤖 Generate",
        use_container_width=True
    ):

        st.session_state.panel = "generate"
        st.rerun()


# ---------------- CLEAR ----------------

with col3:

    if st.button(
        "🗑️ Clear",
        use_container_width=True
    ):

        st.session_state.note = ""
        st.session_state.panel = None
        st.rerun()


# ---------------- REWRITE ----------------

with col4:

    if st.button(
        "🔄 Rewrite",
        use_container_width=True
    ):

        if st.session_state.note.strip():
            st.session_state.panel = "rewrite"
            st.rerun()
        else:
            st.warning("Write something first.")


# ============================================================
# GENERATE PANEL
# ============================================================

if st.session_state.panel == "generate":

    st.divider()

    st.subheader("🤖 Generate")

    prompt = st.text_input(
        "What should AI generate?",
        placeholder="Example: Write a Python calculator..."
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "✨ Generate",
            use_container_width=True
        ):

            if prompt.strip():

                run_ai(
                    (
                        "Generate the following. "
                        "Return ONLY the requested text or code.\n\n"
                        + prompt
                    ),
                    "generate"
                )

            else:
                st.warning("Enter a prompt first.")

    with col2:

        if st.button(
            "Cancel",
            use_container_width=True
        ):

            st.session_state.panel = None
            st.rerun()


# ============================================================
# REWRITE PANEL
# ============================================================

if st.session_state.panel == "rewrite":

    st.divider()

    st.subheader("🔄 Rewrite")

    prompt = st.text_input(
        "How should I rewrite it?",
        placeholder="Example: Make it shorter and professional..."
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🔄 Apply Rewrite",
            use_container_width=True
        ):

            if not st.session_state.note.strip():

                st.warning("Write something first.")

            elif not prompt.strip():

                st.warning(
                    "Tell AI how you want it rewritten."
                )

            else:

                run_ai(
                    (
                        prompt
                        + "\n\nRewrite this:\n\n"
                        + st.session_state.note
                    ),
                    "rewrite"
                )

    with col2:

        if st.button(
            "Cancel",
            use_container_width=True
        ):

            st.session_state.panel = None
            st.rerun()


# ============================================================
# HOME BUTTON
# ============================================================

st.divider()

if st.button(
    "🏠 Home",
    use_container_width=True
):

    st.session_state.page = "home"
    st.session_state.panel = None
    st.rerun()