#!/usr/bin/env python3
"""
Part 3: ICD-11 blocks 15-22 + DSM-5-TR chapters
"""
import json, os

BUILD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_build")

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

# ====== Block 15: Personality disorders and related traits ======
B("L1-6D1", "Personality disorders and related traits", "人格障碍及相关特质", "6D10-6D11.5", [
  D("6D10", "Personality disorder", "人格障碍",
    subtypes=[{"code":"6D10.0","name":"Mild","name_zh":"轻度"},
              {"code":"6D10.1","name":"Moderate","name_zh":"中度"},
              {"code":"6D10.2","name":"Severe","name_zh":"重度"},
              {"code":"6D10.Z","name":"Severity unspecified","name_zh":"严重度未特指"}],
    severity_dimensions=["Self-functioning","Interpersonal functioning","Emotional/behavioural problems","Risk of harm"],
    description_en="A marked disturbance in personality functioning, manifested in impairments in self-functioning (identity, self-worth, self-direction) and/or interpersonal functioning.",
    description_zh="人格功能的显著紊乱，表现在自我功能（身份、自我价值、自我导向）和/或人际功能方面的损害。"),
  D("6D11", "Prominent personality traits or patterns", "突出人格特质或模式",
    subtypes=[{"code":"6D11.0","name":"Negative affectivity","name_zh":"负性情绪倾向"},
              {"code":"6D11.1","name":"Detachment","name_zh":"疏离"},
              {"code":"6D11.2","name":"Dissociality","name_zh":"反社会性"},
              {"code":"6D11.3","name":"Disinhibition","name_zh":"去抑制"},
              {"code":"6D11.4","name":"Anankastia","name_zh":"强迫性"},
              {"code":"6D11.5","name":"Borderline pattern","name_zh":"边缘型模式"}],
    description_en="Trait domain specifiers that describe the characteristics of personality functioning. The borderline pattern corresponds closely to DSM-5 borderline PD.",
    description_zh="描述人格功能特征的特质领域限定词。边缘型模式与DSM-5边缘型人格障碍高度对应。"),
])

# ====== Block 16: Paraphilic disorders ======
B("L1-6D3", "Paraphilic disorders", "性偏好障碍", "6D30-6D3Z", [
  D("6D30", "Exhibitionistic disorder", "露阴障碍", gender_ratio="M>F"),
  D("6D31", "Voyeuristic disorder", "窥阴障碍", gender_ratio="M>F"),
  D("6D32", "Pedophilic disorder", "恋童障碍", gender_ratio="M>F"),
  D("6D33", "Coercive sexual sadism disorder", "强制性施虐障碍", gender_ratio="M>F"),
  D("6D34", "Frotteuristic disorder", "摩擦障碍", gender_ratio="M>F"),
  D("6D35", "Other paraphilic disorder involving non-consenting individuals", "其他涉及非自愿者的性偏好障碍"),
  D("6D36", "Paraphilic disorder involving solitary behaviour or consenting individuals", "涉及独处行为或自愿者的性偏好障碍"),
  D("6D3Z", "Paraphilic disorders, unspecified", "性偏好障碍,未特指的"),
])

# ====== Block 17: Factitious disorders ======
B("L1-6D5", "Factitious disorders", "做作性障碍", "6D50-6D5Z", [
  D("6D50", "Factitious disorder imposed on self", "自身做作性障碍（Munchausen综合征）",
    typical_age=[20,40], gender_ratio="F>M"),
  D("6D51", "Factitious disorder imposed on another", "他人做作性障碍（代理性Munchausen）",
    typical_age=[20,40], gender_ratio="F>M"),
  D("6D5Z", "Factitious disorders, unspecified", "做作性障碍,未特指的"),
])

