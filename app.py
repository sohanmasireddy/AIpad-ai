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

MODEL = "gpt-oss:20b-cloud"


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "note": "",
    "panel": None,
    "error": None,
    "retry": None,
    "generate_prompt": "",
    "rewrite_prompt": "",
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# OLLAMA API KEY
# ============================================================

if "ollama_api_key" not in st.secrets:

    st.error(
        "`ollama_api_key` was not found in Streamlit secrets."
    )

    st.stop()


OLLAMA_API_KEY = st.secrets["ollama_api_key"]


# ============================================================
# OLLAMA CLIENT
# ============================================================

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

        content = (
            chunk
            .get("message", {})
            .get("content", "")
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


        # ----------------------------------------------------
        # GENERATE
        # ----------------------------------------------------

        if action == "generate":

            if st.session_state.note.strip():

                st.session_state.note += (
                    "\n\n" + result
                )

            else:

                st.session_state.note = result


        # ----------------------------------------------------
        # FIX / REWRITE
        # ----------------------------------------------------

        else:

            st.session_state.note = result


        # ----------------------------------------------------
        # RESET
        # ----------------------------------------------------

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
# MAIN LAYOUT
# ============================================================

controls, editor = st.columns(
    [1, 4],
    gap="large",
)


# ============================================================
# LEFT CONTROL AREA
# ============================================================

with controls:

    # --------------------------------------------------------
    # SMALL TITLE
    # --------------------------------------------------------

    st.subheader("📝 AIpad")

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


    # ========================================================
    # GENERATE PANEL
    # ========================================================

    if st.session_state.panel == "generate":

        st.divider()

        st.caption("🏭 Generate")


        st.text_input(
            "Generate prompt",
            placeholder="What should I create?",
            key="generate_prompt",
            label_visibility="collapsed",
        )


        if st.button(
            "✨ Run Generate",
            use_container_width=True,
            type="primary",
        ):

            prompt = (
                st.session_state.generate_prompt
                .strip()
            )

            if not prompt:

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


        if st.button(
            "Cancel",
            use_container_width=True,
        ):

            st.session_state.panel = None

            st.rerun()


    # ========================================================
    # REWRITE PANEL
    # ========================================================

    if st.session_state.panel == "rewrite":

        st.divider()

        st.caption("🔄 Rewrite")


        st.text_input(
            "Rewrite instructions",
            placeholder="Make it shorter...",
            key="rewrite_prompt",
            label_visibility="collapsed",
        )


        if st.button(
            "🔄 Apply Rewrite",
            use_container_width=True,
            type="primary",
        ):

            note = (
                st.session_state.note
                .strip()
            )

            instructions = (
                st.session_state.rewrite_prompt
                .strip()
            )


            if not note:

                st.warning(
                    "Write something first."
                )

            elif not instructions:

                st.warning(
                    "Tell AI how to rewrite it."
                )

            else:

                run_ai(
                    (
                        instructions
                        + "\n\nRewrite this:\n\n"
                        + note
                    ),
                    "rewrite",
                )


        if st.button(
            "Cancel",
            use_container_width=True,
        ):

            st.session_state.panel = None

            st.rerun()


    # ========================================================
    # ERROR
    # ========================================================

    if st.session_state.error:

        st.divider()

        st.error(
            "AI request failed."
        )


        with st.expander("Details"):

            st.code(
                st.session_state.error
            )


        if st.session_state.retry:

            if st.button(
                "🔄 Retry",
                use_container_width=True,
            ):

                prompt, action = (
                    st.session_state.retry
                )

                st.session_state.error = None

                run_ai(
                    prompt,
                    action,
                )


# ============================================================
# RIGHT EDITOR AREA
# ============================================================

with editor:

    # --------------------------------------------------------
    # CENTERED TITLE
    # --------------------------------------------------------

    title_left, title_center, title_right = st.columns(
        [1, 2, 1]
    )

    with title_center:

        st.title("📝 AIpad")


    # --------------------------------------------------------
    # TEXT BOX
    # --------------------------------------------------------

    st.text_area(
        "Your note",
        height=260,
        placeholder="Start writing here...",
        key="note",
        label_visibility="collapsed",
    )
