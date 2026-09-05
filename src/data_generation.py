import uuid
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

COUPON_CATALOG = {"WELCOME150": 150}

def generate_synthetic_data(seed=2):
    random.seed(seed)
    np.random.seed(seed)
    
    accounts, sessions = [], []
    base_time = datetime(2026, 3, 1, 10, 0, 0)
    
    def make_gaps(base=None, jitter=0.0):
        if base is None: 
            return [np.random.normal(1500, 800) for _ in range(4)]
        return [max(100, b + np.random.normal(0, b * jitter)) for b in base]
    
    def build_session(acc_id, gaps, used_coupon):
        events = [{"action": "page_view", "page": "home", "ts_offset_ms": 0}]
        ts = 0
        actions = ["page_view_product", "add_to_cart", "apply_coupon", "checkout"]
        if not used_coupon:
            actions = ["page_view_product", "add_to_cart", "checkout"]
            gaps[2] = (gaps[2] + gaps[3]) / 2
            
        for i, action in enumerate(actions):
            ts += int(gaps[i])
            events.append({"action": action, "ts_offset_ms": ts})
        return {"session_id": f"sess_{uuid.uuid4().hex[:8]}", "account_id": acc_id, "events": events}

    for _ in range(2500):
        acc_id = f"acc_{uuid.uuid4().hex[:8]}"
        used_coupon = random.random() < 0.25
        accounts.append({
            "account_id": acc_id,
            "created_at": (base_time + timedelta(hours=random.randint(1, 720))),
            "device_fingerprint": f"dfp_{uuid.uuid4().hex[:8]}",
            "ip_address": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
            "shipping_address_hash": f"addr_{uuid.uuid4().hex[:6]}",
            "payment_instrument_fragment": f"upi:user_{uuid.uuid4().hex[:8]}@bank",
            "coupon_code_used": "WELCOME150" if used_coupon else None,
            "order_amount": random.randint(300, 2500),
            "prior_legitimate_orders": int(np.random.exponential(0.5)),
            "_is_ring_member": False,
            "_ring_id": None,
            "_is_noisy_legit": False,
            "_legit_cluster_id": None
        })
        sessions.append(build_session(acc_id, make_gaps(), used_coupon))

    for r in range(8):
        ring_size = random.randint(8, 16)
        shared_devices = [f"dfp_{uuid.uuid4().hex[:8]}" for _ in range(2)]
        shared_subnet = f"103.24.{random.randint(1, 255)}"
        shared_addrs = [f"addr_{uuid.uuid4().hex[:6]}" for _ in range(2)]
        shared_payments = [f"upi:ring{r}_{uuid.uuid4().hex[:4]}@bank" for _ in range(2)]
        ring_gaps = [random.uniform(500, 1500) for _ in range(4)]
        ring_start_time = base_time + timedelta(hours=random.randint(100, 600))
        
        for i in range(ring_size):
            acc_id = f"acc_{uuid.uuid4().hex[:8]}"
            dev = f"dfp_{uuid.uuid4().hex[:8]}" if random.random() < 0.15 else random.choice(shared_devices)
            pay = f"upi:user_{uuid.uuid4().hex[:8]}@bank" if random.random() < 0.15 else random.choice(shared_payments)
            accounts.append({
                "account_id": acc_id,
                "created_at": ring_start_time + timedelta(minutes=i*15),
                "device_fingerprint": dev,
                "ip_address": f"{shared_subnet}.{random.randint(1,254)}",
                "shipping_address_hash": random.choice(shared_addrs),
                "payment_instrument_fragment": pay,
                "coupon_code_used": "WELCOME150",
                "order_amount": random.randint(500, 1000),
                "prior_legitimate_orders": random.randint(1, 3) if random.random() < 0.1 else 0,
                "_is_ring_member": True,
                "_ring_id": f"ring_{r:03d}",
                "_is_noisy_legit": False,
                "_legit_cluster_id": None
            })
            sessions.append(build_session(acc_id, make_gaps(ring_gaps, 0.08), True))

    for l in range(5):
        legit_size = random.randint(4, 6)
        shared_ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
        shared_addr = f"addr_{uuid.uuid4().hex[:6]}"
        legit_start_time = base_time + timedelta(hours=random.randint(10, 700))
        
        for i in range(legit_size):
            acc_id = f"acc_{uuid.uuid4().hex[:8]}"
            used_coupon = random.random() < 0.4
            accounts.append({
                "account_id": acc_id,
                "created_at": legit_start_time + timedelta(hours=i*2),
                "device_fingerprint": f"dfp_{uuid.uuid4().hex[:8]}",
                "ip_address": shared_ip,
                "shipping_address_hash": shared_addr,
                "payment_instrument_fragment": f"upi:user_{uuid.uuid4().hex[:8]}@bank",
                "coupon_code_used": "WELCOME150" if used_coupon else None,
                "order_amount": random.randint(300, 2500),
                "prior_legitimate_orders": random.randint(0, 5),
                "_is_ring_member": False,
                "_ring_id": None,
                "_is_noisy_legit": True,
                "_legit_cluster_id": f"legit_{l:03d}"
            })
            sessions.append(build_session(acc_id, make_gaps(), used_coupon))

    df_acc = pd.DataFrame(accounts)
    df_acc = df_acc.sample(frac=1, random_state=seed).reset_index(drop=True)
    return df_acc, pd.DataFrame(sessions)
