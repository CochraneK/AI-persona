#!/usr/bin/env python
"""
大规模 Persona 数据集生成脚本

策略：
  - 37 个诊断 × 20 个不同 seed = 740 Personas
  - 每个诊断从 seed 0~19 各生成一个，保证复现性
  - 输出为结构化 JSON，保留全部核心字段（不含完整 System Prompt）
  - 输出也同时生成一个 CSV 摘要（方便快速浏览）

输出：
  - outputs/persona_dataset_v1.json        (完整数据集)
  - outputs/persona_dataset_v1_summary.csv (摘要)
"""

import json
import os
import sys
import csv
import time
from datetime import datetime

# 确保能导入 core 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import generate_persona, DIAGNOSIS_OCEAN_RANGES


# ====================================================================
# 配置
# ====================================================================
PER_DIAGNOSIS = 20       # 每个诊断生成多少个
TOTAL_SEEDS = range(50)  # 可用的 seed 池

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "dataset"
)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 要在输出中包含的字段
PERSONA_FIELDS = [
    "label", "gender", "age", "education", "locale", "marital_status",
    "ocean", "ocean_description",
    "personality_tags", "cognitive_styles", "coping_styles",
    "social_relations", "values_beliefs", "communication_style",
    "lifestyle_habits", "skills_abilities", "erikson_stage",
    "formative_wound", "compensatory_desire", "storr_need",
    "arc_type",
    "core_desire", "core_fear", "dysfunctional_beliefs", "stress_pattern",
    "triggers", "safety_behaviors",
    "life_events",
    "occupation", "hidden_experiences",
    # --- Archetype Grid (v1.2) ---
    "archetype_key", "archetype_name", "archetype_one_liner",
]


def serialize_persona(p) -> dict:
    """将 Persona 对象序列化为可 JSON 序列化的 dict"""
    record = {
        "diagnosis_key": getattr(p, "primary_diagnosis_en", p.label.rsplit("_", 1)[0] if "_" in p.label else p.label),
        "seed": None,  # 由外部填入
    }
    for field in PERSONA_FIELDS:
        val = getattr(p, field, None)

        # LifeEvent 列表特殊处理
        if field == "life_events" and val:
            record[field] = [
                {
                    "name_cn": e.name_cn,
                    "name_en": e.name_en,
                    "domain": getattr(e, "domain", ""),
                    "stage": getattr(e, "stage", ""),
                    "valence": getattr(e, "valence", ""),
                    "lcu": getattr(e, "lcu", 50),
                    "description": getattr(e, "description_cn", e.name_cn),
                }
                for e in val
            ]
        elif isinstance(val, dict):
            record[field] = val
        elif isinstance(val, list):
            record[field] = [str(v) for v in val]
        elif val is not None:
            record[field] = val
        else:
            record[field] = None

    return record


def generate_dataset(diagnoses=None, per_diagnosis=None):
    """主生成函数

    Args:
        diagnoses: 诊断键列表；None = 全部诊断（DIAGNOSIS_OCEAN_RANGES 的键）
        per_diagnosis: 每个诊断生成多少个；None = 使用 PER_DIAGNOSIS 常量
    """
    diagnoses = list(diagnoses) if diagnoses else sorted(DIAGNOSIS_OCEAN_RANGES.keys())
    n_per = per_diagnosis if per_diagnosis else PER_DIAGNOSIS
    total_expected = len(diagnoses) * n_per

    print(f"=" * 60)
    print(f"  大规模 Persona 数据集生成")
    print(f"  诊断数: {len(diagnoses)}")
    print(f"  每诊断: {n_per}")
    print(f"  预计总数: {total_expected}")
    print(f"=" * 60)
    print()

    all_personas = []
    errors = []

    t_start = time.time()

    for diag_idx, diag in enumerate(diagnoses, 1):
        diag_start = time.time()
        diag_personas = []

        for seed in range(n_per):
            try:
                p = generate_persona(diag, rng_seed=seed)
                record = serialize_persona(p)
                record["seed"] = seed
                diag_personas.append(record)
            except Exception as e:
                errors.append({"diagnosis": diag, "seed": seed, "error": str(e)})

        all_personas.extend(diag_personas)
        elapsed = time.time() - diag_start
        ok = len(diag_personas)
        fail = n_per - ok
        if fail:
            status = f"⚠️ {ok}/{n_per} (失败 {fail})"
        else:
            status = f"✅ {ok}/{n_per}"
        print(f"  [{diag_idx:2d}/{len(diagnoses)}] {diag:25s}  {status}  "
              f"({elapsed:.2f}s)")

    t_total = time.time() - t_start
    print()
    print(f"=" * 60)
    print(f"  生成完成!")
    print(f"  耗时: {t_total:.2f}s")
    print(f"  成功: {len(all_personas)}")
    print(f"  失败: {len(errors)}")
    print(f"=" * 60)
    print()

    return all_personas, errors, t_total


