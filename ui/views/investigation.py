"""Investigation / case review view."""

import streamlit as st

from ..components import counter_evidence, evidence_list, risk_badge, section
from ..data import generate_reviewer_summary
from ..graphs import network_figure


ACTIONS = {
    "HIGH": "Hold pending promotional credits and review the case.",
    "MEDIUM": "Restrict promotional eligibility for 24 hours pending review.",
    "LOW": "Log only; the topology is consistent with a natural shared environment.",
}


def render(graph, df_acc, cases, metrics):
    review_cases = [c for c in cases if c["confidence"] in {"HIGH", "MEDIUM"}]
    cleared_cases = [c for c in cases if c["confidence"] == "LOW"]
    choices = review_cases + cleared_cases[:3]

    if not choices:
        st.info("No cases crossed the configured investigation threshold.")
        return

    section(
        "Case review",
        "Investigation",
        "Review connected-account clusters, evidence, and the model-assisted case summary.",
    )

    labels = [f'{c["cluster_id"]} · {c["confidence"]}' for c in choices]
    selected_label = st.selectbox(
        "Case", labels, label_visibility="collapsed", key="investigation_case"
    )
    case = choices[labels.index(selected_label)]
    confidence = case["confidence"]

    left, right = st.columns([1.55, 1], gap="large")

    with left:
        st.markdown("**Relational evidence**")
        fig = network_figure(
            graph,
            case["members"],
            color="#5b9b7b" if confidence == "LOW" else "#d66570",
            height=500,
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False},
            key="investigation_graph",
        )
        st.caption(
            f'{case["size"]} accounts · hover a node to inspect its linked evidence'
        )

    with right:
        st.markdown(
            f'<div class="rt-case-id">{case["cluster_id"]}</div>'
            f'<div class="rt-case-meta">{case["size"]} accounts under review · '
            f'₹{case["claimed_exposure"]:,} claimed exposure<br>'
            f'{risk_badge(confidence, case["score"])}</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="rt-section">Evidence for coordination</div>', unsafe_allow_html=True)
        evidence_list(case)

        st.markdown('<div class="rt-section">Counter-evidence</div>', unsafe_allow_html=True)
        counter_evidence(case)

        st.markdown('<div class="rt-section">Recommended action</div>', unsafe_allow_html=True)
        if confidence == "LOW":
            st.markdown(
                '<div class="rt-clear">No enforcement action. Record the cluster for context.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="rt-action">{ACTIONS[confidence]}</div>',
                unsafe_allow_html=True,
            )

            with st.expander("Scoring details"):
                st.caption(
                    "Score = 40% strong relational ties + 25% evidence diversity + "
                    "20% behavioral similarity + 15% graph density, with a counter-evidence penalty."
                )

            st.markdown('<div class="rt-section">Investigator summary</div>', unsafe_allow_html=True)
            st.caption("Summarizes the existing case file; it does not change the risk score.")
            if st.button(
                "Generate summary",
                key=f"gemini_{case['cluster_id']}",
                type="secondary",
            ):
                with st.spinner("Generating investigator summary…"):
                    summary, error = generate_reviewer_summary(case["case_file_text"])
                if summary:
                    st.session_state[f"gemini_summary_{case['cluster_id']}"] = summary
                else:
                    st.session_state[f"gemini_error_{case['cluster_id']}"] = error

            summary = st.session_state.get(f"gemini_summary_{case['cluster_id']}")
            error = st.session_state.get(f"gemini_error_{case['cluster_id']}")
            if summary:
                st.markdown(f'<div class="rt-ai-note">{summary}</div>', unsafe_allow_html=True)
            elif error:
                st.warning(error)

            if st.button("Approve action", type="primary", key=f"approve_{case['cluster_id']}"):
                if "approved_actions" not in st.session_state:
                    st.session_state.approved_actions = []
                entry = f'{case["cluster_id"]} · {confidence}'
                if entry not in st.session_state.approved_actions:
                    st.session_state.approved_actions.append(entry)
                st.success("Action recorded.")

    st.divider()
    section(
        "Manual review",
        "Borderline cases",
        "Clusters close to a calibrated decision boundary.",
    )

    exceptions = metrics.get("exceptions", [])
    if not exceptions:
        st.caption("No borderline cases.")
        return

    cols = st.columns(min(len(exceptions), 4))
    for index, exception in enumerate(exceptions):
        with cols[index % len(cols)]:
            st.markdown(
                f'<div class="rt-queue"><div class="rt-queue-id">{exception["cluster_id"]}</div>'
                f'<div class="rt-queue-score">{exception["score"]:.2f}</div>'
                f'<div class="rt-queue-note">Within ±0.05 of a decision boundary</div></div>',
                unsafe_allow_html=True,
            )
