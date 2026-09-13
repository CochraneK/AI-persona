#!/usr/bin/env python3
"""
Generate diagnosis_ontology.json — ICD-11 Chapter 06 + DSM-5-TR
Part 1: ICD-11 blocks (1-5: Neurodevelopmental through OCD)
"""
import json, os, sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(SCRIPT_DIR, "_build")
os.makedirs(BUILD_DIR, exist_ok=True)

ICD11_SCHEMA = {
  "id": "06",
  "name": "Mental, Behavioural or Neurodevelopmental Disorders",
  "name_zh": "精神、行为或神经发育障碍",
  "description": "Syndromes characterised by clinically significant disturbance in cognition, emotional regulation, or behaviour reflecting dysfunction in psychological, biological, or developmental processes underlying mental and behavioural functioning.",
  "description_zh": "以个体认知、情绪调节或行为的临床显著紊乱为特征，反映心理、生物或发育过程功能障碍的综合征。",
  "code_range": "6A00-6E8Z",
  "exclusions": ["Acute stress reaction (QE84)", "Uncomplicated bereavement (QE62)"],
  "coded_elsewhere": ["Sleep-wake disorders (Ch.7)", "Sexual dysfunctions (HA00-HA0Z)", "Gender incongruence (HA60-HA6Z)"]
}

ICD11_BLOCKS = []

def B(block_id, name_en, name_zh, code_range, children, description_en="", description_zh=""):
    ICD11_BLOCKS.append({
        "id": block_id,
        "name": name_en,
        "name_zh": name_zh,
        "description": description_en,
        "description_zh": description_zh,
        "code_range": code_range,
        "disorders": children
    })

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

