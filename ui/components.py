import html
import streamlit as st


def header():
    st.markdown(
        """
        <div class="rt-header">
            <div>
                <div class="rt-title">SybilGraph</div>
                <div class="rt-subtitle">Coordinated abuse investigation console</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, tone=""):
    st.markdown(
        f"""
        <div class="rt-metric">
            <div class="rt-metric-label">{html.escape(str(label))}</div>
            <div class="rt-metric-value rt-{html.escape(str(tone))}">{html.escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title, kicker=None, description=None):
    """Render a compact, consistent section heading."""
    if kicker:
        st.markdown(
            f'<div class="rt-kicker">{html.escape(str(kicker))}</div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        f'<div class="rt-section-title">{html.escape(str(title))}</div>',
        unsafe_allow_html=True,
    )
    if description:
        st.markdown(
            f'<div class="rt-note">{html.escape(str(description))}</div>',
            unsafe_allow_html=True,
        )


def risk_badge(confidence, score):
    confidence = str(confidence).upper()
    tone = {"HIGH": "danger", "MEDIUM": "warning", "LOW": "good"}.get(confidence, "")
    return (
        f'<span class="rt-{tone}"><strong>{html.escape(confidence)}</strong>'
        f' · score {float(score):.2f}</span>'
    )


def evidence_list(case):
    """Render only evidence that is actually present in the case file."""
    labels = {
        "device": "Shared device fingerprint lineage",
        "payment": "Shared payment instrument fragments",
        "address": "Shared address similarity",
        "ip": "Shared network subnet",
        "behavior": "Synchronized checkout timing",
    }
    counts = case.get("evidence_counts", {}) or {}
    rendered = False
    for key, label in labels.items():
        count = counts.get(key, 0)
        if count:
            rendered = True
            st.markdown(
                f'<div class="rt-evidence"><strong>{int(count)}</strong>{html.escape(label)}</div>',
                unsafe_allow_html=True,
            )
    if not rendered:
        st.caption("No individual evidence categories were returned for this case.")


def counter_evidence(case):
    """Render the legitimate/shared-environment signals that reduce confidence."""
    items = []
    independent = case.get("ind_pay_accs") or []
    prior = case.get("prior_accs") or []
    if independent:
        items.append(f"{len(independent)} accounts used independent payment instruments")
    if prior:
        items.append(f"{len(prior)} accounts have prior legitimate account history")

    if not items:
        st.caption("No material counter-evidence was identified.")
        return

    for item in items:
        st.markdown(
            f'<div class="rt-evidence"><strong>—</strong>{html.escape(item)}</div>',
            unsafe_allow_html=True,
        )
 