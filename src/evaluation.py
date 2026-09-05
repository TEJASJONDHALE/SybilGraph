import numpy as np
from sklearn.metrics import precision_recall_curve
from .data_generation import COUPON_CATALOG


def calibrate_thresholds(train_seed=99):
    """Calibrate medium/high thresholds on a separate synthetic seed."""
    from .data_generation import generate_synthetic_data
    from .detector import RingDetector

    df_acc, df_sess = generate_synthetic_data(train_seed)
    detector = RingDetector(df_acc, df_sess)
    detector.build_bipartite_graph()
    detector.add_behavioral_similarity()
    clusters = detector.cluster_and_score()

    gt = df_acc.set_index("account_id")["_is_ring_member"].to_dict()
    y_true = [1 if gt[aid] else 0 for aid in gt]
    account_scores = {
        member: cluster["score"]
        for cluster in clusters
        for member in cluster["members"]
    }
    y_score = [account_scores.get(aid, 0.0) for aid in gt]

    precisions, recalls, thresholds = precision_recall_curve(y_true, y_score)

    def choose(min_precision, fallback):
        valid = np.where(precisions[:-1] >= min_precision)[0]
        if not len(valid):
            return float(fallback)
        best_recall = np.max(recalls[:-1][valid])
        candidates = valid[recalls[:-1][valid] == best_recall]
        return float(np.min(thresholds[candidates]))

    medium = choose(0.85, 0.35)
    high = choose(0.95, 0.55)
    high = max(high, medium)
    return medium, high


def evaluate_pipeline(df_acc, clusters, med_th, high_th):
    """Evaluate the calibrated operating point on the evaluation dataset."""
    gt = df_acc.set_index("account_id")[["_is_ring_member", "_ring_id"]].to_dict("index")
    ring_members = {aid for aid, data in gt.items() if data["_is_ring_member"]}

    account_scores = {
        member: cluster["score"]
        for cluster in clusters
        for member in cluster["members"]
    }
    y_true = [1 if data["_is_ring_member"] else 0 for data in gt.values()]
    y_score = [account_scores.get(aid, 0.0) for aid in gt]
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_score)

    predicted = {
        member
        for cluster in clusters
        if cluster["score"] >= med_th
        for member in cluster["members"]
    }

    tp_ids = predicted & ring_members
    fp_ids = predicted - ring_members
    fn_ids = ring_members - predicted

    tp = len(tp_ids)
    fp = len(fp_ids)
    fn = len(fn_ids)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0

    fp_cost_unit = 120
    tp_val = int(
        df_acc[df_acc["account_id"].isin(tp_ids)]["coupon_code_used"]
        .map(COUPON_CATALOG).fillna(0).sum()
    )
    fn_val = int(
        df_acc[df_acc["account_id"].isin(fn_ids)]["coupon_code_used"]
        .map(COUPON_CATALOG).fillna(0).sum()
    )
    gross_flagged = int(
        df_acc[df_acc["account_id"].isin(predicted)]["coupon_code_used"]
        .map(COUPON_CATALOG).fillna(0).sum()
    )

    exceptions = [
        cluster for cluster in clusters
        if abs(cluster["score"] - med_th) <= 0.05
        or abs(cluster["score"] - high_th) <= 0.05
    ]

    return {
        "med_th": float(med_th),
        "high_th": float(high_th),
        "precision": precision,
        "recall": recall,
        "gross_flagged": gross_flagged,
        "net_saved": tp_val - (fp * fp_cost_unit) - fn_val,
        "fp_cost": fp * fp_cost_unit,
        "exceptions": exceptions,
        "curve": (thresholds, precisions[:-1], recalls[:-1]),
    }