# ====== Block 1: Neurodevelopmental disorders ======
B("L1-6A0", "Neurodevelopmental disorders", "神经发育障碍", "6A00-6A0Z", [
  D("6A00", "Disorders of intellectual development", "智力发育障碍",
    subtypes=[{"code":"6A00.0","name":"Mild","name_zh":"轻度","description":"IQ ~50-69, approx 2-3 SD below mean"},
              {"code":"6A00.1","name":"Moderate","name_zh":"中度","description":"IQ ~35-49, approx 3-4 SD below mean"},
              {"code":"6A00.2","name":"Severe","name_zh":"重度","description":"IQ ~20-34"},
              {"code":"6A00.3","name":"Profound","name_zh":"极重度","description":"IQ <20"},
              {"code":"6A00.4","name":"Provisional","name_zh":"暂时的"},
              {"code":"6A00.Z","name":"Unspecified","name_zh":"未特指的"}],
    typical_age=[0,18], gender_ratio="M>F",
    severity_dimensions=["Intellectual functioning","Adaptive behavior","Social skills","Practical skills"],
    relevant_scales=["Wechsler Intelligence Scales","Vineland Adaptive Behavior Scales"]),

  D("6A01", "Developmental speech or language disorders", "发育性言语或语言障碍",
    subtypes=[{"code":"6A01.0","name":"Developmental speech sound disorder","name_zh":"发育性语音障碍"},
              {"code":"6A01.1","name":"Developmental speech fluency disorder","name_zh":"发育性言语流畅障碍（口吃）"},
              {"code":"6A01.20","name":"Developmental language disorder with receptive and expressive impairment","name_zh":"发育性语言障碍伴感受性和表达性语言受损"},
              {"code":"6A01.21","name":"Developmental language disorder mainly with expressive impairment","name_zh":"发育性语言障碍主要伴表达性语言受损"},
              {"code":"6A01.22","name":"Developmental language disorder mainly with pragmatic impairment","name_zh":"发育性语言障碍主要伴语用语言受损"}],
    typical_age=[2,7], gender_ratio="M>F"),

  D("6A02", "Autism spectrum disorder", "孤独症谱系障碍",
    subtypes=[{"code":"6A02.0","name":"Without intellectual disability, with mild/no language impairment","name_zh":"不伴智力发育障碍，伴轻度或不伴功能性语言受损"},
              {"code":"6A02.1","name":"With intellectual disability, with mild/no language impairment","name_zh":"伴智力发育障碍，伴轻度或不伴功能性语言损害"},
              {"code":"6A02.2","name":"Without intellectual disability, with functional language impairment","name_zh":"不伴智力发育障碍，伴功能性语言损害"},
              {"code":"6A02.3","name":"With intellectual disability, with functional language impairment","name_zh":"伴智力发育障碍，伴功能性语言损害"},
              {"code":"6A02.4","name":"Without intellectual disability, with absence of functional language","name_zh":"不伴智力发育障碍，伴功能性语言缺失"},
              {"code":"6A02.5","name":"With intellectual disability, with absence of functional language","name_zh":"伴智力发育障碍，伴功能性语言缺失"}],
    typical_age=[2,5], gender_ratio="M>F(4:1)",
    common_comorbidities=[{"disorder":"ADHD","rate":0.30},{"disorder":"Intellectual disability","rate":0.50},{"disorder":"Anxiety","rate":0.40}],
    relevant_scales=["ADOS-2","ADI-R","SCQ","SRS-2"]),

  D("6A03", "Developmental learning disorder", "发育性学习障碍",
    subtypes=[{"code":"6A03.0","name":"With impairment in reading","name_zh":"伴阅读受损（阅读障碍）"},
              {"code":"6A03.1","name":"With impairment in written expression","name_zh":"伴书面表达受损"},
              {"code":"6A03.2","name":"With impairment in mathematics","name_zh":"伴数学受损（计算障碍）"}],
    typical_age=[6,12], gender_ratio="M>F",
    relevant_scales=["WRAT-5","Woodcock-Johnson"]),

  D("6A04", "Developmental motor coordination disorder", "发育性运动共济障碍", typical_age=[3,10], gender_ratio="M>F"),
  D("6A05", "Attention deficit hyperactivity disorder", "注意缺陷多动障碍",
    subtypes=[{"code":"6A05.0","name":"Predominantly inattentive","name_zh":"主要表现为注意力不集中"},
              {"code":"6A05.1","name":"Predominantly hyperactive-impulsive","name_zh":"主要表现为多动-冲动"},
              {"code":"6A05.2","name":"Combined presentation","name_zh":"联合表现"}],
    typical_age=[3,12], gender_ratio="M>F(2:1 in children; ~1:1 in adults)",
    common_comorbidities=[{"disorder":"Anxiety","rate":0.25},{"disorder":"Depression","rate":0.20},{"disorder":"ASD","rate":0.15}],
    relevant_scales=["ASRS","Conners-3","SNAP-IV","Vanderbilt"]),

  D("6A06", "Stereotyped movement disorder", "刻板性运动障碍",
    subtypes=[{"code":"6A06.0","name":"Without self-injurious behaviour","name_zh":"不伴自伤"},
              {"code":"6A06.1","name":"With self-injurious behaviour","name_zh":"伴自伤"}],
    typical_age=[2,10]),
  D("6A0Y", "Other specified neurodevelopmental disorders", "其他特指的神经发育障碍"),
  D("6A0Z", "Neurodevelopmental disorders, unspecified", "神经发育障碍，未特指的"),
], description_en="Behavioural and cognitive disorders arising during developmental period involving significant difficulties in acquisition and execution of intellectual, motor, or social functions.")