# ====== Block 18: Neurocognitive disorders ======
B("L1-6D7", "Neurocognitive disorders", "神经认知障碍", "6D70-6E0Z", [
  D("6D70", "Delirium", "谵妄",
    subtypes=[{"code":"6D70.0","name":"Due to disease classified elsewhere","name_zh":"由于分类于他处的疾病"},
              {"code":"6D70.1","name":"Due to psychoactive substances/medications","name_zh":"由于精神活性物质（包括治疗药物）"},
              {"code":"6D70.2","name":"Due to multiple etiological factors","name_zh":"由于多种病因因素"}],
    typical_age=[65,90], gender_ratio="M=F",
    relevant_scales=["CAM","MDAS","DOS"]),
  D("6D71", "Mild neurocognitive disorder", "轻度神经认知障碍",
    typical_age=[60,90], gender_ratio="M=F",
    relevant_scales=["MoCA","MMSE","CDR"]),
  D("6D72", "Amnestic disorder", "遗忘障碍",
    typical_age=[50,80], gender_ratio="M=F"),
  # Dementia group
  D("6D80", "Dementia due to Alzheimer disease", "阿尔茨海默病性痴呆",
    typical_age=[65,90], gender_ratio="F>M",
    severity_dimensions=["Cognitive decline","Functional impairment","Behavioural disturbances"],
    relevant_scales=["NPI-Q","ADAS-Cog","CDR"]),
  D("6D81", "Dementia due to cerebrovascular disease", "脑血管病性痴呆（血管性痴呆）",
    typical_age=[60,85], gender_ratio="M>F",
    relevant_scales=["Hachinski","NINDS-AIREN"]),
  D("6D82", "Dementia with Lewy bodies", "路易体痴呆",
    typical_age=[60,85], gender_ratio="M>F"),
  D("6D83", "Frontotemporal dementia", "额颞叶痴呆",
    typical_age=[45,70], gender_ratio="M=F"),
  D("6D84", "Dementia due to psychoactive substances", "精神活性物质性痴呆",
    typical_age=[40,60], gender_ratio="M>F"),
  D("6D85", "Dementia due to diseases classified elsewhere", "分类于他处的疾病所致痴呆",
    subtypes=[{"code":"6D85.0","name":"Due to Parkinson disease","name_zh":"帕金森病性痴呆"},
              {"code":"6D85.1","name":"Due to Huntington disease","name_zh":"亨廷顿病性痴呆"},
              {"code":"6D85.2","name":"Due to HIV","name_zh":"HIV性痴呆"},
              {"code":"6D85.3","name":"Due to prion disease","name_zh":"朊蛋白病性痴呆"},
              {"code":"6D85.4","name":"Due to traumatic brain injury","name_zh":"创伤性脑损伤性痴呆"}]),
  D("6D86", "Behavioural or psychological disturbances in dementia", "痴呆中的精神或行为紊乱",
    relevant_scales=["NPI-Q","BEHAVE-AD","MOSES"]),
  D("6D8Z", "Dementia, unknown cause", "痴呆,原因未知或未特定"),
  D("6E0Y", "Other specified neurocognitive disorders", "其他特指的神经认知障碍"),
  D("6E0Z", "Neurocognitive disorders, unspecified", "神经认知障碍,未特指的"),
])

# ====== Block 19: Mental disorders associated with pregnancy ======
B("L1-6E2", "Mental/behavioural disorders associated with pregnancy, childbirth or the puerperium", "与妊娠、分娩和产褥期有关的精神或行为障碍", "6E20-6E2Z", [
  D("6E20", "Perinatal mental disorders without psychotic symptoms", "不伴精神病性症状",
    subtypes=[{"code":"6E20.0","name":"Postpartum depression NOS","name_zh":"产后抑郁NOS"}],
    typical_age=[16,45], gender_ratio="F only",
    relevant_scales=["EPDS"]),
  D("6E21", "Perinatal mental disorders with psychotic symptoms", "伴精神病性症状",
    typical_age=[16,45], gender_ratio="F only"),
  D("6E2Z", "Perinatal mental disorders, unspecified", "未特指的"),
])

