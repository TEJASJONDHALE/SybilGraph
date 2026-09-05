import pandas as pd
import streamlit as st
from ui.graphs import replay_figure

def render(graph, df_acc, cases):
    st.markdown('<div class="rt-kicker">Replay</div>', unsafe_allow_html=True)
    st.markdown('<div class="rt-section-title">Cluster formation</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="rt-note">Step through account creation to see when the network becomes connected.</div>',
        unsafe_allow_html=True,
    )

    if not cases:
        st.info("No cases are available for replay.")
        return

    selected_id = st.selectbox(
        "Case", [c["cluster_id"] for c in cases],
        key="replay_case", label_visibility="visible"
    )
    case = next(c for c in cases if c["cluster_id"] == selected_id)

    dates = pd.to_datetime(
        df_acc[df_acc["account_id"].isin(case["members"])]["created_at"]
    )
    start, end = dates.min(), dates.max()

    if start == end:
        st.info("All accounts in this case share the same creation time.")
        return

    current = st.slider(
        "Creation time",
        min_value=start.to_pydatetime(),
        max_value=end.to_pydatetime(),
        value=end.to_pydatetime(),
        format="DD MMM YYYY · HH:mm",
    )

    active = []
    for account_id in case["members"]:
        created = pd.to_datetime(
            df_acc.loc[df_acc["account_id"] == account_id, "created_at"].iloc[0]
        )
        if created <= current:
            active.append(account_id)

    st.plotly_chart(
        replay_figure(graph, case["members"], active),
        use_container_width=True,
        config={"displayModeBar": False},
    )
    st.caption(
        f"{len(active)} of {len(case['members'])} accounts active at "
        f"{current.strftime('%d %b %Y, %H:%M')}."
    )