# ====== Block 2: Schizophrenia or other primary psychotic disorders ======
B("L1-6A2", "Schizophrenia or other primary psychotic disorders", "精神分裂症或其他原发性精神病性障碍", "6A20-6A2Z", [
  D("6A20", "Schizophrenia", "精神分裂症",
    subtypes=[{"code":"6A20.0","name":"First episode","name_zh":"首次发作","description":"subtyped: currently symptomatic / partial remission / full remission"},
              {"code":"6A20.1","name":"Multiple episodes","name_zh":"多次发作"},
              {"code":"6A20.2","name":"Continuous","name_zh":"连续病程"}],
    typical_age=[18,35], gender_ratio="M=F",
    common_comorbidities=[{"disorder":"Substance use","rate":0.40},{"disorder":"Depression","rate":0.30},{"disorder":"Anxiety","rate":0.25}],
    severity_dimensions=["Positive symptoms","Negative symptoms","Cognitive impairment","Functional impairment"],
    relevant_scales=["PANSS","SANS","SAPS","PSP","BCIS"]),

  D("6A21", "Schizoaffective disorder", "分裂情感性障碍",
    subtypes=[{"code":"6A21.0","name":"First episode","name_zh":"首次发作"},
              {"code":"6A21.1","name":"Multiple episodes","name_zh":"多次发作"},
              {"code":"6A21.2","name":"Continuous","name_zh":"连续病程"}],
    typical_age=[18,30], gender_ratio="F>M",
    relevant_scales=["PANSS","YMRS","HDRS"]),

  D("6A22", "Schizotypal disorder", "分裂型障碍",
    typical_age=[18,30], gender_ratio="M>F",
    relevant_scales=["SPQ-B","SPQ","PAS"]),

  D("6A23", "Acute and transient psychotic disorder", "急性短暂性精神病性障碍",
    subtypes=[{"code":"6A23.0","name":"First episode","name_zh":"首次发作"},
              {"code":"6A23.1","name":"Multiple episodes","name_zh":"多次发作"}],
    typical_age=[20,40], gender_ratio="F>M"),

  D("6A24", "Delusional disorder", "妄想性障碍",
    subtypes=[{"code":"6A24.0","name":"Currently symptomatic","name_zh":"目前为症状性"},
              {"code":"6A24.1","name":"In partial remission","name_zh":"目前为部分缓解"},
              {"code":"6A24.2","name":"In full remission","name_zh":"目前为完全缓解"}],
    typical_age=[30,50], gender_ratio="M=F"),
  D("6A25", "Symptomatic manifestations of primary psychotic disorders", "原发性精神病性障碍的症状表现",
    subtypes=[{"code":"6A25.0","name":"Positive symptoms","name_zh":"阳性症状"},
              {"code":"6A25.1","name":"Negative symptoms","name_zh":"阴性症状"},
              {"code":"6A25.2","name":"Depressive symptoms","name_zh":"抑郁症状"},
              {"code":"6A25.3","name":"Manic symptoms","name_zh":"躁狂症状"},
              {"code":"6A25.4","name":"Psychomotor symptoms","name_zh":"精神运动性症状"},
              {"code":"6A25.5","name":"Cognitive symptoms","name_zh":"认知症状"}]),
  D("6A2Y", "Other specified primary psychotic disorders", "其他特指的精神分裂症或其他原发性精神病性障碍"),
  D("6A2Z", "Primary psychotic disorders, unspecified", "精神分裂症或其他原发性精神病性障碍,未特指的"),
], description_en="Characterized by disturbances in thinking, perception, emotions, and behaviour, with reality testing impairment and delusions/hallucinations.")

# ====== Block 3: Catatonia ======
B("L1-6A4", "Catatonia", "紧张症", "6A40-6A4Z", [
  D("6A40", "Catatonia associated with another mental disorder", "与其他精神障碍有关的紧张症",
    common_comorbidities=[{"disorder":"Schizophrenia","rate":0.10},{"disorder":"Mood disorders","rate":0.15},{"disorder":"ASD","rate":0.05}]),
  D("6A41", "Catatonia induced by substances or medications", "精神活性物质(包括治疗药物)所致紧张症"),
  D("6A4Z", "Catatonia, unspecified", "紧张症,未特指的"),
], description_en="Psychomotor syndrome characterized by marked disturbances in activity, posture, speech, and responsiveness.")

