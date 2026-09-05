import os

import streamlit as st

from src.sybilgraph_core import (
    RingDetector,
    calibrate_thresholds,
    evaluate_pipeline,
    generate_synthetic_data,
)


@st.cache_data(show_spinner=False)
def get_thresholds(seed=99):
    return calibrate_thresholds(seed)


@st.cache_data(show_spinner=False)
def get_pipeline(seed, med_th, high_th):
    df_acc, df_sess = generate_synthetic_data(seed)
    detector = RingDetector(df_acc, df_sess)
    detector.build_bipartite_graph()
    detector.add_behavioral_similarity()
    clusters = detector.cluster_and_score()
    metrics = evaluate_pipeline(df_acc, clusters, med_th, high_th)
    cases = detector.generate_case_files(clusters, med_th, high_th)
    return df_acc, detector.G, clusters, metrics, cases


def generate_reviewer_summary(case_text):
    """Ask Gemini to summarize a SybilGraph case using only supplied evidence.

    The API key is read from GEMINI_API_KEY. Gemini is deliberately invoked only
    when the investigator requests a summary, avoiding hidden API calls on every
    Streamlit rerun.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None, "API_KEY is not configured."

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        prompt = (
            "You are assisting a fraud investigator. Read the SybilGraph case file "
            "below and write a concise 2-3 sentence investigator summary. "
            "Use only the supplied evidence. Do not invent facts, identify people, "
            "or make an enforcement recommendation. State the strongest coordination "
            "signals and any meaningful counter-evidence.\n\n"
            f"CASE FILE:\n{case_text}"
        )
        interaction = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt,
        )
        text = getattr(interaction, "output_text", None)
        if not text:
            return None, "Empty response."
        return text.strip(), None

    except Exception as exc:
        return None, f"request failed: {exc}"
