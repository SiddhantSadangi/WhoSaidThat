import random
from typing import List

import requests
import streamlit as st
import streamlit.components.v1 as components

__version__ = "1.0.0"

API_SERVER = "https://api.quotable.io"
NUM_OPTIONS = 4

state = st.session_state

st.set_page_config(
    page_title="Who Said That?",
    page_icon="🤔",
    menu_items={
        "About": f"🤔 Who Said That? v{__version__}  "
        f"\nApp contact: [Siddhant Sadangi](mailto:siddhant.sadangi@gmail.com)",
        "Report a Bug": "https://github.com/SiddhantSadangi/WhoSaidThat/issues/new",
        "Get help": None,
    },
)

st.header("🤔 Who Said That?", divider="rainbow")
st.caption(
    """Do you love quotes? Do you enjoy learning from the wisdom of others? Do you think you can recognize the authors of famous quotes?  
    If you answered yes to any of these questions, then this is the app for you!"""
)

# ---------- SIDEBAR ----------
with st.sidebar:
    with open("sidebar.html", "r", encoding="UTF-8") as sidebar_file:
        sidebar_html = sidebar_file.read().replace("{VERSION}", __version__)

    st.components.v1.html(sidebar_html, height=600)


# ---------- STREAMLIT FUNCTIONS ----------
def set_session_states() -> None:
    state["score"] = 0
    state["quotes"] = {}
    state["disabled"] = {
        "get_quote": True,
        "submit": True,
        "select_tags": False,
    }
    state["tags"] = state["selected_tags"] = []

    get_tags()


# ---------- APP FUNCTIONS ----------
def get_tags() -> None:
    response = requests.get(f"{API_SERVER}/tags").json()
    state["tags"].extend(sorted({item["name"] for item in response}))


def get_quote(tags: List[str] = None) -> None:
    state["disabled"] = {
        "get_quote": True,
        "submit": False,
        "select_tags": True,
    }
    response = query(tags)[0]
    quote = response["content"]
    author = response["author"]
    author_slug = response["authorSlug"]
    tags = response["tags"]

    state["quotes"][quote] = {
        "author": author,
        "author_slug": author_slug,
        "tags": tags,
    }


def query(tags: List[str] = None, limit: int = 1) -> list[str]:
    if tags:
        return requests.get(f"{API_SERVER}/quotes/random?{limit=}&tags={'|'.join(tags)}").json()
    else:
        return requests.get(f"{API_SERVER}/quotes/random?{limit=}").json()


def get_random_authors() -> List[str]:
    responses = query(limit=NUM_OPTIONS - 1)
    authors = {author: author_slug}
    for response in responses:
        authors[response["author"]] = response["authorSlug"]

    return authors


def get_author_details(id: str):
    return requests.get(f"{API_SERVER}/authors/{id}")


def get_author_pic(slug: str):
    return requests.get(f"https://images.quotable.dev/profile/200/{slug}.jpg")


def evaluate(answer, author) -> None:
    if author == answer:
        state["score"] += 1
        st.success(f"Correct answer! Score: {state['score']}", icon="✅")
        get_quote(state["selected_tags"])
    else:
        game_over()


def game_over() -> None:
    st.error(f'Wrong answer! Correct answer is "{author}"', icon="❌")
    st.subheader(f"Final score: {state['score']}")
    state["disabled"] = {
        "get_quotes": True,
        "submit": True,
        "select_tags": True,
    }
    state["score"] = 0
    state["quotes"] = 0
    st.button(
        "Restart 🔁",
        use_container_width=True,
        type="primary",
        on_click=set_session_states,
    )

    c1, c2, c3, c4, _ = st.columns([3, 1, 1, 1, 2])
    c1.text("Share the 💖 on social media")
    with c2:
        components.html(
            """
                <a href="https://www.facebook.com/sharer/sharer.php?kid_directed_site=0&sdk=joey&u=https%3A%2F%2Fwhosaidthat.streamlit.app%2F&display=popup&ref=plugin&src=share_button"
                    target="_blank">
                    <img src="https://github.com/SiddhantSadangi/SiddhantSadangi/assets/41324509/3c38dc85-6e4d-499b-b0c5-a74cadf0c30b"
                        alt="Share on Facebook" width="40" height="40">
                </a>
            """
        )
    with c3:
        components.html(
            """
                <a href="https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fwhosaidthat.streamlit.app%2F"
                    target="_blank">
                    <img src="https://github.com/SiddhantSadangi/SiddhantSadangi/assets/41324509/854b630d-4dbc-4a13-9a8e-ebebe3d34441"
                        alt="Share on LinkedIn" height="40" width="40">
                </a>
            """
        )
    with c4:
        components.html(
            """
                <a href="https://www.twitter.com/intent/tweet%3Foriginal_referer%3Dhttps%3A%2F%2Fwhosaidthat.streamlit.app%2F%26ref_src%3Dtwsrc%5Etfw%7Ctwcamp%5Ebuttonembed%7Ctwterm%5Eshare%7Ctwgr%5E%26text%3DDo%20you%20love%20quotes%3F%20Do%20you%20enjoy%20learning%20from%20the%20wisdom%20of%20others%3F%20Do%20you%20think%20you%20can%20recognize%20the%20authors%20of%20famous%20quotes%3F%0AIf%20you%20answered%20yes%20to%20any%20of%20these%20questions%2C%20then%20%2A%2AWho%20Said%20That%3F%2A%2A%20is%20the%20app%20for%20you%21%26url%3Dhttps%3A%2F%2Fwhosaidthat.streamlit.app%2F"
                    target="_blank">
                    <img src="https://github.com/SiddhantSadangi/SiddhantSadangi/assets/41324509/e2a5e256-20f2-4d20-b0fb-256b3ebe227a"
                        alt="Share on X" height="40" width="40">
                </a>
            """
        )


# ---------- APP ----------
if "quotes" not in state:
    set_session_states()

with st.expander("Select tags", expanded=not state["disabled"]["select_tags"]):
    state["selected_tags"] = st.multiselect(
        "Selection cannot be changed once round has started",
        options=state["tags"],
        default=state["tags"],
        disabled=state["disabled"]["select_tags"],
    )

if st.button(
    "Start 🚀",
    type="primary",
    use_container_width=True,
    disabled=state["disabled"]["select_tags"],
):
    state["disabled"] = {
        "get_quotes": False,
        "submit": True,
        "select_tags": True,
    }
    get_quote(state["selected_tags"])

if state.quotes:
    quote = list(state["quotes"])[-1]
    author = state["quotes"][quote]["author"]
    author_slug = state["quotes"][quote]["author_slug"]
    authors = get_random_authors()

    st.subheader(quote)

    columns = st.columns(4)
    for idx, choice in enumerate(random.sample(list(authors), k=len(authors))):
        with columns[idx]:
            image_url = f"https://images.quotable.dev/profile/200/{authors[choice]}.jpg"
            if requests.get(image_url).status_code == 200:
                st.image(f"https://images.quotable.dev/profile/200/{authors[choice]}.jpg")
            else:
                st.image(
                    "https://www.pngall.com/wp-content/uploads/5/Profile-Male-PNG-Free-Download-180x180.png"
                )
            st.button(
                choice,
                key=state["score"] + idx + 1,
                use_container_width=True,
                on_click=evaluate,
                args=(author, choice),
            )

# TODO: Show info about authors after answer
# TODO: Scoring mechanism (ref: https://song-game.streamlit.app/)