# ====== Block 4: Mood disorders ======
B("L1-6A6", "Mood disorders", "心境障碍", "6A60-6A8Z", [
  # Bipolar sub-block
  {"id":"L2-6A6","name":"Bipolar or related disorders","name_zh":"双相及相关障碍","code_range":"6A60-6A6Z","disorders":[
    D("6A60", "Bipolar type I disorder", "双相障碍I型",
      subtypes=[{"code":"6A60.0","name":"Current manic with no psychotic symptoms","name_zh":"目前为不伴精神病性症状的躁狂发作"},
                {"code":"6A60.1","name":"Current manic with psychotic symptoms","name_zh":"目前为伴精神病性症状的躁狂发作"},
                {"code":"6A60.2","name":"Current hypomanic","name_zh":"目前为轻躁狂发作"},
                {"code":"6A60.3","name":"Current mild depression","name_zh":"目前为轻度抑郁发作"},
                {"code":"6A60.6","name":"Current severe depression without psychotic","name_zh":"目前为不伴精神病性症状的重度抑郁发作"},
                {"code":"6A60.7","name":"Current severe depression with psychotic","name_zh":"目前为伴精神病性症状的重度抑郁发作"},
                {"code":"6A60.9","name":"Current mixed","name_zh":"目前为混合性发作"},
                {"code":"6A60.F","name":"In full remission","name_zh":"目前为完全缓解"}],
      typical_age=[15,30], gender_ratio="M=F",
      common_comorbidities=[{"disorder":"Anxiety","rate":0.60},{"disorder":"Substance use","rate":0.40},{"disorder":"ADHD","rate":0.15}],
      relevant_scales=["YMRS","MDQ","HCL-32","BDI"]),

    D("6A61", "Bipolar type II disorder", "双相障碍Ⅱ型",
      subtypes=[{"code":"6A61.0","name":"Current hypomanic","name_zh":"目前为轻躁狂发作"},
                {"code":"6A61.1","name":"Current mild depression","name_zh":"目前为轻度抑郁发作"},
                {"code":"6A61.4","name":"Current severe depression","name_zh":"目前为重度抑郁发作"},
                {"code":"6A61.A","name":"In full remission","name_zh":"目前为完全缓解"}],
      typical_age=[15,30], gender_ratio="F>M",
      relevant_scales=["YMRS","MDQ","HCL-32"]),

    D("6A62", "Cyclothymic disorder", "环性心境障碍",
      typical_age=[15,25], gender_ratio="M=F",
      common_comorbidities=[{"disorder":"Bipolar I/II","rate":0.25}]),
    D("6A6Y", "Other specified bipolar or related disorders", "其他特指的双相及相关障碍"),
    D("6A6Z", "Bipolar or related disorders, unspecified", "双相及相关障碍,未特指的"),
  ]},
  # Depressive sub-block
  {"id":"L2-6A7","name":"Depressive disorders","name_zh":"抑郁障碍","code_range":"6A70-6A7Z","disorders":[
    D("6A70", "Single episode depressive disorder", "单次发作的抑郁障碍",
      subtypes=[{"code":"6A70.0","name":"Mild","name_zh":"轻度"},
                {"code":"6A70.1","name":"Moderate without psychotic","name_zh":"中度,不伴精神病性症状"},
                {"code":"6A70.2","name":"Moderate with psychotic","name_zh":"中度,伴精神病性症状"},
                {"code":"6A70.3","name":"Severe without psychotic","name_zh":"重度,不伴精神病性症状"},
                {"code":"6A70.4","name":"Severe with psychotic","name_zh":"重度,伴精神病性症状"}],
      typical_age=[20,40], gender_ratio="F>M(2:1)",
      common_comorbidities=[{"disorder":"Anxiety","rate":0.50},{"disorder":"Substance use","rate":0.20}],
      severity_dimensions=["Mood","Anhedonia","Energy","Sleep","Appetite","Concentration","Psychomotor"],
      relevant_scales=["PHQ-9","BDI-II","HDRS","QIDS-SR"]),

    D("6A71", "Recurrent depressive disorder", "复发性抑郁障碍",
      subtypes=[{"code":"6A71.0","name":"Current mild","name_zh":"目前为轻度发作"},
                {"code":"6A71.1","name":"Current moderate","name_zh":"目前为中度发作"},
                {"code":"6A71.3","name":"Current severe","name_zh":"目前为重度发作"},
                {"code":"6A71.6","name":"In partial remission","name_zh":"目前为部分缓解"},
                {"code":"6A71.7","name":"In full remission","name_zh":"目前为完全缓解"}],
      typical_age=[20,40], gender_ratio="F>M",
      common_comorbidities=[{"disorder":"Anxiety","rate":0.50},{"disorder":"Substance use","rate":0.20}],
      relevant_scales=["PHQ-9","BDI-II","HDRS"]),

    D("6A72", "Dysthymic disorder", "恶劣心境障碍",
      typical_age=[20,30], gender_ratio="F>M",
      common_comorbidities=[{"disorder":"Major depression","rate":0.40},{"disorder":"Anxiety","rate":0.50}],
      relevant_scales=["PHQ-9","BDI-II"]),

    D("6A73", "Mixed depressive and anxiety disorder", "混合性抑郁焦虑障碍",
      typical_age=[20,40], gender_ratio="F>M",
      relevant_scales=["HADS","PHQ-9","GAD-7"]),
    D("6A7Y", "Other specified depressive disorders", "其他特指的抑郁障碍"),
    D("6A7Z", "Depressive disorders, unspecified", "抑郁障碍,未特指的"),
  ]},
  D("6A80", "Symptomatic and course manifestations of mood disorders", "心境障碍中发作的症状和病程表现",
    subtypes=[{"code":"6A80.0","name":"Prominent anxiety","name_zh":"突出的焦虑症状"},
              {"code":"6A80.1","name":"Panic attacks","name_zh":"惊恐发作"},
              {"code":"6A80.2","name":"Current persistent depression","name_zh":"目前抑郁发作持续"},
              {"code":"6A80.3","name":"Melancholic features","name_zh":"伴忧郁特征"},
              {"code":"6A80.4","name":"Seasonal pattern","name_zh":"季节特征"},
              {"code":"6A80.5","name":"Rapid cycling","name_zh":"快速循环"}]),
  D("6A8Y", "Other specified mood disorders", "其他特指的心境障碍"),
  D("6A8Z", "Mood disorders, unspecified", "心境障碍,未特指的"),
], description_en="Disorders characterized by disturbances in mood or affect, either depressive (sadness/hopelessness) or manic (elation/irritability).",
  description_zh="以情绪或情感的紊乱为特征的障碍，抑郁（悲伤/无望）或躁狂（兴奋/易怒）。")

