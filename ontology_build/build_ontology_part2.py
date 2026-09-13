#!/usr/bin/env python3
"""
Part 2: ICD-11 blocks 8-14 (Dissociative through Disruptive behaviour)
"""
import json, os, sys

BUILD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_build")
sys.path.insert(0, os.path.dirname(__file__))

def D(code, name_en, name_zh, subtypes=None, common_comorbidities=None,
      typical_age=None, gender_ratio=None, relevant_scales=None,
      severity_dimensions=None, description_en="", description_zh=""):
    d = {"code": code, "name": name_en, "name_zh": name_zh,
         "description": description_en, "description_zh": description_zh}
    if subtypes: d["subtypes"] = subtypes
    if common_comorbidities: d["common_comorbidities"] = common_comorbidities
    if typical_age: d["typical_age_of_onset"] = typical_age
    if gender_ratio: d["gender_ratio"] = gender_ratio
    if relevant_scales: d["relevant_scales"] = relevant_scales
    if severity_dimensions: d["severity_dimensions"] = severity_dimensions
    return d

ICD11_BLOCKS = []

def B(block_id, name_en, name_zh, code_range, children, description_en="", description_zh=""):
    ICD11_BLOCKS.append({
        "id": block_id, "name": name_en, "name_zh": name_zh,
        "description": description_en, "description_zh": description_zh,
        "code_range": code_range, "disorders": children
    })

# ====== Block 8: Dissociative disorders ======
B("L1-6B6", "Dissociative disorders", "分离障碍", "6B60-6B6Z", [
  D("6B60", "Dissociative neurological symptom disorder", "分离性神经症状障碍",
    subtypes=[{"code":"6B60.0","name":"With visual symptoms","name_zh":"伴视觉症状"},
              {"code":"6B60.1","name":"With auditory symptoms","name_zh":"伴听觉症状"},
              {"code":"6B60.2","name":"With vertigo","name_zh":"伴眩晕"},
              {"code":"6B60.3","name":"With sensory changes","name_zh":"伴感觉改变"},
              {"code":"6B60.4","name":"With non-epileptic seizures","name_zh":"不伴抽搐或痉挛"},
              {"code":"6B60.5","name":"With speech disturbance","name_zh":"伴言语生成症状"},
              {"code":"6B60.6","name":"With paresis or weakness","name_zh":"伴无力或麻痹"},
              {"code":"6B60.7","name":"With gait disturbance","name_zh":"伴步态症状"},
              {"code":"6B60.8","name":"With movement disturbance","name_zh":"伴运动症状"}],
    typical_age=[15,35], gender_ratio="F>M"),
  D("6B61", "Dissociative amnesia", "分离遗忘症",
    subtypes=[{"code":"6B61.0","name":"With dissociative fugue","name_zh":"伴分离性漫游"},
              {"code":"6B61.1","name":"Without dissociative fugue","name_zh":"不伴分离性漫游"}],
    typical_age=[20,40], gender_ratio="F>M"),
  D("6B62", "Trance disorder", "出神障碍"),
  D("6B63", "Possession trance disorder", "附体出神障碍"),
  D("6B64", "Dissociative identity disorder", "分离性身份障碍",
    description_en="Disruption of identity with two or more distinct personality states.",
    description_zh="身份瓦解，存在两个或更多不同的人格状态。",
    typical_age=[20,30], gender_ratio="F>M",
    relevant_scales=["SCID-D","DES"]),
  D("6B65", "Partial dissociative identity disorder", "部分分离性身份障碍",
    typical_age=[20,30], gender_ratio="F>M"),
  D("6B66", "Depersonalization-derealization disorder", "人格解体-现实解体障碍",
    typical_age=[16,25], gender_ratio="M=F"),
  D("6B6Y", "Other specified dissociative disorders", "其他特指的分离障碍"),
  D("6B6Z", "Dissociative disorders, unspecified", "分离障碍,未特指的"),
])

