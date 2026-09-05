import streamlit as st

def apply_styles():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stHeader"] { background: transparent; }
        footer { display: none; }

        .block-container {
            max-width: 1460px;
            padding: 30px 42px 44px;
        }

        .rt-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            border-bottom: 1px solid #2a3038;
            padding-bottom: 18px;
            margin-bottom: 22px;
        }

        .rt-title {
            font-size: 25px;
            line-height: 1.1;
            font-weight: 700;
            letter-spacing: -0.4px;
        }

        .rt-subtitle {
            margin-top: 5px;
            color: #8d949e;
            font-size: 12px;
        }

        .rt-status {
            color: #8d949e;
            font-size: 11px;
            border: 1px solid #303640;
            padding: 6px 10px;
            border-radius: 5px;
            background: #111419;
        }

        .rt-status::before {
            content: "●";
            color: #62b981;
            margin-right: 7px;
        }

        .rt-kicker {
            color: #7f8792;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: .09em;
            font-weight: 700;
            margin-bottom: 7px;
        }

        .rt-section-title {
            font-size: 19px;
            font-weight: 680;
            margin-bottom: 3px;
        }

        .rt-note {
            color: #8c939d;
            font-size: 12px;
            margin-bottom: 15px;
        }

        .rt-metric {
            border: 1px solid #292f38;
            background: #12161b;
            border-radius: 7px;
            padding: 14px 15px;
            min-height: 78px;
        }

        .rt-metric-label {
            color: #8b929c;
            font-size: 10px;
            margin-bottom: 7px;
        }

        .rt-metric-value {
            color: #eceff3;
            font-size: 22px;
            font-weight: 700;
        }

        .rt-good { color: #65bd88; }
        .rt-warning { color: #d6ad55; }
        .rt-danger { color: #e45c68; }

        .rt-case-id {
            font-size: 22px;
            font-weight: 700;
            margin: 2px 0 5px;
        }

        .rt-case-meta {
            color: #aeb4bc;
            font-size: 12px;
            line-height: 1.55;
        }

        .rt-evidence {
            border-top: 1px solid #272d35;
            padding: 9px 0;
            color: #c8cdd4;
            font-size: 12px;
        }

        .rt-evidence strong {
            color: #e05e69;
            margin-right: 5px;
        }

        .rt-ai-note {
            border: 1px solid #304052;
            background: #12171c;
            border-left: 3px solid #7897b8;
            border-radius: 5px;
            padding: 11px 12px;
            color: #cbd2da;
            font-size: 12px;
            line-height: 1.55;
        }

        .rt-action {
            border: 1px solid #3a3032;
            border-left: 3px solid #d65c67;
            background: #151719;
            border-radius: 5px;
            padding: 11px 12px;
            color: #c9cdd2;
            font-size: 12px;
            line-height: 1.5;
        }

        .rt-clear {
            border: 1px solid #294436;
            background: #111914;
            border-radius: 5px;
            padding: 11px 12px;
            color: #a8cfb6;
            font-size: 12px;
        }

        .rt-queue {
            border: 1px solid #293541;
            background: #12171c;
            border-radius: 5px;
            padding: 11px 13px;
            min-height: 76px;
        }

        .rt-queue-id {
            color: #9bb8d1;
            font-size: 10px;
            font-weight: 700;
        }

        .rt-queue-score {
            font-size: 17px;
            font-weight: 700;
            margin-top: 4px;
        }

        .rt-queue-note {
            color: #7e8791;
            font-size: 10px;
            margin-top: 3px;
        }

        div[data-baseweb="tab-list"] {
            gap: 0;
            border-bottom: 1px solid #292f38;
        }

        button[data-baseweb="tab"] {
            font-size: 12px !important;
            font-weight: 600 !important;
            padding: 10px 17px !important;
        }

        div[data-testid="stSelectbox"] label {
            color: #7f8792 !important;
            font-size: 10px !important;
            text-transform: uppercase;
            letter-spacing: .08em;
        }

        div[data-testid="stMetric"] {
            background: #12161b;
            border: 1px solid #292f38;
            border-radius: 7px;
            padding: 8px 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