# ====== Block 20: Psychological factors affecting medical conditions ======
B("L1-6E4", "Psychological or behavioural factors affecting disorders classified elsewhere", "心理或行为因素影响分类于他处的疾患或疾病", "6E40", [
  D("6E40", "Psychological/behavioural factors affecting medical conditions", "影响分类于他处的疾患或疾病的心理或行为因素",
    subtypes=[{"code":"6E40.0","name":"Mental disorder","name_zh":"精神障碍"},
              {"code":"6E40.1","name":"Psychological symptoms","name_zh":"心理症状"},
              {"code":"6E40.2","name":"Personality traits/coping","name_zh":"人格特征或应对方式"},
              {"code":"6E40.3","name":"Maladaptive health behaviours","name_zh":"适应不良健康行为"},
              {"code":"6E40.4","name":"Stress-related physiological response","name_zh":"应激相关生理反应"}]),
])

# ====== Block 21: Secondary mental/behavioural syndromes ======
B("L1-6E6", "Secondary mental/behavioural syndromes associated with disorders classified elsewhere", "与分类于他处的障碍或疾病相关的继发性精神或行为综合征", "6E60-6E6Z", [
  D("6E60", "Secondary neurodevelopmental syndrome", "继发性神经发育综合征",
    subtypes=[{"code":"6E60.0","name":"Secondary speech/language syndrome","name_zh":"继发性言语或语言综合征"}]),
  D("6E61", "Secondary psychotic syndrome", "继发性精神病性综合征",
    subtypes=[{"code":"6E61.0","name":"With hallucinations","name_zh":"伴幻觉"},
              {"code":"6E61.1","name":"With delusions","name_zh":"伴妄想"}]),
  D("6E62", "Secondary mood syndrome", "继发性心境障碍",
    subtypes=[{"code":"6E62.0","name":"With depressive symptoms","name_zh":"伴抑郁症状"},
              {"code":"6E62.1","name":"With manic symptoms","name_zh":"伴躁狂症状"}]),
  D("6E63", "Secondary anxiety syndrome", "继发性焦虑综合征"),
  D("6E64", "Secondary obsessive-compulsive or related syndrome", "继发性强迫或相关综合征"),
  D("6E65", "Secondary dissociative syndrome", "继发性分离综合征"),
  D("6E66", "Secondary impulse control syndrome", "继发性冲动控制综合征"),
  D("6E67", "Secondary neurocognitive syndrome", "继发性神经认知综合征"),
  D("6E68", "Secondary personality change", "继发性人格改变"),
  D("6E69", "Secondary catatonia syndrome", "继发性紧张症综合征"),
  D("6E6Y", "Other specified secondary syndrome", "其他特指的继发性精神或行为综合征"),
  D("6E6Z", "Secondary syndrome, unspecified", "未特指的继发性精神或行为综合征"),
])

# ====== Block 22: Other/unspecified ======
B("L1-6E8", "Other specified/unspecified mental disorders", "其他或未特指的精神、行为或神经发育障碍", "6E8Y-6E8Z", [
  D("6E8Y", "Other specified mental/behavioural/neurodevelopmental disorders", "其他特指的精神、行为或神经发育障碍"),
  D("6E8Z", "Mental/behavioural/neurodevelopmental disorders, unspecified", "精神、行为或神经发育障碍,未特指的"),
])

# ====== DSM-5-TR ======
DSM5TR = {
    "id": "dsm5tr",
    "name": "Diagnostic and Statistical Manual of Mental Disorders, 5th Edition, Text Revision",
    "name_zh": "精神障碍诊断与统计手册（第五版·文本修订）",
    "year": 2022,
    "publisher": "American Psychiatric Association",
    "total_categories": 297,
    "chapters": []
}

D_PARAMS = {"code","name_en","name_zh","subtypes","common_comorbidities",
            "typical_age","gender_ratio","relevant_scales",
            "severity_dimensions","description_en","description_zh"}