def save_dataset(all_personas, errors, elapsed, json_path=None, csv_path=None):
    """保存数据集为 JSON + CSV 摘要

    Args:
        json_path: 自定义 JSON 输出路径；None = dataset/persona_dataset_v1.json
        csv_path: 自定义 CSV 输出路径；None = dataset/persona_dataset_v1_summary.csv
    """
    json_path = json_path or os.path.join(OUTPUT_DIR, "persona_dataset_v1.json")
    csv_path = csv_path or os.path.join(OUTPUT_DIR, "persona_dataset_v1_summary.csv")

    # --- JSON ---
    dataset = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "version": "v1",
            "total_personas": len(all_personas),
            "diagnoses": len(DIAGNOSIS_OCEAN_RANGES),
            "per_diagnosis": PER_DIAGNOSIS,
            "fields": PERSONA_FIELDS,
            "elapsed_seconds": round(elapsed, 2),
            "errors": len(errors),
        },
        "errors": errors,
        "personas": all_personas,
    }

    json_path = json_path or os.path.join(OUTPUT_DIR, "persona_dataset_v1.json")
    csv_path = csv_path or os.path.join(OUTPUT_DIR, "persona_dataset_v1_summary.csv")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=1)
    file_size_mb = os.path.getsize(json_path) / (1024 * 1024)
    print(f"  JSON: {json_path}")
    print(f"  大小: {file_size_mb:.2f} MB")

    # --- CSV 摘要 ---
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id", "diagnosis", "seed",
            "o_O", "o_C", "o_E", "o_A", "o_N",
            "gender", "age", "education", "locale", "marital_status",
            "occupation",
            "core_desire", "core_fear",
            "formative_wound_short",
            "arc_type", "erikson_stage",
            "life_events_count",
            # --- Archetype Grid (v1.2) ---
            "archetype_key", "archetype_name",
        ])
        for rec in all_personas:
            ocean = rec.get("ocean", {})
            erikson = rec.get("erikson_stage", {})
            wound = rec.get("formative_wound", "")
            writer.writerow([
                rec["label"],
                rec["diagnosis_key"],
                rec["seed"],
                ocean.get("O", ""),
                ocean.get("C", ""),
                ocean.get("E", ""),
                ocean.get("A", ""),
                ocean.get("N", ""),
                rec.get("gender", ""),
                rec.get("age", ""),
                rec.get("education", ""),
                rec.get("locale", ""),
                rec.get("marital_status", ""),
                rec.get("occupation", ""),
                rec.get("core_desire", ""),
                rec.get("core_fear", ""),
                wound[:30] if wound else "",
                rec.get("arc_type", ""),
                erikson.get("stage", ""),
                len(rec.get("life_events", [])),
                rec.get("archetype_key", ""),
                rec.get("archetype_name", ""),
            ])

    print(f"  CSV: {csv_path}")
    print()

    return json_path, csv_path


# ====================================================================
# 入口
# ====================================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="批量生成 Persona 数据集")
    parser.add_argument("--diagnoses", type=str, default=None,
                        help="逗号分隔的诊断键，如 depressive,adhd,anorexia；默认全部诊断")
    parser.add_argument("--samples-per-diagnosis", "--count", dest="per_diagnosis",
                        type=int, default=None,
                        help=f"每个诊断生成的数量（默认 {PER_DIAGNOSIS}）")
    parser.add_argument("--output", type=str, default=None,
                        help="JSON 输出路径（默认 dataset/persona_dataset_v1.json）")
    parser.add_argument("--csv-output", type=str, default=None,
                        help="CSV 摘要输出路径（默认 dataset/persona_dataset_v1_summary.csv）")
    args = parser.parse_args()

    _diagnoses = [d.strip() for d in args.diagnoses.split(",")] if args.diagnoses else None

    print()
    print("🚀 大规模 Persona 数据集生成开始")
    print()

    personas, errors, elapsed = generate_dataset(
        diagnoses=_diagnoses, per_diagnosis=args.per_diagnosis,
    )
    json_path, csv_path = save_dataset(
        personas, errors, elapsed,
        json_path=args.output, csv_path=args.csv_output,
    )

    print("✅ 完成!")
    print(f"   数据集: {json_path}")
    print(f"   摘要:   {csv_path}")

    # 快速质量检查
    print()
    print("=" * 60)
    print("  快速质量检查")
    print("=" * 60)

    # 1. 检查是否有空值字段
    null_fields = {}
    for rec in personas:
        for field in PERSONA_FIELDS:
            if field == "life_events":
                continue  # 已序列化为 list
            val = rec.get(field)
            if val is None:
                null_fields[field] = null_fields.get(field, 0) + 1
    if null_fields:
        print(f"⚠️  有空值的字段:")
        for fld, cnt in sorted(null_fields.items()):
            print(f"     {fld}: {cnt}/{len(personas)}")
    else:
        print(f"✅ 所有字段非空")

    # 2. OCEAN 分布
    o_values = {d: [] for d in "OCEAN"}
    for rec in personas:
        ocean = rec.get("ocean", {})
        for k, v in ocean.items():
            if k.upper() in o_values and isinstance(v, (int, float)):
                o_values[k.upper()].append(v)
    for dim, vals in o_values.items():
        if vals:
            avg = sum(vals) / len(vals)
            print(f"   OCEAN-{dim}: avg={avg:.2f}, n={len(vals)}")

    # 3. 弧线类型分布
    arc_counts = {}
    for rec in personas:
        arc = rec.get("arc_type", "unknown")
        arc_counts[arc] = arc_counts.get(arc, 0) + 1
    print(f"   弧线类型: {dict(sorted(arc_counts.items()))}")

    # 4. 年龄分布
    ages = [rec.get("age") for rec in personas if rec.get("age")]
    if ages:
        print(f"   年龄: min={min(ages)}, max={max(ages)}, avg={sum(ages)/len(ages):.1f}")

    print()