# ====== Block 9: Feeding or eating disorders ======
B("L1-6B8", "Feeding or eating disorders", "喂食或进食障碍", "6B80-6B8Z", [
  D("6B80", "Anorexia nervosa", "神经性厌食",
    subtypes=[{"code":"6B80.0","name":"With significantly low body weight","name_zh":"伴显著的低体重",
               "sub":[
                 {"code":"6B80.00","name":"Restricting type","name_zh":"限制型"},
                 {"code":"6B80.01","name":"Binge-purge type","name_zh":"暴食-清除型"}]},
              {"code":"6B80.1","name":"With dangerously low body weight","name_zh":"伴危险的低体重"},
              {"code":"6B80.2","name":"In recovery with normal body weight","name_zh":"恢复期伴正常体重"}],
    typical_age=[14,25], gender_ratio="F>M(10:1)",
    common_comorbidities=[{"disorder":"Depression","rate":0.50},{"disorder":"Anxiety","rate":0.50},{"disorder":"OCD","rate":0.20}],
    severity_dimensions=["BMI","Restriction severity","Binge-purge frequency"],
    relevant_scales=["EDE-Q","EAT-26","SCOFF"]),
  D("6B81", "Bulimia nervosa", "神经性贪食",
    typical_age=[16,30], gender_ratio="F>M(10:1)",
    common_comorbidities=[{"disorder":"Depression","rate":0.50},{"disorder":"BPD","rate":0.25}],
    relevant_scales=["EDE-Q","BULIT-R"]),
  D("6B82", "Binge eating disorder", "暴食障碍",
    typical_age=[20,40], gender_ratio="F>M(1.5:1)",
    common_comorbidities=[{"disorder":"Obesity","rate":0.50},{"disorder":"Depression","rate":0.40}],
    relevant_scales=["BES","EDE-Q"]),
  D("6B83", "Avoidant-restrictive food intake disorder", "回避-限制性摄食障碍",
    typical_age=[3,20], gender_ratio="M=F"),
  D("6B84", "Pica", "异食癖", typical_age=[2,10], gender_ratio="M=F"),
  D("6B85", "Rumination-regurgitation disorder", "反刍-反流障碍", typical_age=[3,12], gender_ratio="M=F"),
  D("6B8Y", "Other specified feeding/eating disorders", "其他特指的喂食或进食障碍"),
  D("6B8Z", "Feeding/eating disorders, unspecified", "喂食或进食障碍,未特指的"),
])

# ====== Block 10: Elimination disorders ======
B("L1-6C0", "Elimination disorders", "排泄障碍", "6C00-6C0Z", [
  D("6C00", "Enuresis", "遗尿症",
    subtypes=[{"code":"6C00.0","name":"Nocturnal","name_zh":"夜间遗尿症"},
              {"code":"6C00.1","name":"Diurnal","name_zh":"日间遗尿症"},
              {"code":"6C00.2","name":"Nocturnal and diurnal","name_zh":"夜间和日间遗尿症"}],
    typical_age=[5,12], gender_ratio="M>F"),
  D("6C01", "Encopresis", "遗粪症",
    subtypes=[{"code":"6C01.0","name":"With constipation/overflow","name_zh":"伴便秘或溢出性失禁"},
              {"code":"6C01.1","name":"Without constipation","name_zh":"不伴便秘或溢出性失禁"}],
    typical_age=[5,12], gender_ratio="M>F"),
  D("6C0Z", "Elimination disorders, unspecified", "排泄障碍,未特指的"),
])

# ====== Block 11: Disorders of bodily distress or bodily experience ======
B("L1-6C2", "Disorders of bodily distress or bodily experience", "躯体不适或躯体体验障碍", "6C20-6C2Z", [
  D("6C20", "Bodily distress disorder", "躯体不适障碍",
    subtypes=[{"code":"6C20.0","name":"Mild","name_zh":"轻度"},
              {"code":"6C20.1","name":"Moderate","name_zh":"中度"},
              {"code":"6C20.2","name":"Severe","name_zh":"重度"}],
    typical_age=[20,50], gender_ratio="F>M",
    common_comorbidities=[{"disorder":"Anxiety","rate":0.40},{"disorder":"Depression","rate":0.40}],
    relevant_scales=["PHQ-15","SSS-8","WI"]),
  D("6C21", "Body integrity dysphoria", "身体一致性烦恼",
    description_en="Persistent desire to have a specific physical impairment (e.g., amputation).",
    description_zh="持续渴望拥有某种特定的身体残疾（如截肢）。"),
  D("6C2Y", "Other specified bodily distress disorders", "其他特指的躯体不适或躯体体验障碍"),
  D("6C2Z", "Bodily distress disorders, unspecified", "躯体不适或躯体体验障碍,未特指的"),
])

