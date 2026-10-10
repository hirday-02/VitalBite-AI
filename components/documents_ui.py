
import streamlit as st


def render_documents_tab(user_id=None):
    """Display the Documents feature as coming soon in the demo."""

    st.markdown(
        """
        <div style="
            padding: 2.5rem 1rem;
            text-align: center;
            background: rgba(255, 255, 255, 0.75);
            border: 1px solid #DCE7F1;
            border-radius: 20px;
            margin: 1rem 0;
        ">
            <div style="font-size: 3rem; margin-bottom: 0.75rem;">
                st.subheader("Documents")
            </div>
            <h2 style="color: #0F172A; margin-bottom: 0.5rem;">
                Health Documents
            </h2>
            <p style="color: #0284C7; font-weight: 700;">
                Coming Soon
            </p>
            <p style="color: #64748B; max-width: 600px;
                      margin: 0 auto; line-height: 1.7;">
                We are working on secure health document uploads,
                lab report summaries, and AI-assisted interpretation.
                This feature is not available in the current demo.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