# ====== Block 5: Anxiety or fear-related disorders ======
B("L1-6B0", "Anxiety or fear-related disorders", "焦虑或恐惧相关性障碍", "6B00-6B0Z", [
  D("6B00", "Generalized anxiety disorder", "广泛性焦虑障碍",
    description_en="Excessive anxiety and worry about multiple events/activities, most days for at least several months.",
    description_zh="对多种事件或活动的过度焦虑和担忧，持续至少数月。",
    typical_age=[20,40], gender_ratio="F>M(2:1)",
    common_comorbidities=[{"disorder":"Depression","rate":0.60},{"disorder":"Other anxiety","rate":0.50}],
    relevant_scales=["GAD-7","BAI","HADS-A"]),

  D("6B01", "Panic disorder", "惊恐障碍",
    description_en="Recurrent unexpected panic attacks with fear of future attacks.",
    description_zh="反复的意外惊恐发作，伴对未来发作的恐惧。",
    typical_age=[20,30], gender_ratio="F>M(2:1)",
    relevant_scales=["PDSS","ASI"]),

  D("6B02", "Agoraphobia", "广场恐怖",
    description_en="Fear of situations where escape might be difficult or help unavailable.",
    description_zh="对难以逃离或无法获得帮助的场合的恐惧。",
    typical_age=[20,30], gender_ratio="F>M"),

  D("6B03", "Specific phobia", "特定的恐怖",
    description_en="Intense fear of a specific object or situation (e.g., animals, heights, blood).",
    description_zh="对特定物体或情境（如动物、高处、血液）的强烈恐惧。",
    typical_age=[5,20], gender_ratio="F>M(2:1)"),

  D("6B04", "Social anxiety disorder", "社交性焦虑障碍",
    description_en="Marked fear of social situations involving potential scrutiny by others.",
    description_zh="对可能被他人审视的社交场合的显著恐惧。",
    typical_age=[10,20], gender_ratio="M=F",
    relevant_scales=["SIAS","SPIN","LSAS"]),

  D("6B05", "Separation anxiety disorder", "分离性焦虑障碍",
    description_en="Developmentally inappropriate fear of separation from attachment figures.",
    description_zh="与依恋对象分离时出现与发育水平不相称的恐惧。",
    typical_age=[3,10], gender_ratio="M=F"),

  D("6B06", "Selective mutism", "选择性缄默症",
    description_en="Consistent failure to speak in specific social situations despite speaking in others.",
    description_zh="在特定社交场合持续不说话，尽管在其他场合能说话。",
    typical_age=[3,8], gender_ratio="M=F"),
  D("6B0Y", "Other specified anxiety or fear-related disorders", "其他特指的焦虑或恐惧相关性障碍"),
  D("6B0Z", "Anxiety or fear-related disorders, unspecified", "焦虑或恐惧相关性障碍,未特指的"),
], description_en="Disorders characterized by excessive fear, anxiety, and avoidance behaviours.",
  description_zh="以过度的恐惧、焦虑和回避行为为特征的障碍。")

