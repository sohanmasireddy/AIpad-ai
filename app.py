import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="AIpad", page_icon="📝")

# --- AI SETUP ---
if "ollama_api_key" not in st.secrets:
    st.error("`ollama_api_key` was not found. Please add it to `.streamlit/secrets.toml`.")
    st.stop()

ollama_api_key = st.secrets["ollama_api_key"]

ai = OpenAI(
    base_url="https://ollama.com/v1",
    api_key=ollama_api_key
)

MODEL = "gpt-oss:20b-cloud"

# --- SESSION STATE ---
defaults = {
    "page": "home",
    "note": "",
    "panel": None,
    "error": None,
    "retry": None
}

for key, value in defaults.items():
    st.session_state.setdefault(key, value)


def ask(prompt):
    response = ai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def run_ai(prompt, action):
    try:
        with st.spinner("AI is working..."):
            result = ask(prompt)

        if action == "generate":
            st.session_state.note += "\n" + result
        else:
            st.session_state.note = result

        st.session_state.panel = None
        st.rerun()

    except Exception as e:
        st.session_state.error = str(e)
        st.session_state.retry = (prompt, action)
        st.session_state.page = "error"
        st.rerun()


# --- HOME PAGE ---
if st.session_state.page == "home":
    st.title("📝 AIpad")
    st.write("Your AI-powered notepad.")
    st.divider()

    st.subheader("Welcome to AIpad")
    st.write("Write, generate, fix, and rewrite text or code.")

    if st.button("🚀 Open AIpad", use_container_width=True):
        st.session_state.page = "main"
        st.rerun()

    st.stop()


# --- ERROR PAGE ---
if st.session_state.page == "error":
    st.title("⚠️ AI Error")
    st.error("AIpad couldn't get a response from the AI.")

    with st.expander("Show error details"):
        st.code(st.session_state.error)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Retry", use_container_width=True):
            prompt, action = st.session_state.retry
            run_ai(prompt, action)

    with col2:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

    st.stop()


# --- MAIN PAGE ---
st.title("📝 AIpad")
st.write("Write Here")

# Binding text_area directly to session state key
st.session_state.note = st.text_area(
    "Your note",
    value=st.session_state.note,
    height=350,
    placeholder="Write something here..."
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("✨ AI Fix", use_container_width=True):
        if st.session_state.note.strip():
            run_ai(
                "Fix the code and/or text. Return only the fixed text and/or code.\n\n"
                + st.session_state.note,
                "fix"
            )
        else:
            st.warning("Write something first.")

with col2:
    if st.button("🤖 Generate", use_container_width=True):
        st.session_state.panel = "generate"
        st.rerun()

with col3:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.note = ""
        st.rerun()

with col4:
    if st.button("🔄 Rewrite", use_container_width=True):
        st.session_state.panel = "rewrite"
        st.rerun()


# --- GENERATE PANEL ---
if st.session_state.panel == "generate":
    st.divider()
    prompt = st.text_input("What should AI generate?")

    if st.button("Generate"):
        if prompt.strip():
            run_ai(
                "Generate this. Return only the text and/or code.\n\n" + prompt,
                "generate"
            )
        else:
            st.warning("Enter a prompt first.")


# --- REWRITE PANEL ---
if st.session_state.panel == "rewrite":
    st.divider()
    prompt = st.text_input(
        "How should I rewrite it?",
        placeholder="Example: Make it shorter and professional..."
    )

    if st.button("Apply Rewrite"):
        if not st.session_state.note.strip():
            st.warning("Write something first.")
        elif not prompt.strip():
            st.warning("Tell AI how you want it rewritten.")
        else:
            run_ai(
                prompt + "\n\nRewrite this:\n\n" + st.session_state.note,
                "rewrite"
            )


st.divider()

if st.button("🏠 Home"):
    st.session_state.page = "home"
    st.rerun()