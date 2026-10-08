import os

import requests
import streamlit as st


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

DEFAULT_SERVER_URL = os.getenv("BOOK_SERVER_URL", "http://127.0.0.1:8000")


# ---------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="Book Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------
# Dark theme / styling
# ---------------------------------------------------------------------

st.markdown(
    """
    <style>
        .stApp {
            background: #0e1117;
        }

        [data-testid="stSidebar"] {
            background: #111827;
            border-right: 1px solid #263244;
        }

        .hero {
            padding: 1.2rem 1.5rem;
            border: 1px solid #263244;
            border-radius: 14px;
            background: linear-gradient(135deg, #151c2b, #10151f);
            margin-bottom: 1.2rem;
        }

        .hero h1 {
            margin: 0;
            font-size: 2rem;
        }

        .hero p {
            color: #9ca3af;
            margin: 0.4rem 0 0 0;
        }

        .status-card {
            padding: 0.8rem 1rem;
            border-radius: 10px;
            background: #151c2b;
            border: 1px solid #263244;
            margin-bottom: 1rem;
        }

        div[data-testid="stMetric"] {
            background: #151c2b;
            border: 1px solid #263244;
            padding: 0.8rem;
            border-radius: 12px;
        }

        .book-card {
            background: #151c2b;
            border: 1px solid #263244;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.7rem;
        }

        .book-title {
            font-size: 1.1rem;
            font-weight: 600;
        }

        .book-author {
            color: #9ca3af;
            margin-top: 0.25rem;
        }

        .book-id {
            color: #6b7280;
            font-size: 0.8rem;
        }

        .section-note {
            color: #9ca3af;
            font-size: 0.9rem;
        }

        .stButton > button {
            border-radius: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------

if "server_url" not in st.session_state:
    st.session_state.server_url = DEFAULT_SERVER_URL.rstrip("/")

if "selected_book_id" not in st.session_state:
    st.session_state.selected_book_id = None


# ---------------------------------------------------------------------
# API helper functions
# ---------------------------------------------------------------------

def api_url(path: str) -> str:
    return f"{st.session_state.server_url.rstrip('/')}{path}"


def handle_response(response):
    """Return JSON when possible and raise a useful API error otherwise."""
    try:
        data = response.json()
    except ValueError:
        data = {"detail": response.text or "No response body"}

    if response.ok:
        return data

    detail = data.get("detail", str(data)) if isinstance(data, dict) else str(data)
    raise RuntimeError(f"HTTP {response.status_code}: {detail}")


def get_books():
    response = requests.get(api_url("/books/"), timeout=5)
    return handle_response(response)


def get_book(book_id: int):
    response = requests.get(api_url(f"/books/{book_id}"), timeout=5)
    return handle_response(response)


def create_book(title: str, author: str):
    response = requests.post(
        api_url("/books/"),
        json={"title": title, "author": author},
        timeout=5,
    )
    return handle_response(response)


def update_book(book_id: int, title: str, author: str):
    response = requests.put(
        api_url(f"/books/{book_id}"),
        json={"title": title, "author": author},
        timeout=5,
    )
    return handle_response(response)


def delete_book(book_id: int):
    response = requests.delete(
        api_url(f"/books/{book_id}"),
        timeout=5,
    )
    return handle_response(response)


# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------

with st.sidebar:
    st.markdown("## ⚙️ Connection")

    server_url = st.text_input(
        "Book Server URL",
        value=st.session_state.server_url,
        help="URL of the running FastAPI/Uvicorn server.",
    )

    st.session_state.server_url = server_url.rstrip("/")

    if st.button("🔌 Check Connection", use_container_width=True):
        try:
            books = get_books()
            st.success(f"Connected • {len(books)} books")
        except requests.RequestException:
            st.error("Server unreachable")
        except Exception as exc:
            st.error(str(exc))

    st.divider()

    st.markdown("### API")
    st.code(
        f"{st.session_state.server_url}\n"
        "GET    /books/\n"
        "POST   /books/\n"
        "GET    /books/{{id}}\n"
        "PUT    /books/{{id}}\n"
        "DELETE /books/{{id}}",
        language="text",
    )

    st.divider()

    st.caption("Book Manager")
    st.caption("Streamlit → requests → FastAPI → SQLite")


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>📚 Book Manager</h1>
        <p>Manage books through the FastAPI HTTP service.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------

try:
    books = get_books()
    server_online = True
except Exception as exc:
    books = []
    server_online = False
    connection_error = str(exc)


if server_online:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📚 Total Books", len(books))

    with col2:
        st.metric("🟢 API Status", "Online")

    with col3:
        st.metric("🔗 Server", st.session_state.server_url)
else:
    st.error(
        f"Unable to connect to the book server at "
        f"`{st.session_state.server_url}`.\n\n"
        "Start it with:\n"
        "`uvicorn books_server:app --reload`"
    )
    st.stop()


st.divider()


# ---------------------------------------------------------------------
# Main navigation
# ---------------------------------------------------------------------

tab_browse, tab_create, tab_update, tab_delete = st.tabs(
    ["📖 Browse Books", "➕ Add Book", "✏️ Update Book", "🗑️ Delete Book"]
)


# ---------------------------------------------------------------------
# Browse
# ---------------------------------------------------------------------

with tab_browse:
    st.subheader("Book Library")
    st.markdown(
        '<div class="section-note">View all books or inspect an individual book.</div>',
        unsafe_allow_html=True,
    )

    refresh_col, lookup_col = st.columns([1, 3])

    with refresh_col:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    with lookup_col:
        lookup_id = st.number_input(
            "Find book by ID",
            min_value=1,
            step=1,
            value=1,
            label_visibility="collapsed",
        )

    if st.button("🔎 Find Book", use_container_width=True):
        try:
            book = get_book(int(lookup_id))
            st.session_state.selected_book_id = book["id"]

            st.success(f"Book #{book['id']} found")

            c1, c2, c3 = st.columns([1, 4, 4])
            c1.metric("ID", book["id"])
            c2.markdown(f"**{book['title']}**")
            c3.markdown(f"by {book['author']}")
        except Exception as exc:
            st.error(str(exc))

    st.divider()

    if not books:
        st.info("No books found in the library.")
    else:
        for book in books:
            st.markdown(
                f"""
                <div class="book-card">
                    <div class="book-title">📕 {book["title"]}</div>
                    <div class="book-author">by {book["author"]}</div>
                    <div class="book-id">Book ID: {book["id"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------

with tab_create:
    st.subheader("Add a New Book")
    st.markdown(
        '<div class="section-note">Create a new book using the POST /books/ endpoint.</div>',
        unsafe_allow_html=True,
    )

    with st.form("create_book_form", clear_on_submit=True):
        title = st.text_input(
            "Book Title",
            placeholder="e.g. Clean Code",
        )

        author = st.text_input(
            "Author",
            placeholder="e.g. Robert C. Martin",
        )

        submitted = st.form_submit_button(
            "➕ Create Book",
            use_container_width=True,
        )

        if submitted:
            if not title.strip() or not author.strip():
                st.warning("Please enter both title and author.")
            else:
                try:
                    book = create_book(title.strip(), author.strip())

                    st.success(
                        f'Book created successfully — ID {book["id"]}'
                    )

                    st.json(book)

                except requests.RequestException as exc:
                    st.error(f"Request failed: {exc}")
                except Exception as exc:
                    st.error(str(exc))


# ---------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------

with tab_update:
    st.subheader("Update a Book")
    st.markdown(
        '<div class="section-note">Update the title and author using PUT /books/{id}.</div>',
        unsafe_allow_html=True,
    )

    update_id = st.number_input(
        "Book ID",
        min_value=1,
        step=1,
        value=st.session_state.selected_book_id or 1,
        key="update_id",
    )

    if st.button("📥 Load Book", use_container_width=True):
        try:
            book = get_book(int(update_id))

            st.session_state["edit_title"] = book["title"]
            st.session_state["edit_author"] = book["author"]
            st.success(f'Loaded book #{book["id"]}')

        except Exception as exc:
            st.error(str(exc))

    edit_title = st.text_input(
        "Title",
        value=st.session_state.get("edit_title", ""),
        key="edit_title",
    )

    edit_author = st.text_input(
        "Author",
        value=st.session_state.get("edit_author", ""),
        key="edit_author",
    )

    if st.button("💾 Save Changes", use_container_width=True):
        if not edit_title.strip() or not edit_author.strip():
            st.warning("Title and author are required.")
        else:
            try:
                book = update_book(
                    int(update_id),
                    edit_title.strip(),
                    edit_author.strip(),
                )

                st.success(f'Book #{book["id"]} updated successfully.')
                st.json(book)

            except Exception as exc:
                st.error(str(exc))


# ---------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------

with tab_delete:
    st.subheader("Delete a Book")
    st.markdown(
        '<div class="section-note">Delete a book using DELETE /books/{id}.</div>',
        unsafe_allow_html=True,
    )

    delete_id = st.number_input(
        "Book ID to delete",
        min_value=1,
        step=1,
        value=1,
        key="delete_id",
    )

    st.warning(
        "⚠️ Deleting a book is permanent. The operation cannot be undone."
    )

    confirm_delete = st.checkbox(
        "I understand that this book will be permanently deleted."
    )

    if st.button(
        "🗑️ Delete Book",
        type="primary",
        use_container_width=True,
        disabled=not confirm_delete,
    ):
        try:
            result = delete_book(int(delete_id))
            st.success(result["message"])
            st.session_state.selected_book_id = None
            st.rerun()

        except Exception as exc:
            st.error(str(exc))


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------

st.divider()

st.caption(
    "Book Manager • Streamlit client • HTTP API via requests • "
    f"Connected to {st.session_state.server_url}"
)