# ====== Block 12: Disorders due to substance use or addictive behaviours ======
SUBSTANCE_COMMON = ["Episode of harmful use","Harmful pattern","Dependence","Intoxication","Withdrawal","Substance-induced delirium","Substance-induced psychotic disorder","Substance-induced mood/anxiety disorder"]
SUBSTANCE_CODES = [
  ("6C40", "Alcohol", "酒精", 18, 40, "M>F"),
  ("6C41", "Cannabis", "大麻", 16, 30, "M>F"),
  ("6C42", "Synthetic cannabinoids", "合成大麻素", 18, 30, "M>F"),
  ("6C43", "Opioids", "阿片类", 20, 40, "M>F"),
  ("6C44", "Sedatives, hypnotics or anxiolytics", "镇静催眠或抗焦虑药", 20, 50, "F>M"),
  ("6C45", "Cocaine", "可卡因", 20, 40, "M>F"),
  ("6C46", "Stimulants (amphetamines, methamphetamine)", "兴奋剂（安非他明、甲基苯丙胺）", 18, 35, "M>F"),
  ("6C47", "Synthetic cathinones", "合成卡西酮", 18, 30, "M>F"),
  ("6C48", "Caffeine", "咖啡因", 20, 40, "M=F"),
  ("6C49", "Hallucinogens", "致幻剂", 18, 30, "M>F"),
  ("6C4A", "Nicotine", "尼古丁", 16, 30, "M=F"),
  ("6C4B", "Volatile inhalants", "挥发性吸入剂", 14, 25, "M>F"),
  ("6C4C", "MDMA or related drugs", "MDMA及相关药物", 18, 30, "M=F"),
  ("6C4D", "Dissociative drugs (ketamine, PCP)", "解离性药物（氯胺酮、PCP）", 18, 30, "M>F"),
  ("6C4E", "Other specified psychoactive substances", "其他特指的精神活性物质", 20, 40, "M=F"),
  ("6C4F", "Multiple specified psychoactive substances", "多种特指的精神活性物质", 20, 40, "M>F"),
  ("6C4G", "Unknown/unspecified psychoactive substances", "未知或未特指的精神活性物质", 20, 40, "M=F"),
  ("6C4H", "Non-psychoactive substances", "非精神活性物质", 20, 50, "M=F"),
]
substance_disorders = []
for code, name_en, name_zh, a_min, a_max, gr in SUBSTANCE_CODES:
    substance_disorders.append(D(code, f"Disorders due to use of {name_en}", f"{name_zh}使用所致障碍",
        typical_age=[a_min, a_max], gender_ratio=gr,
        severity_dimensions=["Use severity","Dependence","Intoxication/Withdrawal","Substance-induced mental disorders"],
        relevant_scales=["AUDIT" if "Alcohol" in name_en else "DAST-10","ASSIST","CAGE"],
        common_comorbidities=[{"disorder":"Depression","rate":0.30},{"disorder":"Anxiety","rate":0.25},{"disorder":"PTSD","rate":0.15}]))