# ====== Block 6: Obsessive-compulsive or related disorders ======
B("L1-6B2", "Obsessive-compulsive or related disorders", "强迫性或相关障碍", "6B20-6B2Z", [
  D("6B20", "Obsessive-compulsive disorder", "强迫性障碍",
    subtypes=[{"code":"6B20.0","name":"With good or fair insight","name_zh":"伴一般或良好自知力"},
              {"code":"6B20.1","name":"With poor or absent insight","name_zh":"伴较差自知力或缺乏自知力"}],
    typical_age=[10,25], gender_ratio="M=F",
    common_comorbidities=[{"disorder":"Anxiety","rate":0.60},{"disorder":"Depression","rate":0.40},{"disorder":"Tic disorders","rate":0.20}],
    relevant_scales=["Y-BOCS","OCI-R","MOCI"]),

  D("6B21", "Body dysmorphic disorder", "躯体变形障碍",
    subtypes=[{"code":"6B21.0","name":"With good or fair insight","name_zh":"伴一般或良好自知力"},
              {"code":"6B21.1","name":"With poor or absent insight","name_zh":"伴较差自知力或缺乏自知力"}],
    typical_age=[15,30], gender_ratio="M=F",
    relevant_scales=["BDD-YBOCS"]),

  D("6B22", "Olfactory reference disorder", "嗅觉牵连障碍",
    subtypes=[{"code":"6B22.0","name":"With good or fair insight","name_zh":"伴一般或良好自知力"},
              {"code":"6B22.1","name":"With poor or absent insight","name_zh":"伴较差或缺乏自知力"}]),

  D("6B23", "Hypochondriasis", "疑病症",
    subtypes=[{"code":"6B23.0","name":"With good or fair insight","name_zh":"伴一般或良好自知力"},
              {"code":"6B23.1","name":"With poor or absent insight","name_zh":"伴较差自知力或缺乏自知力"}],
    common_comorbidities=[{"disorder":"Anxiety","rate":0.50},{"disorder":"Depression","rate":0.30}],
    relevant_scales=["SHAI","WI"]),

  D("6B24", "Hoarding disorder", "囤积障碍",
    subtypes=[{"code":"6B24.0","name":"With good or fair insight","name_zh":"伴一般或良好自知力"},
              {"code":"6B24.1","name":"With poor or absent insight","name_zh":"伴较差或缺乏自知力"}],
    typical_age=[20,40], gender_ratio="M=F",
    common_comorbidities=[{"disorder":"Depression","rate":0.40},{"disorder":"Anxiety","rate":0.30}]),

  D("6B25", "Body-focused repetitive behaviour disorders", "聚焦于躯体的重复行为障碍",
    subtypes=[{"code":"6B25.0","name":"Trichotillomania","name_zh":"拔毛癖"},
              {"code":"6B25.1","name":"Excoriation disorder","name_zh":"抓痕障碍"}],
    typical_age=[10,20], gender_ratio="F>M",
    relevant_scales=["MGH-HPS","NIMH-TSS"]),
  D("6B2Y", "Other specified OCRDs", "其他特指的强迫性或相关障碍"),
  D("6B2Z", "OCRD, unspecified", "强迫性或相关障碍,未特指的"),
])

