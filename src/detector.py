from .data_generation import COUPON_CATALOG

import random
import numpy as np
import pandas as pd
import networkx as nx
from scipy.spatial.distance import euclidean

class RingDetector:
    def __init__(self, df_acc, df_sess):
        self.df_acc = df_acc.drop(columns=[c for c in df_acc.columns if c.startswith('_')])
        self.df_sess = df_sess
        self.G = nx.Graph()
        
    def build_bipartite_graph(self):
        edges = []
        for _, row in self.df_acc.iterrows():
            aid = row['account_id']
            if pd.notna(row['device_fingerprint']):
                edges.append((aid, f"dev_{row['device_fingerprint']}", {'weight': 4, 'type': 'device'}))
            if pd.notna(row['payment_instrument_fragment']):
                edges.append((aid, f"pay_{row['payment_instrument_fragment']}", {'weight': 4, 'type': 'payment'}))
            if pd.notna(row['shipping_address_hash']):
                edges.append((aid, f"addr_{row['shipping_address_hash']}", {'weight': 2, 'type': 'address'}))
            if pd.notna(row['ip_address']):
                subnet = '.'.join(row['ip_address'].split('.')[:3])
                edges.append((aid, f"ip_{subnet}", {'weight': 1, 'type': 'ip'}))
                
        B = nx.Graph()
        B.add_edges_from(edges)
        
        accounts = self.df_acc['account_id'].tolist()
        for u in accounts:
            if u not in B: continue
            for attr_node in B.neighbors(u):
                for v in B.neighbors(attr_node):
                    if u < v:
                        if not self.G.has_edge(u, v):
                            self.G.add_edge(u, v, weight=0, evidence=[])
                        self.G[u][v]['weight'] += B[u][attr_node]['weight']
                        self.G[u][v]['evidence'].append(B[u][attr_node]['type'])

    def add_behavioral_similarity(self):
        vectors = {}
        for _, s in self.df_sess.iterrows():
            events = s['events']
            gaps = [max(0, events[i]['ts_offset_ms'] - events[i-1]['ts_offset_ms']) for i in range(1, len(events))]
            vectors[s['account_id']] = [np.log1p(g) for g in gaps]
            
        dim_values = {0: [], 1: [], 2: [], 3: []}
        for gaps in vectors.values():
            for dim, val in enumerate(gaps):
                if dim < 4:
                    dim_values[dim].append(val)
                    
        means = {d: np.mean(dim_values[d]) if dim_values[d] else 0.0 for d in range(4)}
        stds = {d: np.std(dim_values[d]) + 1e-9 if dim_values[d] else 1.0 for d in range(4)}
        
        z_vecs = {}
        for aid, gaps in vectors.items():
            z_vecs[aid] = np.array([(gaps[d] - means[d]) / stds[d] for d in range(len(gaps)) if d < 4])
        
        acc_list = list(z_vecs.keys())
        null_sims = []
        for _ in range(3000):
            a, b = random.sample(acc_list, 2)
            za, zb = z_vecs[a], z_vecs[b]
            k = min(len(za), len(zb))
            if k > 0:
                dist = euclidean(za[:k], zb[:k]) * np.sqrt(4.0 / k)
                null_sims.append(np.exp(-dist / 2.0))
                
        p85, p95 = np.percentile(null_sims, 85), np.percentile(null_sims, 95)
        
        for u, v in self.G.edges():
            if u in z_vecs and v in z_vecs:
                zu, zv = z_vecs[u], z_vecs[v]
                k = min(len(zu), len(zv))
                if k > 0:
                    dist = euclidean(zu[:k], zv[:k]) * np.sqrt(4.0 / k)
                    sim = np.exp(-dist / 2.0)
                    if sim >= p85:
                        self.G[u][v]['weight'] += 2 if sim >= p95 else 1
                        self.G[u][v]['evidence'].append("behavior")
                        self.G[u][v]['beh_sim'] = sim

    def cluster_and_score(self):
        communities = [c for c in nx.community.louvain_communities(self.G, weight='weight', resolution=0.9) if len(c) >= 3]
        clusters = []
        
        for i, comm in enumerate(communities):
            subG = self.G.subgraph(comm)
            n, m = subG.number_of_nodes(), subG.number_of_edges()
            edge_density = m / (n * (n - 1) / 2) if n > 1 else 0
            
            strong_edges, beh_sims, ev_types = 0, [], set()
            ev_counts = {}
            for ev_t in ['device', 'payment', 'address', 'ip', 'behavior']:
                nodes_touching = set()
                for u, v, d in subG.edges(data=True):
                    ev_list = d.get('evidence', [])
                    if ev_t in ev_list:
                        nodes_touching.add(u)
                        nodes_touching.add(v)
                if nodes_touching:
                    ev_counts[ev_t] = len(nodes_touching)
            
            for u, v, d in subG.edges(data=True):
                ev_str = " ".join(d.get('evidence', []))
                if any(t in ev_str for t in ['device', 'payment', 'behavior']):
                    strong_edges += 1
                if 'beh_sim' in d:
                    beh_sims.append(d['beh_sim'])
                for ev in d.get('evidence', []):
                    ev_types.add(ev)
                    
            strong_fraction = strong_edges / m if m > 0 else 0
            
            cluster_df = self.df_acc[self.df_acc['account_id'].isin(comm)]
            payment_counts = cluster_df['payment_instrument_fragment'].value_counts()
            independent_pays = payment_counts[payment_counts == 1].index
            ind_pay_accs = set(cluster_df[cluster_df['payment_instrument_fragment'].isin(independent_pays)]['account_id'])
            prior_accs = set(cluster_df[cluster_df['prior_legitimate_orders'] >= 2]['account_id'])
            
            counter_ev_ratio = len(ind_pay_accs.union(prior_accs)) / n
            raw_score = (0.40 * strong_fraction) + (0.25 * (min(len(ev_types), 5) / 5)) + (0.20 * (np.mean(beh_sims) if beh_sims else 0)) + (0.15 * edge_density)
            final_score = raw_score * (1 - min(0.5, counter_ev_ratio * 0.6))
            
            claimed_exposure = int(cluster_df['coupon_code_used'].map(COUPON_CATALOG).fillna(0).sum())
            
            clusters.append({
                "cluster_id": f"C_{i:04d}",
                "members": list(comm),
                "size": n,
                "score": final_score,
                "evidence_types_present": list(ev_types),
                "evidence_counts": ev_counts,
                "ind_pay_accs": list(ind_pay_accs),
                "prior_accs": list(prior_accs),
                "claimed_exposure": claimed_exposure
            })
            
        return sorted(clusters, key=lambda x: x['score'], reverse=True)

    def generate_case_files(self, clusters, threshold_medium=0.35, threshold_high=0.55):
        files = []
        for c in clusters:
            if c['score'] >= threshold_high:
                conf = "HIGH"
                action = "Hold pending promotional credits, pending review"
            elif c['score'] >= threshold_medium:
                conf = "MEDIUM"
                action = "Restrict promotional eligibility for 24h, pending review"
            else:
                conf = "LOW"
                action = "Log only - Graph topology indicates a natural shared environment (e.g., household network)."
            
            ev_for, ev_against = [], []
            ev_counts = c.get('evidence_counts', {})
            
            if 'device' in ev_counts:
                ev_for.append(f"  + {ev_counts['device']} accounts share device fingerprint lineages")
            if 'payment' in ev_counts:
                ev_for.append(f"  + {ev_counts['payment']} accounts share payment instrument fragments")
            if 'address' in ev_counts:
                ev_for.append(f"  + {ev_counts['address']} accounts share address similarity")
            if 'ip' in ev_counts:
                ev_for.append(f"  + {ev_counts['ip']} accounts share the same network subnet")
            if 'behavior' in ev_counts:
                ev_for.append(f"  + {ev_counts['behavior']} accounts show synchronized checkout timing")
            if not ev_for:
                ev_for.append("  + Weak relational ties only")
            
            if c['ind_pay_accs']:
                ev_against.append(f"  - {len(c['ind_pay_accs'])} accounts used independent payment instruments")
            if c['prior_accs']:
                ev_against.append(f"  - {len(c['prior_accs'])} accounts have aged legitimate history")
            if not ev_against:
                ev_against.append("  - None identified")

            c['case_file_text'] = f"CASE {c['cluster_id']}\n{c['size']} accounts under review · ₹{c['claimed_exposure']} claimed to date\n\nCONFIDENCE: {conf} (Score: {c['score']:.2f})\n\nEvidence for coordination\n{chr(10).join(ev_for)}\n\nEvidence against\n{chr(10).join(ev_against)}\n\nRecommended action\n  {action}"
            c['confidence'] = conf
            files.append(c)
        return files
