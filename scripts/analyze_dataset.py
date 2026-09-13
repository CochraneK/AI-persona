#!/usr/bin/env python
"""数据质量分析脚本：检查 Persona 数据集的结构和分布"""

import json
import os
from collections import defaultdict, Counter

# 相对于 scripts/ 定位到 dataset/
DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "dataset", "persona_dataset_v1.json"
)

with open(DATASET_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

personas = data["personas"]
meta = data["meta"]
errors = data["errors"]

print("=" * 85)
print("  数据集深度分析")
print("=" * 85)
print(f"  生成时间: {meta['generated_at']}")
print(f"  总数: {meta['total_personas']}")
print(f"  诊断数: {meta['diagnoses']}")
print(f"  每诊断: {meta['per_diagnosis']}")
print(f"  文件大小: 3.71 MB")
print(f"  错误数: {len(errors)}")
print("=" * 85)
print()

# ====================================================================
# 1. 按诊断分组统计
# ====================================================================
print("─" * 85)
print(f"{'诊断':25s} {'N':>4s} {'O':>5s} {'C':>5s} {'E':>5s} {'A':>5s} {'N(神)':>5s}  {'弧线分布(正/平/负)':25s}")
print("─" * 85)

dx_stats = defaultdict(lambda: {"o": [], "c": [], "e": [], "a": [], "n": [], "arcs": [], "ages": []})

for rec in personas:
    dx = rec["diagnosis_key"]
    o = rec.get("ocean", {})
    for dim, key in [("o","O"),("c","C"),("e","E"),("a","A"),("n","N")]:
        v = o.get(key)
        if isinstance(v, (int, float)):
            dx_stats[dx][dim].append(v)
    dx_stats[dx]["arcs"].append(rec.get("arc_type", "?"))
    dx_stats[dx]["ages"].append(rec.get("age", 0))

sorted_dxs = sorted(dx_stats.keys())
for dx in sorted_dxs:
    s = dx_stats[dx]
    n = len(s["o"])
    def avg(lst): return sum(lst) / len(lst) if lst else 0
    o_avg, c_avg, e_avg, a_avg, n_avg = [avg(s[d]) for d in ["o","c","e","a","n"]]
    arc_c = Counter(s["arcs"])
    arc_str = f"正={arc_c.get('positive',0)} 平={arc_c.get('flat',0)} 负={arc_c.get('negative',0)}"
    print(f"{dx:25s} {n:4d} {o_avg:5.2f} {c_avg:5.2f} {e_avg:5.2f} {a_avg:5.2f} {n_avg:5.2f}  {arc_str:25s}")

print("─" * 85)
print()

# ====================================================================
# 2. 健康 vs 临床 OCEAN 对比
# ====================================================================
healthy = [r for r in personas if r["diagnosis_key"] == "healthy"]
clinical = [r for r in personas if r["diagnosis_key"] != "healthy"]

def ocean_mean(recs, dim_key):
    vals = [r.get("ocean", {}).get(dim_key, 0) for r in recs
            if isinstance(r.get("ocean", {}).get(dim_key), (int, float))]
    return sum(vals) / len(vals) if vals else 0

print("健康 vs 临床 OCEAN 对比:")
print(f"{'维度':10s} {'健康对照 (n=20)':>15s} {'临床诊断 (n=720)':>16s}  {'差异':>8s}")
print("-" * 52)
for dim, key in [("O","O"),("C","C"),("E","E"),("A","A"),("N","N")]:
    hv = ocean_mean(healthy, key)
    cv = ocean_mean(clinical, key)
    print(f"{dim:10s} {hv:15.2f} {cv:16.2f}  {cv-hv:+8.2f}")

print()

# ====================================================================
# 3. 全局分布
# ====================================================================
all_arcs = Counter(r["arc_type"] for r in personas)
print(f"弧线分布:        {dict(all_arcs)}")

all_genders = Counter(r.get("gender", "?") for r in personas)
print(f"性别分布:        {dict(all_genders)}")

all_ages = [r.get("age", 0) for r in personas if r.get("age")]
print(f"年龄:            min={min(all_ages)}, max={max(all_ages)}, avg={sum(all_ages)/len(all_ages):.1f}")

total_events = sum(len(r.get("life_events", [])) for r in personas)
print(f"生活事件总数:    {total_events}")
print(f"人均事件数:      {total_events/len(personas):.1f}")

all_occupations = set(r.get("occupation", "") for r in personas)
print(f"职业种类:        {len(all_occupations)}")

all_lcales = Counter(r.get("locale", "?") for r in personas)
print(f"地区分布:        {dict(all_lcales)}")

all_education = Counter(r.get("education", "?") for r in personas)
print(f"教育程度分布:    {dict(all_education)}")

all_marital = Counter(r.get("marital_status", "?") for r in personas)
print(f"婚姻状况分布:    {dict(all_marital)}")

all_erikson = Counter(r.get("erikson_stage", {}).get("stage", "?") for r in personas)
print(f"Erikson阶段分布: {dict(all_erikson)}")

print()

# ====================================================================
# 4. Core Desire / Core Fear TOP10
# ====================================================================
desires = Counter(r.get("core_desire", "") for r in personas)
fears = Counter(r.get("core_fear", "") for r in personas)

print(f"{'Top 10 核心欲望':30s} {'Top 10 核心恐惧':30s}")
print("-" * 60)
for (d, dc), (f_, fc) in zip(desires.most_common(10), fears.most_common(10)):
    print(f"{d:28s} x{dc:3d}  |  {f_:28s} x{fc:3d}")

print()

# ====================================================================
# 5. N 维度极端值诊断
# ====================================================================
print("N(神经质) 最高的 5 个诊断:")
dx_n = [(dx, sum(s["n"])/len(s["n"]) if s["n"] else 0) for dx, s in dx_stats.items()]
dx_n.sort(key=lambda x: -x[1])
for dx, n_val in dx_n[:5]:
    print(f"  {dx:25s}  N={n_val:.2f}")

print()
print("N(神经质) 最低的 5 个诊断:")
for dx, n_val in dx_n[-5:]:
    print(f"  {dx:25s}  N={n_val:.2f}")

print()

# 也要修正 CSV summary 中的 ocean 访问
# 在 generate_dataset.py 中 CSV 列目前用了 ocean.get("openness") 等
# 应该改为 ocean.get("O") 等单字母键
# ====================================================================
print("Core Fear 多样性 (按诊断):")
dx_fears = defaultdict(set)
for r in personas:
    dx_fears[r["diagnosis_key"]].add(r.get("core_fear", ""))
for dx in sorted(dx_fears.keys()):
    fears_set = dx_fears[dx]
    print(f"  {dx:25s}  {len(fears_set)} 种不同恐惧 ({'≥5种✅' if len(fears_set) >= 5 else '<5种⚠️'})")

print()
print("✅ 分析完成")
