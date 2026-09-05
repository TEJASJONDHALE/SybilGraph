import streamlit as st
from ui.graphs import precision_recall_figure

def render(metrics):
    st.markdown('<div class="rt-kicker">Evaluation</div>', unsafe_allow_html=True)
    st.markdown('<div class="rt-section-title">Precision–recall performance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="rt-note">Held-out evaluation at the calibrated medium-risk operating point.</div>',
        unsafe_allow_html=True,
    )

    st.plotly_chart(
        precision_recall_figure(metrics),
        use_container_width=True,
        config={"displayModeBar": False},
    )

    a, b, c = st.columns(3)
    a.metric("Medium threshold", f"{metrics['med_th']:.3f}")
    b.metric("Precision", f"{metrics['precision'] * 100:.1f}%")
    c.metric("Recall", f"{metrics['recall'] * 100:.1f}%")