def CH(name_en, name_zh, disorders, description_en="", description_zh=""):
    converted = []
    for d in disorders:
        if isinstance(d, dict):
            if "name" in d and "name_en" not in d:
                d["name_en"] = d.pop("name")
            # Keep only parameters that D() accepts
            filtered = {k:v for k,v in d.items() if k in D_PARAMS}
            converted.append(D(**filtered))
        else:
            converted.append(d)
    DSM5TR["chapters"].append({
        "name": name_en, "name_zh": name_zh,
        "description": description_en, "description_zh": description_zh,
        "disorders": converted
    })

CH("Neurodevelopmental Disorders", "神经发育障碍", [
  {"code":"","name":"Intellectual Disability (Intellectual Developmental Disorder)","name_zh":"智力残疾（智力发育障碍）"},
  {"code":"","name":"Global Developmental Delay","name_zh":"全面发育迟缓"},
  {"code":"","name":"Language Disorder","name_zh":"语言障碍"},
  {"code":"","name":"Speech Sound Disorder","name_zh":"语音障碍"},
  {"code":"","name":"Childhood-Onset Fluency Disorder (Stuttering)","name_zh":"儿童期起病的言语流畅障碍（口吃）"},
  {"code":"","name":"Social (Pragmatic) Communication Disorder","name_zh":"社交（语用）沟通障碍"},
  {"code":"","name":"Autism Spectrum Disorder","name_zh":"孤独症谱系障碍"},
  {"code":"","name":"Attention-Deficit/Hyperactivity Disorder","name_zh":"注意缺陷/多动障碍"},
  {"code":"","name":"Specific Learning Disorder","name_zh":"特定学习障碍"},
  {"code":"","name":"Developmental Coordination Disorder","name_zh":"发育性协调障碍"},
  {"code":"","name":"Stereotypic Movement Disorder","name_zh":"刻板性运动障碍"},
  {"code":"","name":"Tourette's Disorder","name_zh":"妥瑞氏障碍"},
  {"code":"","name":"Persistent (Chronic) Motor or Vocal Tic Disorder","name_zh":"持续性（慢性）运动或发声抽动障碍"},
  {"code":"","name":"Provisional Tic Disorder","name_zh":"暂时性抽动障碍"},
])
CH("Schizophrenia Spectrum and Other Psychotic Disorders", "精神分裂症谱系及其他精神病性障碍", [
  {"code":"","name":"Schizotypal (Personality) Disorder","name_zh":"分裂型（人格）障碍"},
  {"code":"","name":"Delusional Disorder","name_zh":"妄想性障碍"},
  {"code":"","name":"Brief Psychotic Disorder","name_zh":"短暂精神病性障碍"},
  {"code":"","name":"Schizophreniform Disorder","name_zh":"精神分裂症样障碍"},
  {"code":"","name":"Schizophrenia","name_zh":"精神分裂症"},
  {"code":"","name":"Schizoaffective Disorder","name_zh":"分裂情感性障碍"},
  {"code":"","name":"Substance/Medication-Induced Psychotic Disorder","name_zh":"物质/药物所致精神病性障碍"},
  {"code":"","name":"Psychotic Disorder Due to Another Medical Condition","name_zh":"由于其他躯体疾病所致精神病性障碍"},
  {"code":"","name":"Catatonia Associated With Another Mental Disorder","name_zh":"与其他精神障碍相关的紧张症"},
  {"code":"","name":"Catatonic Disorder Due to Another Medical Condition","name_zh":"由于其他躯体疾病所致紧张症障碍"},
])
CH("Bipolar and Related Disorders", "双相及相关障碍", [
  {"code":"","name":"Bipolar I Disorder","name_zh":"双相I型障碍"},
  {"code":"","name":"Bipolar II Disorder","name_zh":"双相II型障碍"},
  {"code":"","name":"Cyclothymic Disorder","name_zh":"环性心境障碍"},
  {"code":"","name":"Substance/Medication-Induced Bipolar and Related Disorder","name_zh":"物质/药物所致双相及相关障碍"},
  {"code":"","name":"Bipolar and Related Disorder Due to Another Medical Condition","name_zh":"由于其他躯体疾病所致双相及相关障碍"},
])
CH("Depressive Disorders", "抑郁障碍", [
  {"code":"","name":"Disruptive Mood Dysregulation Disorder","name_zh":"破坏性心境失调障碍"},
  {"code":"","name":"Major Depressive Disorder, Single Episode","name_zh":"重性抑郁障碍，单次发作"},
  {"code":"","name":"Major Depressive Disorder, Recurrent","name_zh":"重性抑郁障碍，复发性"},
  {"code":"","name":"Persistent Depressive Disorder (Dysthymia)","name_zh":"持续性抑郁障碍（恶劣心境）"},
  {"code":"","name":"Premenstrual Dysphoric Disorder","name_zh":"经前期烦躁障碍"},
  {"code":"","name":"Substance/Medication-Induced Depressive Disorder","name_zh":"物质/药物所致抑郁障碍"},
  {"code":"","name":"Depressive Disorder Due to Another Medical Condition","name_zh":"由于其他躯体疾病所致抑郁障碍"},
])
CH("Anxiety Disorders", "焦虑障碍", [
  {"code":"F93.0","name":"Separation Anxiety Disorder","name_zh":"分离焦虑障碍"},
  {"code":"F94.0","name":"Selective Mutism","name_zh":"选择性缄默症"},
  {"code":"F40.2","name":"Specific Phobia","name_zh":"特定恐怖症"},
  {"code":"F40.10","name":"Social Anxiety Disorder (Social Phobia)","name_zh":"社交焦虑障碍（社交恐怖症）"},
  {"code":"F41.0","name":"Panic Disorder","name_zh":"惊恐障碍"},
  {"code":"F40.00","name":"Agoraphobia","name_zh":"广场恐怖"},
  {"code":"F41.1","name":"Generalized Anxiety Disorder","name_zh":"广泛性焦虑障碍"},
  {"code":"","name":"Substance/Medication-Induced Anxiety Disorder","name_zh":"物质/药物所致焦虑障碍"},
  {"code":"F06.4","name":"Anxiety Disorder Due to Another Medical Condition","name_zh":"由于其他躯体疾病所致焦虑障碍"},
])
CH("Obsessive-Compulsive and Related Disorders", "强迫及相关障碍", [
  {"code":"F42.2","name":"Obsessive-Compulsive Disorder","name_zh":"强迫症"},
  {"code":"F45.22","name":"Body Dysmorphic Disorder","name_zh":"躯体变形障碍"},
  {"code":"","name":"Hoarding Disorder","name_zh":"囤积障碍"},
  {"code":"","name":"Trichotillomania (Hair-Pulling Disorder)","name_zh":"拔毛癖（拔毛障碍）"},
  {"code":"","name":"Excoriation (Skin-Picking) Disorder","name_zh":"抓痕障碍"},
  {"code":"","name":"Substance/Medication-Induced OCD and Related Disorder","name_zh":"物质/药物所致强迫及相关障碍"},
])
CH("Trauma- and Stressor-Related Disorders", "创伤及应激相关障碍", [
  {"code":"","name":"Reactive Attachment Disorder","name_zh":"反应性依恋障碍"},
  {"code":"","name":"Disinhibited Social Engagement Disorder","name_zh":"脱抑制性社会参与障碍"},
  {"code":"","name":"Posttraumatic Stress Disorder","name_zh":"创伤后应激障碍"},
  {"code":"","name":"Acute Stress Disorder","name_zh":"急性应激障碍"},
  {"code":"","name":"Adjustment Disorders","name_zh":"适应障碍"},
  {"code":"","name":"Prolonged Grief Disorder","name_zh":"延长哀伤障碍"},
])
CH("Dissociative Disorders", "分离障碍", [
  {"code":"","name":"Dissociative Identity Disorder","name_zh":"分离性身份障碍"},
  {"code":"","name":"Dissociative Amnesia","name_zh":"分离性遗忘症"},
  {"code":"","name":"Depersonalization/Derealization Disorder","name_zh":"人格解体/现实解体障碍"},
])
CH("Somatic Symptom and Related Disorders", "躯体症状及相关障碍", [
  {"code":"","name":"Somatic Symptom Disorder","name_zh":"躯体症状障碍"},
  {"code":"","name":"Illness Anxiety Disorder","name_zh":"疾病焦虑障碍（疑病症）"},
  {"code":"","name":"Functional Neurological Symptom Disorder (Conversion Disorder)","name_zh":"功能性神经症状障碍（转换障碍）"},
  {"code":"","name":"Psychological Factors Affecting Other Medical Conditions","name_zh":"影响其他医疗状况的心理因素"},
  {"code":"","name":"Factitious Disorder","name_zh":"做作性障碍"},
])
CH("Feeding and Eating Disorders", "喂食及进食障碍", [
  {"code":"","name":"Pica","name_zh":"异食癖"},
  {"code":"","name":"Rumination Disorder","name_zh":"反刍障碍"},
  {"code":"","name":"Avoidant/Restrictive Food Intake Disorder","name_zh":"回避/限制性摄食障碍"},
  {"code":"","name":"Anorexia Nervosa","name_zh":"神经性厌食"},
  {"code":"","name":"Bulimia Nervosa","name_zh":"神经性贪食"},
  {"code":"","name":"Binge-Eating Disorder","name_zh":"暴食障碍"},
])
CH("Elimination Disorders", "排泄障碍", [
  {"code":"","name":"Enuresis","name_zh":"遗尿症"},
  {"code":"","name":"Encopresis","name_zh":"遗粪症"},
])
CH("Sleep-Wake Disorders", "睡眠-觉醒障碍", [
  {"code":"","name":"Insomnia Disorder","name_zh":"失眠障碍"},
  {"code":"","name":"Hypersomnolence Disorder","name_zh":"嗜睡障碍"},
  {"code":"","name":"Narcolepsy","name_zh":"发作性睡病"},
  {"code":"","name":"Obstructive Sleep Apnea Hypopnea","name_zh":"阻塞性睡眠呼吸暂停低通气"},
  {"code":"","name":"Central Sleep Apnea","name_zh":"中枢性睡眠呼吸暂停"},
  {"code":"","name":"Sleep-Related Hypoventilation","name_zh":"睡眠相关性低通气"},
  {"code":"","name":"Circadian Rhythm Sleep-Wake Disorder","name_zh":"昼夜节律睡眠-觉醒障碍"},
  {"code":"","name":"Non-Rapid Eye Movement Sleep Arousal Disorders","name_zh":"非快速眼动睡眠唤醒障碍"},
  {"code":"","name":"Nightmare Disorder","name_zh":"梦魇障碍"},
  {"code":"","name":"REM Sleep Behavior Disorder","name_zh":"REM睡眠行为障碍"},
  {"code":"","name":"Restless Legs Syndrome","name_zh":"不宁腿综合征"},
  {"code":"","name":"Substance/Medication-Induced Sleep Disorder","name_zh":"物质/药物所致睡眠障碍"},
])
CH("Sexual Dysfunctions", "性功能障碍", [
  {"code":"","name":"Delayed Ejaculation","name_zh":"延迟射精"},
  {"code":"","name":"Erectile Disorder","name_zh":"勃起障碍"},
  {"code":"","name":"Female Orgasmic Disorder","name_zh":"女性高潮障碍"},
  {"code":"","name":"Female Sexual Interest/Arousal Disorder","name_zh":"女性性兴趣/唤起障碍"},
  {"code":"","name":"Genito-Pelvic Pain/Penetration Disorder","name_zh":"生殖-盆腔痛/插入障碍"},
  {"code":"","name":"Male Hypoactive Sexual Desire Disorder","name_zh":"男性性欲减退障碍"},
  {"code":"","name":"Premature (Early) Ejaculation","name_zh":"早泄"},
  {"code":"","name":"Substance/Medication-Induced Sexual Dysfunction","name_zh":"物质/药物所致性功能障碍"},
])
CH("Gender Dysphoria", "性别烦躁", [
  {"code":"","name":"Gender Dysphoria","name_zh":"性别烦躁"},
])
CH("Disruptive, Impulse-Control, and Conduct Disorders", "破坏性、冲动控制及品行障碍", [
  {"code":"","name":"Oppositional Defiant Disorder","name_zh":"对立违抗障碍"},
  {"code":"","name":"Intermittent Explosive Disorder","name_zh":"间歇性暴怒障碍"},
  {"code":"","name":"Conduct Disorder","name_zh":"品行障碍"},
  {"code":"","name":"Antisocial Personality Disorder","name_zh":"反社会型人格障碍"},
  {"code":"","name":"Pyromania","name_zh":"纵火癖"},
  {"code":"","name":"Kleptomania","name_zh":"盗窃癖"},
])
CH("Substance-Related and Addictive Disorders", "物质相关及成瘾障碍", [
  {"code":"","name":"Alcohol Use Disorder","name_zh":"酒精使用障碍"},
  {"code":"","name":"Caffeine Intoxication/Withdrawal","name_zh":"咖啡因中毒/戒断"},
  {"code":"","name":"Cannabis Use Disorder","name_zh":"大麻使用障碍"},
  {"code":"","name":"Hallucinogen Use Disorder","name_zh":"致幻剂使用障碍"},
  {"code":"","name":"Inhalant Use Disorder","name_zh":"吸入剂使用障碍"},
  {"code":"","name":"Opioid Use Disorder","name_zh":"阿片类使用障碍"},
  {"code":"","name":"Sedative/Hypnotic/Anxiolytic Use Disorder","name_zh":"镇静/催眠/抗焦虑药使用障碍"},
  {"code":"","name":"Stimulant Use Disorder","name_zh":"兴奋剂使用障碍"},
  {"code":"","name":"Tobacco Use Disorder","name_zh":"烟草使用障碍"},
  {"code":"","name":"Gambling Disorder","name_zh":"赌博障碍"},
])
CH("Neurocognitive Disorders", "神经认知障碍", [
  {"code":"","name":"Delirium","name_zh":"谵妄"},
  {"code":"","name":"Major or Mild NCD Due to Alzheimer's Disease","name_zh":"阿尔茨海默病所致重度或轻度NCD"},
  {"code":"","name":"Major or Mild Frontotemporal NCD","name_zh":"额颞叶NCD"},
  {"code":"","name":"Major or Mild NCD With Lewy Bodies","name_zh":"路易体NCD"},
  {"code":"","name":"Major or Mild Vascular NCD","name_zh":"血管性NCD"},
  {"code":"","name":"Major or Mild NCD Due to Traumatic Brain Injury","name_zh":"创伤性脑损伤所致NCD"},
  {"code":"","name":"Major or Mild NCD Due to HIV Infection","name_zh":"HIV感染所致NCD"},
  {"code":"","name":"Major or Mild NCD Due to Prion Disease","name_zh":"朊蛋白病所致NCD"},
  {"code":"","name":"Major or Mild NCD Due to Parkinson's Disease","name_zh":"帕金森病所致NCD"},
  {"code":"","name":"Major or Mild NCD Due to Huntington's Disease","name_zh":"亨廷顿病所致NCD"},
])
CH("Personality Disorders", "人格障碍", [
  {"code":"","name":"Paranoid Personality Disorder","name_zh":"偏执型人格障碍","note":"Cluster A"},
  {"code":"","name":"Schizoid Personality Disorder","name_zh":"分裂样人格障碍","note":"Cluster A"},
  {"code":"","name":"Schizotypal Personality Disorder","name_zh":"分裂型人格障碍","note":"Cluster A"},
  {"code":"","name":"Antisocial Personality Disorder","name_zh":"反社会型人格障碍","note":"Cluster B"},
  {"code":"","name":"Borderline Personality Disorder","name_zh":"边缘型人格障碍","note":"Cluster B"},
  {"code":"","name":"Histrionic Personality Disorder","name_zh":"表演型人格障碍","note":"Cluster B"},
  {"code":"","name":"Narcissistic Personality Disorder","name_zh":"自恋型人格障碍","note":"Cluster B"},
  {"code":"","name":"Avoidant Personality Disorder","name_zh":"回避型人格障碍","note":"Cluster C"},
  {"code":"","name":"Dependent Personality Disorder","name_zh":"依赖型人格障碍","note":"Cluster C"},
  {"code":"","name":"Obsessive-Compulsive Personality Disorder","name_zh":"强迫型人格障碍","note":"Cluster C"},
])
CH("Paraphilic Disorders", "性偏好障碍", [
  {"code":"","name":"Voyeuristic Disorder","name_zh":"窥阴障碍"},
  {"code":"","name":"Exhibitionistic Disorder","name_zh":"露阴障碍"},
  {"code":"","name":"Frotteuristic Disorder","name_zh":"摩擦障碍"},
  {"code":"","name":"Sexual Masochism Disorder","name_zh":"性受虐障碍"},
  {"code":"","name":"Sexual Sadism Disorder","name_zh":"性施虐障碍"},
  {"code":"","name":"Pedophilic Disorder","name_zh":"恋童障碍"},
  {"code":"","name":"Fetishistic Disorder","name_zh":"恋物障碍"},
  {"code":"","name":"Transvestic Disorder","name_zh":"异装障碍"},
])
CH("Other Mental Disorders and Additional Codes", "其他精神障碍及附加编码", [
  {"code":"","name":"Other Specified Mental Disorder Due to Medical Condition","name_zh":"由于躯体疾病的其他特指精神障碍"},
  {"code":"","name":"Unspecified Mental Disorder Due to Medical Condition","name_zh":"由于躯体疾病的未特指精神障碍"},
  {"code":"","name":"Other Specified Mental Disorder","name_zh":"其他特指的精神障碍"},
  {"code":"","name":"Unspecified Mental Disorder","name_zh":"未特指的精神障碍"},
])
CH("Medication-Induced Movement Disorders", "药物所致运动障碍", [
  {"code":"","name":"Medication-Induced Parkinsonism","name_zh":"药物所致帕金森症"},
  {"code":"","name":"Neuroleptic Malignant Syndrome","name_zh":"神经阻滞剂恶性综合征"},
  {"code":"","name":"Medication-Induced Acute Dystonia","name_zh":"药物所致急性肌张力障碍"},
  {"code":"","name":"Medication-Induced Acute Akathisia","name_zh":"药物所致急性静坐不能"},
  {"code":"","name":"Tardive Dyskinesia","name_zh":"迟发性运动障碍"},
  {"code":"","name":"Antidepressant Discontinuation Syndrome","name_zh":"抗抑郁药停药综合征"},
])

# Save part 3
with open(os.path.join(BUILD_DIR, "icd11_part3.json"), "w", encoding="utf-8") as f:
    json.dump({"blocks": ICD11_BLOCKS, "dsm5tr": DSM5TR}, f, ensure_ascii=False, indent=2)
print(f"Part 3 saved: {len(ICD11_BLOCKS)} ICD-11 blocks, {len(DSM5TR['chapters'])} DSM-5-TR chapters")
