import streamlit as st
from ui.components import header 
from ui.data import get_pipeline, get_thresholds
from ui.styles import apply_styles
from ui.views.evaluation import render as render_evaluation
from ui.views.investigation import render as render_investigation
from ui.views.replay import render as render_replay

st.set_page_config(
    page_title="SybilGraph",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_styles()
header()

DATA_SEED = 2
CALIBRATION_SEED = 99

med_th, high_th = get_thresholds(CALIBRATION_SEED)
df_acc, graph, clusters, metrics, cases = get_pipeline(
    DATA_SEED, med_th, high_th
)


tab_investigation, tab_replay, tab_evaluation = st.tabs(
    ["Investigation", "Replay", "Evaluation"]
)

with tab_investigation:
    render_investigation(graph, df_acc, cases, metrics)

with tab_replay:
    render_replay(graph, df_acc, cases)

with tab_evaluation:
    render_evaluation(metrics)