# ====== Block 7: Disorders specifically associated with stress ======
B("L1-6B4", "Disorders specifically associated with stress", "应激相关障碍", "6B40-6B4Z", [
  D("6B40", "Post-traumatic stress disorder", "创伤后应激障碍",
    description_en="Develops following exposure to an extremely threatening or horrific event; characterized by re-experiencing, avoidance, hyperarousal.",
    description_zh="在经历极端威胁或恐怖事件后发展；以再体验、回避、过度警觉为特征。",
    typical_age=[20,40], gender_ratio="F>M",
    common_comorbidities=[{"disorder":"Depression","rate":0.50},{"disorder":"Substance use","rate":0.30},{"disorder":"Anxiety","rate":0.50}],
    relevant_scales=["PCL-5","CAPS-5","IES-R","C-SSRS"]),

  D("6B41", "Complex post-traumatic stress disorder", "复杂性创伤后应激障碍",
    description_en="Develops after sustained/repeated trauma; includes PTSD symptoms + disturbances in self-organization (affect dysregulation, negative self-concept, interpersonal difficulties).",
    description_zh="在持续/重复的创伤后发展；除PTSD症状外，还有自我组织障碍（情感调节障碍、消极自我概念、人际关系困难）。",
    typical_age=[20,40], gender_ratio="F>M",
    relevant_scales=["ITQ"]),

  D("6B42", "Prolonged grief disorder", "延长哀伤障碍",
    description_en="Persistent and pervasive grief response lasting >6 months after bereavement.",
    description_zh="在丧亲后持续>6个月的弥漫性哀伤反应。",
    relevant_scales=["PG-13","ICG"]),

  D("6B43", "Adjustment disorder", "适应障碍",
    description_en="Emotional/behavioural symptoms in response to an identifiable psychosocial stressor.",
    description_zh="对可识别的心理社会应激源的适应性情绪/行为反应。",
    typical_age=[20,40], gender_ratio="M=F"),

  D("6B44", "Reactive attachment disorder", "反应性依恋障碍",
    description_en="Severely disturbed attachment behaviour in young children due to social neglect.",
    description_zh="因社会忽视导致的幼儿严重依恋行为紊乱。",
    typical_age=[1,5], gender_ratio="M=F"),

  D("6B45", "Disinhibited social engagement disorder", "脱抑制性社会参与障碍",
    description_en="Indiscriminate social approach in young children due to social neglect.",
    description_zh="因社会忽视导致的幼儿不加区别的社交行为。",
    typical_age=[1,5], gender_ratio="M=F"),
  D("6B4Y", "Other specified stress-related disorders", "其他特指的应激相关障碍"),
  D("6B4Z", "Stress-related disorders, unspecified", "应激相关障碍,未特指的"),
])

# Save part 1
os.makedirs(BUILD_DIR, exist_ok=True)
with open(os.path.join(BUILD_DIR, "icd11_part1.json"), "w", encoding="utf-8") as f:
    json.dump({"schema": ICD11_SCHEMA, "blocks": ICD11_BLOCKS}, f, ensure_ascii=False, indent=2)
print(f"Part 1 saved: {len(ICD11_BLOCKS)} blocks")