substance_disorders.append(D("6C4Y", "Other specified substance use disorders", "其他特指的物质使用所致障碍"))
substance_disorders.append(D("6C4Z", "Substance use disorders, unspecified", "物质使用所致障碍,未特指的"))
addiction_disorders = [
  D("6C50", "Gambling disorder", "赌博障碍",
    subtypes=[{"code":"6C50.0","name":"Predominantly offline","name_zh":"线下为主"},
              {"code":"6C50.1","name":"Predominantly online","name_zh":"线上为主"}],
    typical_age=[20,40], gender_ratio="M>F",
    relevant_scales=["PGSI","SOGS"]),
  D("6C51", "Gaming disorder", "游戏障碍",
    subtypes=[{"code":"6C51.0","name":"Predominantly online","name_zh":"线上为主"},
              {"code":"6C51.1","name":"Predominantly offline","name_zh":"线下为主"}],
    typical_age=[12,30], gender_ratio="M>F",
    relevant_scales=["IGD-20","GAS"]),
  D("6C5Y", "Other specified addictive behaviour disorders", "其他特指的成瘾行为所致障碍"),
  D("6C5Z", "Addictive behaviour disorders, unspecified", "成瘾行为所致障碍,未特指的"),
]
B("L1-6C4", "Disorders due to substance use or addictive behaviours", "物质使用或成瘾行为所致障碍", "6C40-6C5Z",
  [{"id":"L2-6C4","name":"Disorders due to substance use","name_zh":"物质使用所致障碍","code_range":"6C40-6C4Z","disorders":substance_disorders},
   {"id":"L2-6C5","name":"Disorders due to addictive behaviours","name_zh":"成瘾行为所致障碍","code_range":"6C50-6C5Z","disorders":addiction_disorders}])

# ====== Block 13: Impulse control disorders ======
B("L1-6C7", "Impulse control disorders", "冲动控制障碍", "6C70-6C7Z", [
  D("6C70", "Pyromania", "纵火癖", typical_age=[10,25], gender_ratio="M>F"),
  D("6C71", "Kleptomania", "盗窃癖", typical_age=[15,30], gender_ratio="F>M"),
  D("6C72", "Compulsive sexual behaviour disorder", "强迫性性行为障碍",
    typical_age=[20,40], gender_ratio="M>F",
    relevant_scales=["CSBI","SAST-R"]),
  D("6C73", "Intermittent explosive disorder", "间歇性暴怒障碍",
    typical_age=[15,30], gender_ratio="M>F",
    common_comorbidities=[{"disorder":"Anxiety","rate":0.30},{"disorder":"Depression","rate":0.30},{"disorder":"Substance use","rate":0.40}],
    relevant_scales=["AIAQ-CF"]),
  D("6C7Y", "Other specified impulse control disorders", "其他特指的冲动控制障碍"),
  D("6C7Z", "Impulse control disorders, unspecified", "冲动控制障碍,未特指的"),
])

# ====== Block 14: Disruptive behaviour or dissocial disorders ======
B("L1-6C9", "Disruptive behaviour or dissocial disorders", "破坏行为或反社会障碍", "6C90-6C9Z", [
  D("6C90", "Oppositional defiant disorder", "对立违抗障碍",
    subtypes=[{"code":"6C90.0","name":"With chronic irritability-anger","name_zh":"伴慢性易怒-愤怒"},
              {"code":"6C90.1","name":"Without chronic irritability-anger","name_zh":"不伴慢性易怒-愤怒"}],
    typical_age=[8,16], gender_ratio="M>F",
    common_comorbidities=[{"disorder":"ADHD","rate":0.50},{"disorder":"Anxiety","rate":0.20}],
    relevant_scales=["CPRS","Conners-3"]),
  D("6C91", "Conduct-dissocial disorder", "品行-反社会障碍",
    subtypes=[{"code":"6C91.0","name":"Childhood onset","name_zh":"儿童期起病"},
              {"code":"6C91.1","name":"Adolescent onset","name_zh":"青少年期起病"}],
    typical_age=[8,16], gender_ratio="M>F",
    common_comorbidities=[{"disorder":"ADHD","rate":0.40},{"disorder":"Substance use","rate":0.30}],
    relevant_scales=["CPRS","ASPD criteria"]),
  D("6C9Y", "Other specified disruptive behaviour disorders", "其他特指的破坏行为或反社会障碍"),
  D("6C9Z", "Disruptive behaviour disorders, unspecified", "破坏行为或反社会障碍,未特指的"),
])

# Save
with open(os.path.join(BUILD_DIR, "icd11_part2.json"), "w", encoding="utf-8") as f:
    json.dump({"blocks": ICD11_BLOCKS}, f, ensure_ascii=False, indent=2)
print(f"Part 2 saved: {len(ICD11_BLOCKS)} blocks")
