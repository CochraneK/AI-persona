"""
生活事件模块 — 2D 事件矩阵（MECE 设计） + 增强理论框架

=========================================================================
设计原则（MECE）
=========================================================================
采用 2D 矩阵：6 个领域(domain) × 4 个时间阶段(life_stage) = 24 格。
每个格包含多个事件模板，共同构成一个人从出生到当前的人生事件全集。

领域划分（MECE：互斥 + 全覆盖）：
  1. 家庭 (Family)        — 与亲属关系、家庭结构相关的事件
  2. 教育 (Education)     — 与正式学习、学术经历相关的事件
  3. 职业 (Occupation)    — 与工作、就业、事业相关的事件
  4. 健康 (Health)        — 与身心疾病、医疗、生理变化相关的事件
  5. 经济 (Finance)       — 与收入、资产、消费、财务相关的事件
  6. 人际 (Interpersonal) — 与朋友、社交、社区关系相关的事件

四个时间阶段：
  1. 童年 (Childhood)      — 0-12 岁
  2. 青少年 (Adolescence)  — 13-17 岁
  3. 成年 (Adulthood)     — 18-40 岁
  4. 中老年 (Mid/Older)   — 41 岁及以上

=========================================================================
诊断关联事件
=========================================================================
除了通用的生活事件模板，还定义了各诊断特有的典型"触发事件"，
这些事件与该诊断的发病/恶化/维持密切相关。
例如：抑郁 — 重大丧失，焦虑 — 社交暴露，创伤 — 事故/暴力经历。

=========================================================================
理论框架（v2 增强）
=========================================================================
  - Holmes & Rahe (1967) Social Readjustment Rating Scale (SRRS):
    首次量化生活事件的压力权重（Life Change Units, LCU），发现累积 LCU 与疾病风险正相关。
    本模块包含完整的 SRRS 36 项参考表（SRRS_REFERENCE），用于标定所有 143 个事件模板的 LCU。
    
  - Brown & Harris (1978) 生活事件与抑郁研究：
    强调"丧失"类事件（loss events）是抑郁症的核心触发因素，提出情境威胁评级（contextual threat rating）。
    → 实现：VulnerabilityFactors 四因子评估 + evaluate_vulnerability() + 诊断特异性脆弱性配置

  - Finlay-Jones & Brown (1981) 事件类型与焦虑研究：
    区分"丧失"（loss → 抑郁）与"危险"（danger → 焦虑）两类事件的不同病理效应。
    → 实现：EVENT_TYPE_SRRS_MAP 将每个事件归类为 loss/danger/humiliation/entrapment/positive/neutral

  - Kendler et al. (1995, 2003) 事件类型与抑郁：
    扩展 Brown & Harris 分类，增加"羞辱"（humiliation）和"陷阱"（entrapment）两类触发事件。
    → 实现：classify_event_type() 函数，支持四类负性事件 + 多维敏感性权重

  - Felitti et al. (1998) 童年逆境经历（ACEs）研究：
    发现 10 类童年逆境与成年后多种身心疾病呈剂量-反应关系，ACE 得分 ≥4 者风险显著升高。
    → 实现：ACES_DOSE_RESPONSE 剂量-反应表 + aces_risk_multiplier() + aces_condition_risk()

  - Hammen (1991) Stress Generation 假说：
    抑郁和人格障碍患者不仅是生活事件的被动受害者，还会主动（无意识地）制造更多压力事件。
    → 实现：STRESS_GENERATION_WEIGHTS + stress_generation_multiplier()

  - Tennant (2002) 生活事件与精神病理学元分析：
    确认负性生活事件是抑郁、焦虑等障碍的重要前因，效应量中等，遗传-环境交互作用不可忽视。
    → 实现：DIAGNOSIS_VULNERABILITY 中 events_to_trigger + 敏感性系数，综合应评估 assess_stress_burden()

=========================================================================
综合应激评估
=========================================================================
  - assess_stress_burden(): 整合 LCU + ACEs + 脆弱性 + stress generation 四个维度的综合评估
  - 输出：定量风险评分 + 风险分层（低/中/高/极高）+ 自然语言解读
=========================================================================
"""

from dataclasses import dataclass, field
from typing import Optional
import random

from .human_ontology import map_legacy_event_domain, map_legacy_event_stage

# =====================================================================
# 数据类型
# =====================================================================

@dataclass
class LifeEvent:
    """单个生活事件模板"""
    domain: str               # 所属领域：family/education/occupation/health/finance/interpersonal
    stage: str                # 所属阶段：childhood/adolescence/adulthood/mid_older
    name_cn: str              # 中文名称
    name_en: str              # 英文名称
    valence: str              # 效价：positive / negative / neutral
    diagnosis_relation: Optional[dict[str, str]] = None
    # 诊断关联：{"diagnosis_key": "trigger"/"maintain"/"unrelated"}
    # trigger = 触发因素，maintain = 维持因素，unrelated = 无关
    lcu: int = 50             # Life Change Unit (SRRS 权重)，默认 50 = 中等压力

    # --- canonical Human Ontology 映射（v1.3，只读属性，不影响序列化） ---
    # legacy 6 域 × 4 阶段矩阵保留为 legacy source，canonical id 经
    # core/human_ontology.py 引用，不在本模块本地重定义。

    @property
    def canonical_domain(self) -> str | None:
        """canonical life domain id（如 family → family_kinship）"""
        return map_legacy_event_domain(self.domain)

    @property
    def canonical_stages(self) -> tuple[str, ...]:
        """canonical developmental stage ids（如 childhood → (early_childhood, middle_childhood)）"""
        return map_legacy_event_stage(self.stage)


# =====================================================================
# 6 领域 × 4 阶段 = 24 格事件矩阵
# =====================================================================

LIFE_EVENTS: list[LifeEvent] = [
    # ==================== 家庭领域 ====================

    # ---- 童年 ----
    LifeEvent("family", "childhood", "出生在完整双亲家庭", "Born into intact two-parent family", "positive", lcu=15),
    LifeEvent("family", "childhood", "父母离异", "Parents divorced", "negative", lcu=73, diagnosis_relation={"depressive": "trigger", "anxiety": "trigger", "adjustment": "trigger"}),
    LifeEvent("family", "childhood", "与祖父母共同生活", "Lived with grandparents", "neutral"),
    LifeEvent("family", "childhood", "独生子女", "Only child", "neutral"),
    LifeEvent("family", "childhood", "有多个兄弟姐妹", "Had multiple siblings", "neutral"),
    LifeEvent("family", "childhood", "家庭经济困难", "Family financial difficulties", "negative", lcu=38),
    LifeEvent("family", "childhood", "父母长期在外务工", "Parents worked away from home long-term", "negative", lcu=25),
    LifeEvent("family", "childhood", "被收养", "Adopted", "negative", lcu=50, diagnosis_relation={"adjustment": "trigger", "depressive": "trigger"}),
    LifeEvent("family", "childhood", "家庭氛围温暖和睦", "Warm and harmonious family atmosphere", "positive", lcu=15),
    LifeEvent("family", "childhood", "父母严厉/体罚", "Strict parents / corporal punishment", "negative", lcu=53, diagnosis_relation={"ptsd": "trigger", "anxiety": "trigger", "depressive": "trigger"}),
    LifeEvent("family", "childhood", "失去父亲或母亲", "Lost a parent", "negative", lcu=63, diagnosis_relation={"depressive": "trigger", "ptsd": "trigger", "adjustment": "trigger"}),

    # ---- 青少年 ----
    LifeEvent("family", "adolescence", "与父母关系紧张", "Strained relationship with parents", "negative", lcu=35),
    LifeEvent("family", "adolescence", "家庭重组/继父母进入", "Family restructured / step-parent entered", "negative", lcu=39, diagnosis_relation={"adjustment": "trigger", "anxiety": "trigger"}),
    LifeEvent("family", "adolescence", "离家出走", "Ran away from home", "negative", lcu=63, diagnosis_relation={"depressive": "trigger", "borderline_pd": "trigger"}),
    LifeEvent("family", "adolescence", "父母再婚", "Parent remarried", "neutral", lcu=39),
    LifeEvent("family", "adolescence", "与父母关系密切亲昵", "Close and warm relationship with parents", "positive", lcu=15),
    LifeEvent("family", "adolescence", "亲戚重大变故（如去世）", "Major change in extended family", "negative", lcu=44),

    # ---- 成年 ----
    LifeEvent("family", "adulthood", "结婚", "Got married", "positive", lcu=50),
    LifeEvent("family", "adulthood", "离婚", "Got divorced", "negative", lcu=73, diagnosis_relation={"depressive": "trigger", "adjustment": "trigger", "alcohol": "trigger"}),
    LifeEvent("family", "adulthood", "生育第一个孩子", "Had first child", "positive", lcu=39),
    LifeEvent("family", "adulthood", "父母患病需要照顾", "Parents fell ill and needed care", "negative", lcu=44, diagnosis_relation={"anxiety": "trigger", "depressive": "trigger", "adjustment": "trigger"}),
    LifeEvent("family", "adulthood", "父母去世", "Parent passed away", "negative", lcu=63, diagnosis_relation={"depressive": "trigger", "adjustment": "trigger", "ptsd": "trigger"}),
    LifeEvent("family", "adulthood", "与配偶/伴侣分居", "Separated from spouse/partner", "negative", lcu=65),
    LifeEvent("family", "adulthood", "长期单身/未婚", "Remained single long-term", "neutral"),
    LifeEvent("family", "adulthood", "与伴侣关系稳定幸福", "Stable and happy relationship", "positive", lcu=20),
    LifeEvent("family", "adulthood", "子女有特殊需求", "Child has special needs", "negative", lcu=44, diagnosis_relation={"anxiety": "trigger", "depressive": "trigger"}),
    LifeEvent("family", "adulthood", "夫妻长期异地", "Long-distance marriage", "negative", lcu=45),

    # ---- 中老年 ----
    LifeEvent("family", "mid_older", "空巢(子女离家)", "Empty nest (children left home)", "neutral", lcu=29),
    LifeEvent("family", "mid_older", "成为祖父母", "Became grandparent", "positive", lcu=20),
    LifeEvent("family", "mid_older", "配偶去世", "Spouse passed away", "negative", lcu=100, diagnosis_relation={"depressive": "trigger", "adjustment": "trigger", "ptsd": "trigger"}),
    LifeEvent("family", "mid_older", "与成年子女同住", "Lived with adult children", "neutral"),
    LifeEvent("family", "mid_older", "兄弟姐妹去世", "Sibling passed away", "negative", lcu=63),

    # ==================== 教育领域 ====================

    # ---- 童年 ----
    LifeEvent("education", "childhood", "入读幼儿园", "Started kindergarten", "neutral"),
    LifeEvent("education", "childhood", "入读小学", "Started primary school", "neutral"),
    LifeEvent("education", "childhood", "学习成绩优异", "Excellent academic performance", "positive", lcu=22),
    LifeEvent("education", "childhood", "学习困难/跟不上", "Learning difficulties / falling behind", "negative", lcu=26),
    LifeEvent("education", "childhood", "被老师表扬/获得奖项", "Praised by teacher / received awards", "positive", lcu=20),
    LifeEvent("education", "childhood", "转学", "Changed school", "neutral", lcu=20),
    LifeEvent("education", "childhood", "因故辍学", "Dropped out of school", "negative", lcu=47, diagnosis_relation={"depressive": "trigger", "adjustment": "trigger"}),

    # ---- 青少年 ----
    LifeEvent("education", "adolescence", "升入重点初中/高中", "Entered selective school", "positive", lcu=26),
    LifeEvent("education", "adolescence", "中考/高考失利", "Failed entrance exams", "negative", lcu=38, diagnosis_relation={"depressive": "trigger", "anxiety": "trigger", "adjustment": "trigger"}),
    LifeEvent("education", "adolescence", "中考/高考成功", "Succeeded in entrance exams", "positive", lcu=28),
    LifeEvent("education", "adolescence", "被校园霸凌", "Bullied at school", "negative", lcu=53, diagnosis_relation={"ptsd": "trigger", "anxiety": "trigger", "depressive": "trigger", "social_anxiety": "trigger"}),
    LifeEvent("education", "adolescence", "参加竞赛并获得名次", "Won competition awards", "positive", lcu=22),
    LifeEvent("education", "adolescence", "担任学生干部", "Served as student leader", "positive", lcu=22),
    LifeEvent("education", "adolescence", "留学/交换", "Studied abroad / exchange", "neutral", lcu=26),
    LifeEvent("education", "adolescence", "被老师不公平对待", "Treated unfairly by teacher", "negative", lcu=23),

    # ---- 成年 ----
    LifeEvent("education", "adulthood", "上大学", "Attended university", "positive", lcu=26),
    LifeEvent("education", "adulthood", "读研究生/博士", "Pursued graduate/doctoral degree", "neutral", lcu=26),
    LifeEvent("education", "adulthood", "未接受高等教育", "Did not attend higher education", "neutral"),
    LifeEvent("education", "adulthood", "留学回国/完成学业", "Returned after overseas study", "positive", lcu=20),
    LifeEvent("education", "adulthood", "在职进修/继续教育", "Work-related further education", "positive", lcu=22),
    LifeEvent("education", "adulthood", "学术造假/论文被撤", "Academic misconduct / paper retraction", "negative", lcu=47, diagnosis_relation={"depressive": "trigger", "anxiety": "trigger"}),
    LifeEvent("education", "adulthood", "获得重要学位/资格证书", "Obtained important degree or certification", "positive", lcu=28),

    # ---- 中老年 ----
    LifeEvent("education", "mid_older", "老年大学/退休后学习", "Attended senior learning programs", "positive", lcu=26),
    LifeEvent("education", "mid_older", "辅导孙辈学习", "Tutored grandchildren", "neutral"),

    # ==================== 职业领域 ====================

    # ---- 青少年（兼职/打工） ----
    LifeEvent("occupation", "adolescence", "高中时期打工/兼职", "Had part-time job in high school", "neutral"),
    LifeEvent("occupation", "adolescence", "参加职业培训", "Attended vocational training", "neutral"),

    # ---- 成年 ----
    LifeEvent("occupation", "adulthood", "找到第一份工作", "Found first job", "positive", lcu=26),
    LifeEvent("occupation", "adulthood", "被裁员/失业", "Laid off / unemployed", "negative", lcu=47, diagnosis_relation={"depressive": "trigger", "anxiety": "trigger", "alcohol": "trigger", "adjustment": "trigger"}),
    LifeEvent("occupation", "adulthood", "升职/加薪", "Promotion / salary increase", "positive", lcu=28),
    LifeEvent("occupation", "adulthood", "创业", "Started a business", "neutral", lcu=39),
    LifeEvent("occupation", "adulthood", "创业失败", "Business failed", "negative", lcu=39, diagnosis_relation={"depressive": "trigger", "adjustment": "trigger"}),
    LifeEvent("occupation", "adulthood", "转行", "Career change", "neutral", lcu=36),
    LifeEvent("occupation", "adulthood", "长期从事同一工作", "Stayed in the same job long-term", "neutral"),
    LifeEvent("occupation", "adulthood", "职场性骚扰/歧视", "Experienced workplace harassment / discrimination", "negative", lcu=53, diagnosis_relation={"ptsd": "trigger", "anxiety": "trigger", "depressive": "trigger"}),
    LifeEvent("occupation", "adulthood", "工作中获得重要成就", "Achieved major accomplishment at work", "positive", lcu=28),
    LifeEvent("occupation", "adulthood", "被同事/上司排挤", "Ostracized by colleagues / supervisor", "negative", lcu=23, diagnosis_relation={"anxiety": "trigger", "depressive": "trigger"}),
    LifeEvent("occupation", "adulthood", "提前退休", "Retired early", "neutral", lcu=45),
    LifeEvent("occupation", "adulthood", "工作与家庭平衡困难", "Difficulty balancing work and family", "negative", lcu=35, diagnosis_relation={"anxiety": "trigger", "depressive": "trigger"}),

    # ---- 中老年 ----
    LifeEvent("occupation", "mid_older", "退休", "Retired", "neutral", lcu=45),
    LifeEvent("occupation", "mid_older", "返聘/退休后继续工作", "Rehired after retirement", "neutral"),
    LifeEvent("occupation", "mid_older", "职场生涯达到巅峰", "Reached career peak", "positive", lcu=28),
    LifeEvent("occupation", "mid_older", "因健康原因无法工作", "Unable to work due to health issues", "negative", lcu=53),
    LifeEvent("occupation", "mid_older", "养老金/退休金不足", "Insufficient pension", "negative", lcu=31),

    # ==================== 健康领域 ====================

    # ---- 童年 ----
    LifeEvent("health", "childhood", "出生时健康/足月", "Born healthy at full term", "positive", lcu=10),
    LifeEvent("health", "childhood", "早产/出生体重低", "Preterm birth / low birth weight", "negative", lcu=44),
    LifeEvent("health", "childhood", "患有慢性儿科疾病", "Had chronic pediatric illness", "negative", lcu=53),
    LifeEvent("health", "childhood", "经常生病/体质弱", "Frequently ill / weak constitution", "negative", lcu=44),
    LifeEvent("health", "childhood", "体质好/很少生病", "Good constitution / rarely ill", "positive", lcu=10),
    LifeEvent("health", "childhood", "遭遇严重意外伤害", "Experienced serious accidental injury", "negative", lcu=53, diagnosis_relation={"ptsd": "trigger", "anxiety": "trigger"}),

    # ---- 青少年 ----
    LifeEvent("health", "adolescence", "初潮/变声等青春期发育", "Puberty development milestone", "neutral"),
    LifeEvent("health", "adolescence", "青春期发育困扰", "Distressed about puberty development", "negative", lcu=39),
    LifeEvent("health", "adolescence", "开始出现心理健康问题", "First onset of mental health issues", "negative", lcu=44, diagnosis_relation={"depressive": "trigger", "anxiety": "trigger"}),
    LifeEvent("health", "adolescence", "体检发现身体异常", "Physical exam abnormality detected", "negative", lcu=44),

    # ---- 成年 ----
    LifeEvent("health", "adulthood", "确诊慢性身心疾病", "Diagnosed with chronic medical condition", "negative", lcu=53, diagnosis_relation={"depressive": "trigger", "anxiety": "trigger", "adjustment": "trigger"}),
    LifeEvent("health", "adulthood", "经历重大手术", "Underwent major surgery", "negative", lcu=53, diagnosis_relation={"ptsd": "trigger", "anxiety": "trigger"}),
    LifeEvent("health", "adulthood", "心理/精神科治疗经历", "Received psychiatric treatment", "neutral", lcu=44),
    LifeEvent("health", "adulthood", "住院治疗", "Hospitalized for treatment", "negative", lcu=53),
    LifeEvent("health", "adulthood", "经历药物的副作用", "Experienced medication side effects", "negative", lcu=44),
    LifeEvent("health", "adulthood", "戒酒/戒毒成功", "Successfully quit alcohol/drugs", "positive", lcu=25),
    LifeEvent("health", "adulthood", "症状缓解/康复", "Symptoms remitted / recovered", "positive", lcu=20),
    LifeEvent("health", "adulthood", "自杀未遂", "Attempted suicide", "negative", lcu=63, diagnosis_relation={"depressive": "maintain", "borderline_pd": "maintain", "ptsd": "trigger"}),
    LifeEvent("health", "adulthood", "自伤行为", "Self-injurious behavior", "negative", lcu=53, diagnosis_relation={"borderline_pd": "maintain", "depressive": "maintain"}),

    # ---- 中老年 ----
    LifeEvent("health", "mid_older", "确诊重大疾病", "Diagnosed with major illness", "negative", lcu=63, diagnosis_relation={"depressive": "trigger", "anxiety": "trigger", "adjustment": "trigger"}),
    LifeEvent("health", "mid_older", "更年期", "Menopause (or male climacteric)", "neutral", lcu=39),
    LifeEvent("health", "mid_older", "认知功能下降", "Cognitive decline", "negative", lcu=44, diagnosis_relation={"depressive": "trigger", "anxiety": "trigger"}),
    LifeEvent("health", "mid_older", "长期服药维持治疗", "Long-term maintenance medication", "neutral"),
    LifeEvent("health", "mid_older", "体能明显下降", "Notable decline in physical strength", "negative", lcu=35),
    LifeEvent("health", "mid_older", "保持良好健康习惯", "Maintained good health habits", "positive", lcu=10),

    # ==================== 经济领域 ====================

    # ---- 童年 ----
    LifeEvent("finance", "childhood", "家庭经济状况良好", "Family in good financial condition", "positive", lcu=15),
    LifeEvent("finance", "childhood", "因贫困缺乏基本生活保障", "Lacked basic necessities due to poverty", "negative", lcu=38),
    LifeEvent("finance", "childhood", "有零花钱/压岁钱", "Had allowance / lucky money", "positive", lcu=8),

    # ---- 青少年 ----
    LifeEvent("finance", "adolescence", "勤工俭学", "Work-study program", "neutral"),
    LifeEvent("finance", "adolescence", "经济拮据无法满足消费需求", "Financial constraints limited consumption", "negative", lcu=31),
    LifeEvent("finance", "adolescence", "家庭突然陷入经济困难", "Family suddenly fell into financial hardship", "negative", lcu=38, diagnosis_relation={"anxiety": "trigger", "depressive": "trigger"}),

    # ---- 成年 ----
    LifeEvent("finance", "adulthood", "收入可观/经济自由", "Good income / financial freedom", "positive", lcu=28),
    LifeEvent("finance", "adulthood", "背负巨额债务", "Burdened with massive debt", "negative", lcu=31, diagnosis_relation={"anxiety": "trigger", "depressive": "trigger", "alcohol": "trigger"}),
    LifeEvent("finance", "adulthood", "购房/购车等大件消费", "Major purchase (house/car)", "neutral", lcu=31),
    LifeEvent("finance", "adulthood", "投资获利/中奖", "Investment profit / won lottery", "positive", lcu=28),
    LifeEvent("finance", "adulthood", "投资失败/被骗", "Investment loss / got scammed", "negative", lcu=38, diagnosis_relation={"depressive": "trigger", "adjustment": "trigger"}),
    LifeEvent("finance", "adulthood", "长期月光族/储蓄少", "Living paycheck to paycheck", "negative", lcu=31),
    LifeEvent("finance", "adulthood", "经济独立不再依赖家人", "Financially independent from family", "positive", lcu=25),

    # ---- 中老年 ----
    LifeEvent("finance", "mid_older", "退休金充足/养老有保障", "Adequate pension / comfortable retirement", "positive", lcu=25),
    LifeEvent("finance", "mid_older", "退休金不足/经济困难", "Insufficient pension / financial hardship", "negative", lcu=38),
    LifeEvent("finance", "mid_older", "给子女经济支持/购房首付", "Supported children financially", "neutral", lcu=29),
    LifeEvent("finance", "mid_older", "被子女经济啃老", "Financially dependent on adult children", "negative", lcu=35),

    # ==================== 人际领域 ====================

    # ---- 童年 ----
    LifeEvent("interpersonal", "childhood", "有亲密好友/玩伴", "Had close friends / playmates", "positive", lcu=15),
    LifeEvent("interpersonal", "childhood", "朋友较少/孤僻", "Few friends / withdrawn", "negative", lcu=25),
    LifeEvent("interpersonal", "childhood", "在邻里/社区有归属感", "Felt belonging in neighborhood", "positive", lcu=15),
    LifeEvent("interpersonal", "childhood", "被同龄人排斥", "Rejected by peers", "negative", lcu=35, diagnosis_relation={"social_anxiety": "trigger", "depressive": "trigger", "anxiety": "trigger"}),
    LifeEvent("interpersonal", "childhood", "参加课外小组/社团", "Joined extracurricular groups", "positive", lcu=12),

    # ---- 青少年 ----
    LifeEvent("interpersonal", "adolescence", "初恋", "First romantic relationship", "neutral", lcu=26),
    LifeEvent("interpersonal", "adolescence", "失恋/分手", "Broke up with first love", "negative", lcu=37),
    LifeEvent("interpersonal", "adolescence", "拥有知心好友", "Had a confidant / best friend", "positive", lcu=18),
    LifeEvent("interpersonal", "adolescence", "被朋友背叛", "Betrayed by a friend", "negative", lcu=37, diagnosis_relation={"depressive": "trigger", "adjustment": "trigger"}),
    LifeEvent("interpersonal", "adolescence", "小团体/帮派经历", "Gang / clique involvement", "negative", lcu=31),
    LifeEvent("interpersonal", "adolescence", "网络交友/网友见面", "Online friendship / met online friend", "neutral"),
    LifeEvent("interpersonal", "adolescence", "社交媒体上被网暴", "Cyberbullied on social media", "negative", lcu=44, diagnosis_relation={"anxiety": "trigger", "depressive": "trigger", "ptsd": "trigger"}),

    # ---- 成年 ----
    LifeEvent("interpersonal", "adulthood", "建立稳定恋爱关系", "Established stable romantic relationship", "positive", lcu=20),
    LifeEvent("interpersonal", "adulthood", "与朋友保持密切往来", "Maintained close circle of friends", "positive", lcu=18),
    LifeEvent("interpersonal", "adulthood", "社交圈子狭窄/朋友少", "Narrow social circle / few friends", "negative", lcu=25),
    LifeEvent("interpersonal", "adulthood", "经历重大人际冲突", "Experienced major interpersonal conflict", "negative", lcu=35, diagnosis_relation={"depressive": "trigger", "adjustment": "trigger", "anxiety": "trigger"}),
    LifeEvent("interpersonal", "adulthood", "参加公益/志愿者活动", "Participated in volunteer activities", "positive", lcu=12),
    LifeEvent("interpersonal", "adulthood", "移民/搬迁到新城市", "Immigrated / moved to a new city", "neutral", lcu=20),
    LifeEvent("interpersonal", "adulthood", "结识重要人脉/贵人", "Met important mentor / key contact", "positive", lcu=18),
    LifeEvent("interpersonal", "adulthood", "被信任的人利用", "Used by someone trusted", "negative", lcu=35, diagnosis_relation={"depressive": "trigger", "anxiety": "trigger"}),

    # ---- 中老年 ----
    LifeEvent("interpersonal", "mid_older", "老友相聚", "Gathered with old friends", "positive", lcu=18),
    LifeEvent("interpersonal", "mid_older", "好友/同龄人去世", "Friend / peer passed away", "negative", lcu=37),
    LifeEvent("interpersonal", "mid_older", "与邻居关系融洽", "Good relationship with neighbors", "positive", lcu=15),
    LifeEvent("interpersonal", "mid_older", "社会活动参与少/孤独", "Low social participation / loneliness", "negative", lcu=29),
    LifeEvent("interpersonal", "mid_older", "与老友保持联系", "Kept in touch with old friends", "positive", lcu=15),
    LifeEvent("interpersonal", "mid_older", "子女移民/远走", "Child emigrated / moved far away", "negative", lcu=29),
]


# =====================================================================
# 统计信息
# =====================================================================

def count_events() -> dict:
    """统计事件分布

    包含基本统计 + LCU 汇总 + ACEs 统计
    """
    result = {
        "total": len(LIFE_EVENTS),
        "by_domain": {},
        "by_canonical_domain": {},
        "by_stage": {},
        "by_valence": {},
        "lcu_stats": {
            "min": min(e.lcu for e in LIFE_EVENTS),
            "max": max(e.lcu for e in LIFE_EVENTS),
            "mean": round(sum(e.lcu for e in LIFE_EVENTS) / len(LIFE_EVENTS), 1),
            "total_lcu_if_all": sum(e.lcu for e in LIFE_EVENTS),
        },
        "aces_event_count": _count_aces_events(),
    }
    for e in LIFE_EVENTS:
        result["by_domain"][e.domain] = result["by_domain"].get(e.domain, 0) + 1
        cd = e.canonical_domain
        if cd is not None:
            result["by_canonical_domain"][cd] = result["by_canonical_domain"].get(cd, 0) + 1
        result["by_stage"][e.stage] = result["by_stage"].get(e.stage, 0) + 1
        result["by_valence"][e.valence] = result["by_valence"].get(e.valence, 0) + 1
    return result


# =====================================================================
# 事件采样逻辑
# =====================================================================

DOMAIN_CN = {
    "family": "家庭",
    "education": "教育",
    "occupation": "职业",
    "health": "健康",
    "finance": "经济",
    "interpersonal": "人际",
}

STAGE_CN = {
    "childhood": "童年",
    "adolescence": "青少年",
    "adulthood": "成年",
    "mid_older": "中老年",
}


def get_events_by_domain_stage(domain: str, stage: str) -> list[LifeEvent]:
    """按领域和阶段筛选事件"""
    return [e for e in LIFE_EVENTS if e.domain == domain and e.stage == stage]


def get_events_by_diagnosis(diagnosis_key: str, relation: str | None = None
                            ) -> list[LifeEvent]:
    """按诊断关联筛选事件
    
    Args:
        diagnosis_key: 诊断键（如 "depressive"）
        relation: 可选过滤 "trigger" / "maintain" / "unrelated"
    """
    result = []
    for e in LIFE_EVENTS:
        if e.diagnosis_relation and diagnosis_key in e.diagnosis_relation:
            if relation is None or e.diagnosis_relation[diagnosis_key] == relation:
                result.append(e)
    return result


def sample_events_for_persona(
    age: int,
    primary_diagnosis_key: str | None = None,
    comorbidity_keys: list[str] | None = None,
    positive_ratio: float = 0.3,
    negative_ratio: float = 0.4,
    neutral_ratio: float = 0.3,
    n_events: int = 6,
    rng: random.Random = random.Random(),
    lcu_bias: float = 0.3,
) -> list[LifeEvent]:
    """为 persona 采样生活事件（支持 LCU 加权）

    Args:
        age: 当前年龄
        primary_diagnosis_key: 主诊断键（用于抽取关联事件）
        comorbidity_keys: 共病键列表
        positive_ratio: 积极事件比例
        negative_ratio: 消极事件比例
        neutral_ratio: 中性事件比例
        n_events: 需要的事件数量
        rng: 随机数生成器
        lcu_bias: LCU 权重偏好强度 (0.0~1.0)，越高越倾向高压力事件

    Returns:
        采样的事件列表（按时间顺序排序）
    """
    # 确定可用的人生阶段
    available_stages = set()
    if age >= 0: available_stages.add("childhood")
    if age >= 13: available_stages.add("adolescence")
    if age >= 18: available_stages.add("adulthood")
    if age >= 41: available_stages.add("mid_older")

    # 收集候选事件
    candidates: list[LifeEvent] = []
    for e in LIFE_EVENTS:
        if e.stage in available_stages:
            candidates.append(e)

    # 如果有诊断，优先抽取诊断关联事件（1-2 个）
    diagnosis_events: list[LifeEvent] = []
    all_keys = []
    if primary_diagnosis_key:
        all_keys.append(primary_diagnosis_key)
    if comorbidity_keys:
        all_keys.extend(comorbidity_keys)

    for key in all_keys:
        trigger_events = get_events_by_diagnosis(key, "trigger")
        diagnosis_events.extend(trigger_events)
        maintain_events = get_events_by_diagnosis(key, "maintain")
        diagnosis_events.extend(maintain_events)

    # 去重
    seen_ids = set()
    unique_diag_events = []
    for e in diagnosis_events:
        if e.name_cn not in seen_ids and e.stage in available_stages:
            seen_ids.add(e.name_cn)
            unique_diag_events.append(e)

    # 选 1-2 个诊断关联事件（优先高 LCU；无放回，避免重复事件）
    n_diag = min(rng.randint(1, 2), len(unique_diag_events), max(0, n_events))
    if n_diag > 0 and lcu_bias > 0:
        diag_pool = list(unique_diag_events)
        selected = []
        for _ in range(n_diag):
            weights = [max(0.1, 1.0 + lcu_bias * (e.lcu - 50) / 50) for e in diag_pool]
            idx = rng.choices(range(len(diag_pool)), weights=weights, k=1)[0]
            selected.append(diag_pool.pop(idx))
    else:
        selected = rng.sample(unique_diag_events, n_diag) if n_diag > 0 else []

    # 从通用事件中补足
    general_events = [e for e in candidates if e not in selected]
    remaining = max(0, n_events - len(selected))

    if remaining > 0:
        # 按效价比例分层采样。配额必须非负且总和精确等于 remaining。
        ratios = [
            max(0.0, float(positive_ratio)),
            max(0.0, float(negative_ratio)),
            max(0.0, float(neutral_ratio)),
        ]
        ratio_sum = sum(ratios)
        if ratio_sum <= 0:
            ratios = [1.0, 1.0, 1.0]
            ratio_sum = 3.0

        raw = [remaining * r / ratio_sum for r in ratios]
        counts = [int(x) for x in raw]
        for idx in sorted(
            range(3),
            key=lambda i: (raw[i] - counts[i], ratios[i]),
            reverse=True,
        )[: remaining - sum(counts)]:
            counts[idx] += 1
        n_pos, n_neg, n_neu = counts

        pos_pool = [e for e in general_events if e.valence == "positive" and e.name_cn not in seen_ids]
        neg_pool = [e for e in general_events if e.valence == "negative" and e.name_cn not in seen_ids]
        neu_pool = [e for e in general_events if e.valence == "neutral" and e.name_cn not in seen_ids]

        def weighted_sample(pool, n, bias=lcu_bias):
            n = max(0, min(int(n), len(pool)))
            if not pool or n <= 0:
                return []
            if bias > 0 and any(e.valence == "negative" for e in pool):
                available = list(pool)
                result = []
                for _ in range(n):
                    weights = [max(0.1, 1.0 + bias * (e.lcu - 50) / 50) for e in available]
                    idx = rng.choices(range(len(available)), weights=weights, k=1)[0]
                    result.append(available.pop(idx))
                return result
            return rng.sample(pool, n)

        selected.extend(weighted_sample(pos_pool, n_pos))
        selected.extend(weighted_sample(neg_pool, n_neg, lcu_bias))
        selected.extend(weighted_sample(neu_pool, n_neu))

        # 如果还不够，从所有剩余中补充
        if len(selected) < n_events:
            extra = [e for e in general_events if e not in selected]
            rng.shuffle(extra)
            selected.extend(extra[:n_events - len(selected)])

    return selected


def format_events_timeline(events: list[LifeEvent]) -> str:
    """将事件列表格式化为可读的时间线"""
    stage_order = ["childhood", "adolescence", "adulthood", "mid_older"]
    current_stage = ""
    lines = []
    for e in sorted(events, key=lambda x: stage_order.index(x.stage)):
        if e.stage != current_stage:
            current_stage = e.stage
            lines.append(f"\n【{STAGE_CN.get(e.stage, e.stage)}】")
        valence_mark = {"positive": "✓", "negative": "✗", "neutral": "●"}.get(e.valence, "●")
        lines.append(f"  {valence_mark} {e.name_cn}")
    return "\n".join(lines)


# =====================================================================
# NEW IN v2 - ACEs 计算、LCU 汇总、增强统计
# =====================================================================

# ACEs 10 类别映射（基于 Felitti et al. 1998）
ACES_CATEGORIES: dict[str, dict] = {
    "情感虐待": {
        "key": "emotional_abuse",
        "description": "在家庭中经常被辱骂、贬低、恐吓",
        "match": lambda e: e.domain == "family" and e.stage == "childhood"
                           and any(kw in e.name_cn for kw in ["父母严厉", "体罚", "父母离异"]),
    },
    "身体虐待": {
        "key": "physical_abuse",
        "description": "被父母或照顾者殴打、伤害",
        "match": lambda e: e.domain == "family" and e.stage == "childhood"
                           and "体罚" in e.name_cn,
    },
    "性虐待": {
        "key": "sexual_abuse",
        "description": "童年期遭遇性侵犯或性骚扰",
        "match": lambda e: False,  # 模板库未包含显式性虐待事件
    },
    "情感忽视": {
        "key": "emotional_neglect",
        "description": "情感需求长期得不到满足",
        "match": lambda e: e.domain == "family" and e.stage == "childhood"
                           and any(kw in e.name_cn for kw in ["父母长期在外务工", "被收养"]),
    },
    "身体忽视": {
        "key": "physical_neglect",
        "description": "基本生活需求得不到满足",
        "match": lambda e: e.domain in ("family", "finance") and e.stage == "childhood"
                           and ("家庭经济困难" in e.name_cn or "因贫困" in e.name_cn),
    },
    "父母离异或分居": {
        "key": "parental_separation",
        "description": "父母离异或分居",
        "match": lambda e: e.domain == "family" and e.stage == "childhood"
                           and "父母离异" in e.name_cn,
    },
    "母亲受虐": {
        "key": "mother_abused",
        "description": "母亲被虐待",
        "match": lambda e: False,
    },
    "家人物质滥用": {
        "key": "household_substance_abuse",
        "description": "家庭成员有物质滥用问题",
        "match": lambda e: False,
    },
    "家人心理疾病": {
        "key": "household_mental_illness",
        "description": "家庭成员患有严重心理疾病",
        "match": lambda e: False,
    },
    "家人服刑": {
        "key": "household_incarceration",
        "description": "家庭成员入狱服刑",
        "match": lambda e: False,
    },
}


def _count_aces_events() -> dict[str, int]:
    """统计各 ACEs 类别在事件模板中匹配的事件数"""
    counts: dict[str, int] = {}
    for cat_name, cat_info in ACES_CATEGORIES.items():
        count = sum(1 for e in LIFE_EVENTS if cat_info["match"](e))
        counts[cat_name] = count
    return counts


def calculate_aces(events: list[LifeEvent]) -> tuple[int, list[str]]:
    """计算童年逆境经历(ACEs)得分

    根据 Felitti et al. (1998) 的 ACEs 分类体系，
    检查童年期(0-12岁)是否有对应逆境事件。

    Returns:
        (aces_score, triggered_categories)
        aces_score: 0-10 的 ACEs 分数
        triggered_categories: 触发的 ACEs 类别列表（中文名）
    """
    childhood_events = [e for e in events if e.stage == "childhood"]
    triggered: list[str] = []

    for cat_name, cat_info in ACES_CATEGORIES.items():
        if any(cat_info["match"](e) for e in childhood_events):
            triggered.append(cat_name)

    return len(triggered), triggered


def compute_lcu_summary(events: list[LifeEvent]) -> dict:
    """计算给定事件列表的 LCU 汇总统计

    Returns:
        {
            "total_lcu": 总 LCU,
            "mean_lcu": 平均 LCU,
            "max_lcu": 最大 LCU,
            "min_lcu": 最小 LCU,
            "high_stress_count": LCU >= 60 的事件数,
            "moderate_stress_count": 40 <= LCU < 60 的事件数,
            "low_stress_count": LCU < 40 的事件数,
        }
    """
    if not events:
        return {
            "total_lcu": 0, "mean_lcu": 0.0, "max_lcu": 0, "min_lcu": 0,
            "high_stress_count": 0, "moderate_stress_count": 0, "low_stress_count": 0,
        }

    lcu_values = [e.lcu for e in events]
    return {
        "total_lcu": sum(lcu_values),
        "mean_lcu": round(sum(lcu_values) / len(lcu_values), 1),
        "max_lcu": max(lcu_values),
        "min_lcu": min(lcu_values),
        "high_stress_count": sum(1 for v in lcu_values if v >= 60),
        "moderate_stress_count": sum(1 for v in lcu_values if 40 <= v < 60),
        "low_stress_count": sum(1 for v in lcu_values if v < 40),
    }


def format_events_timeline_with_lcu(events: list[LifeEvent]) -> str:
    """将事件列表格式化为时间线（含 LCU 权重）"""
    stage_order = ["childhood", "adolescence", "adulthood", "mid_older"]
    current_stage = ""
    lines = []
    for e in sorted(events, key=lambda x: stage_order.index(x.stage)):
        if e.stage != current_stage:
            current_stage = e.stage
            lines.append(f"\n【{STAGE_CN.get(e.stage, e.stage)}】")
        valence_mark = {"positive": "✓", "negative": "✗", "neutral": "●"}.get(e.valence, "●")
        stress_label = ""
        if e.lcu >= 60:
            stress_label = " [高压力]"
        elif e.lcu >= 40:
            stress_label = " [中等压力]"
        else:
            stress_label = " [低压力]"
        lines.append(f"  {valence_mark} {e.name_cn} (LCU={e.lcu}{stress_label})")
    return "\n".join(lines)


# =====================================================================
# v2 理论增强模块
# =====================================================================

# =====================================================================
# 1. SRRS 参考表 — Holmes & Rahe (1967) 原始 LCU 标定
# 用于验证模板库中 LCU 赋值的合理性
# =====================================================================

# 以下为 Holmes & Rahe 原始 SRRS 中的 43 个生活事件及其 LCU（部分条目经后续修订）
# 数据库中同类事件的 LCU 应基于此赋值的性参考
SRRS_REFERENCE: dict[str, int] = {
    # ---- 家庭领域 ----
    "配偶去世": 100,
    "离婚": 73,
    "分居": 65,
    "与伴侣和好": 45,
    "近亲去世": 63,
    "自己受伤或生病": 53,
    "结婚": 50,
    "怀孕": 40,
    "家庭新成员加入": 39,
    "子女离家": 29,
    "姻亲矛盾": 29,
    "配偶开始/停止工作": 26,
    "夫妻间争吵次数变化": 35,
    # ---- 职业领域 ----
    "被解雇": 47,
    "退休": 45,
    "工作性质重大改变": 39,
    "工作职责重大改变": 29,
    "与上司矛盾": 23,
    # ---- 经济领域 ----
    "财务状况重大变化": 38,
    "抵押/贷款超过$10k": 31,
    "抵押/贷款被收回": 30,
    # ---- 教育/人际 ----
    "个人成就": 28,
    "开始或结束学业": 26,
    "开始或结束工作": 26,
    "生活条件重大改变": 25,
    "个人习惯重大改变": 24,
    "搬家": 20,
    "转学": 20,
    "休闲方式重大改变": 19,
    "宗教活动重大改变": 19,
    "社交活动重大改变": 18,
    "睡眠习惯重大改变": 16,
    "饮食习惯重大改变": 15,
    "假期": 13,
    "节日": 12,
    "轻微违法": 11,
}

# 事件类型 → SRRS 关键参考类别（用于后续诊断关联分析）
EVENT_TYPE_SRRS_MAP: dict[str, str] = {
    # 丧失类事件 (Loss) — Brown & Harris 强调抑郁触发
    "配偶去世": "loss", "近亲去世": "loss", "父母去世": "loss",
    "兄弟姐妹去世": "loss", "好友去世": "loss", "失去父亲或母亲": "loss",
    "父母离异": "loss", "家庭重组": "loss", "离家出走": "loss",
    "离婚": "loss_relational", "失恋": "loss_relational",
    "分手": "loss_relational", "分居": "loss_relational",
    "失业": "loss_economic", "被裁员": "loss_economic",
    "被骗": "loss_economic", "投资失败": "loss_economic",
    "被利用": "loss_economic", "欠债": "loss_economic",
    "被裁": "loss_economic",
    # 威胁类事件 (Danger) — Finlay-Jones & Brown 强调焦虑触发
    "霸凌": "danger", "有特殊需求": "danger",
    "被网暴": "danger", "遭受暴力": "danger", "性侵犯": "danger",
    "车祸": "danger", "被威胁": "danger", "自然灾害": "danger",
    "伤害": "danger", "歧视": "danger", "性骚扰": "danger",
    "排挤": "danger", "人际冲突": "danger",
    # 羞辱类事件 (Humiliation) — Kendler 强调抑郁触发
    "被排斥": "humiliation", "被贬低": "humiliation",
    "公开出丑": "humiliation", "被拒绝": "humiliation",
    "被不公平对待": "humiliation",
    # 陷阱类事件 (Entrapment) — 持续低强度压力
    "长期照顾": "entrapment", "慢性": "entrapment",
    "矛盾": "entrapment", "平衡困难": "entrapment",
    "经济困难": "entrapment", "经济拮据": "entrapment",
    "因病无法工作": "entrapment", "被经济啃老": "entrapment",
    "长期单身": "entrapment", "独生子女": "entrapment",
    "长期异地": "entrapment", "空巢": "entrapment",
    "与成年子女同住": "entrapment", "与邻居关系": "entrapment",
    "养老金不足": "entrapment",
    "子女移民": "entrapment",
    "失去父亲或母": "loss",
    # 积极事件
    "结婚": "positive", "升职": "positive", "生育": "positive",
    "升学": "positive", "获奖": "positive", "得奖": "positive",
    "成功": "positive", "获得": "positive", "优异": "positive",
    "表扬": "positive", "成就": "positive", "稳定": "positive",
    "幸福": "positive", "和睦": "positive", "融洽": "positive",
    "自由": "positive", "独立": "positive",
    "康复": "positive", "恢复": "positive",
    "好友": "positive", "好友相聚": "positive",
    # 中性事件
    "转学": "neutral", "搬家": "neutral", "变迁": "neutral",
    "退休": "neutral", "返聘": "neutral",
}


def classify_event_type(event: "LifeEvent") -> str:
    """将生活事件分类为 Brown & Harris 类型体系

    Returns:
        "loss" / "danger" / "humiliation" / "entrapment" / "positive" / "neutral"
    """
    for keyword, event_type in EVENT_TYPE_SRRS_MAP.items():
        if keyword in event.name_cn:
            return event_type
    if event.valence == "positive":
        return "positive"
    if event.valence == "negative":
        return "entrapment"  # 未匹配的负性事件默认为"陷阱"
    return "neutral"


# =====================================================================
# 2. Brown & Harris (1978) 脆弱性因子模型
# =====================================================================

@dataclass
class VulnerabilityFactors:
    """Brown & Harris 脆弱性/保护性因子评估

    原始研究提出的四个脆弱性因子（缺乏亲信、多子女、无工作、早期丧母）
    可以作为生活事件与发病之间的"调节变量"（vulnerability-stress interaction）。
    """
    has_confidant: bool = True
    """有亲密/信任的倾诉对象（保护因子，降低抑郁风险）"""
    has_employment: bool = True
    """有稳定工作（保护因子，提供日常结构与社会角色）"""
    young_children_at_home: int = 0
    """家中 14 岁以下子女人数（≥3 = 脆弱因子）"""
    lost_mother_before_11: bool = False
    """11 岁前丧母（脆弱因子，Brown & Harris 发现最有力预测因子之一）"""
    social_support_network: str = "moderate"
    """社会支持网络：strong / moderate / weak"""


# 诊断脆弱性配置
DIAGNOSIS_VULNERABILITY: dict[str, dict] = {
    "depressive": {
        "need_confidant": True,          # 缺亲信时风险倍增
        "need_employment": True,         # 失业时风险倍增
        "lost_mother_multiplier": 2.5,   # 早期丧母风险倍率
        "events_to_trigger": 2,          # 多少件严重事件可触发抑郁发作
        "loss_sensitivity": 3.0,         # 丧失类事件敏感度（风险倍率）
    },
    "dysthymia": {
        "need_confidant": True,
        "need_employment": True,
        "lost_mother_multiplier": 2.0,
        "events_to_trigger": 4,
        "loss_sensitivity": 1.5,
    },
    "anxiety": {
        "need_confidant": True,
        "need_employment": False,
        "lost_mother_multiplier": 1.8,
        "events_to_trigger": 3,
        "danger_sensitivity": 2.5,       # 威胁类事件敏感度
    },
    "panic": {
        "need_confidant": True,
        "need_employment": False,
        "lost_mother_multiplier": 2.0,
        "events_to_trigger": 2,
        "danger_sensitivity": 3.0,
    },
    "social_anxiety": {
        "need_confidant": True,
        "need_employment": True,
        "lost_mother_multiplier": 1.5,
        "events_to_trigger": 3,
        "humiliation_sensitivity": 3.5,  # 羞辱类事件极度敏感
    },
    "ptsd": {
        "need_confidant": True,
        "need_employment": True,
        "lost_mother_multiplier": 2.5,
        "events_to_trigger": 1,          # 单次创伤即可触发
        "trauma_sensitivity": 4.0,       # 创伤事件极度敏感
    },
    "adjustment": {
        "need_confidant": True,
        "need_employment": True,
        "lost_mother_multiplier": 1.3,
        "events_to_trigger": 1,
        "general_sensitivity": 1.5,
    },
    "ocd": {
        "need_confidant": False,
        "need_employment": False,
        "lost_mother_multiplier": 1.2,
        "events_to_trigger": 3,
        "contamination_sensitivity": 2.0,
    },
    "schizophrenia": {
        "need_confidant": True,
        "need_employment": True,
        "lost_mother_multiplier": 2.0,
        "events_to_trigger": 1,
        "stress_sensitivity": 3.0,      # 一般性应激敏感（stress-vulnerability model）
    },
    "borderline_pd": {
        "need_confidant": True,
        "need_employment": False,
        "lost_mother_multiplier": 3.0,
        "events_to_trigger": 2,
        "abandonment_sensitivity": 3.5,
    },
    "antisocial_pd": {
        "need_confidant": False,
        "need_employment": False,
        "lost_mother_multiplier": 2.0,
        "events_to_trigger": 4,          # 对一般生活事件不敏感
        "frustration_sensitivity": 2.0,
    },
    "substance": {
        "need_confidant": True,
        "need_employment": True,
        "lost_mother_multiplier": 2.0,
        "events_to_trigger": 2,
        "relapse_sensitivity": 2.5,      # 触发复发
    },
    "healthy": {
        "need_confidant": False,
        "need_employment": False,
        "lost_mother_multiplier": 1.0,
        "events_to_trigger": 100,        # 几乎不会应激致病
        "resilience": True,
    },
}

for key in ["bipolar_manic", "bipolar_dep", "cyclothymia", "agoraphobia",
            "hoarding", "body_dysmorphic", "schizotypal", "delusional",
            "adhd", "asd", "intellectual", "tic_disorder",
            "alcohol", "gambling", "anorexia", "bulimia", "binge",
            "narcissistic_pd", "avoidant_pd", "dependent_pd", "obsessive_pd",
            "somatic_symptom", "dissociative", "insomnia"]:
    if key not in DIAGNOSIS_VULNERABILITY:
        DIAGNOSIS_VULNERABILITY[key] = {
            "need_confidant": True,
            "need_employment": False,
            "lost_mother_multiplier": 1.5,
            "events_to_trigger": 3,
            "stress_sensitivity": 2.0,
        }


def evaluate_vulnerability(
    vulnerability: VulnerabilityFactors,
    diagnosis_key: str | None = None,
) -> dict:
    """评估脆弱性因子组合对发病风险的影响

    基于 Brown & Harris 原始模型的四因子交互作用：

    脆弱因子组合 → 风险分级：
    0 个脆弱因子: baseline risk
    1 个脆弱因子: 1.5x
    2 个脆弱因子: 2.5x
    3 个脆弱因子: 4.0x
    4 个脆弱因子: 6.0x+

    Args:
        vulnerability: 脆弱性因子评估对象
        diagnosis_key: 诊断键（用于调整系数）

    Returns:
        {
            "vulnerability_count": int,           激活的脆弱因子数
            "vulnerability_factors": list[str],   具体激活因子
            "risk_multiplier": float,             风险倍率
            "diagnosis_adjusted_multiplier": float,诊断调整后的风险倍率
        }
    """
    factors: list[str] = []
    if not vulnerability.has_confidant:
        factors.append("缺乏亲信倾诉对象")
    if not vulnerability.has_employment:
        factors.append("无稳定工作")
    if vulnerability.young_children_at_home >= 3:
        factors.append(f"{vulnerability.young_children_at_home}名14岁以下子女")
    if vulnerability.lost_mother_before_11:
        factors.append("11岁前丧母")

    n = len(factors)
    if n == 0:
        base_multiplier = 1.0
    elif n == 1:
        base_multiplier = 1.5
    elif n == 2:
        base_multiplier = 2.5
    elif n == 3:
        base_multiplier = 4.0
    else:
        base_multiplier = 6.0

    # 诊断调整
    diag_cfg = DIAGNOSIS_VULNERABILITY.get(diagnosis_key, {})
    lost_mother_mult = diag_cfg.get("lost_mother_multiplier", 1.0)
    if "11岁前丧母" in factors:
        diag_adjusted = base_multiplier * lost_mother_mult
    else:
        diag_adjusted = base_multiplier

    return {
        "vulnerability_count": n,
        "vulnerability_factors": factors,
        "risk_multiplier": round(base_multiplier, 2),
        "diagnosis_adjusted_multiplier": round(diag_adjusted, 2),
    }


# =====================================================================
# 3. ACEs 剂量-反应风险模型 — Felitti et al. (1998)
# =====================================================================

# ACEs 得分 → 各健康风险的 OR（来自 Felitti 原始论文）
ACES_DOSE_RESPONSE: dict[int, dict[str, float]] = {
    0: {
        "ischemic_heart_disease": 1.0, "cancer": 1.0,
        "stroke": 1.0, "diabetes": 1.0, "depression": 1.0,
        "suicide_attempt": 1.0, "substance_abuse": 1.0,
    },
    1: {
        "ischemic_heart_disease": 1.2, "cancer": 1.1,
        "stroke": 1.3, "diabetes": 1.1, "depression": 1.5,
        "suicide_attempt": 1.5, "substance_abuse": 1.5,
    },
    2: {
        "ischemic_heart_disease": 1.5, "cancer": 1.2,
        "stroke": 1.6, "diabetes": 1.3, "depression": 2.0,
        "suicide_attempt": 2.5, "substance_abuse": 2.0,
    },
    3: {
        "ischemic_heart_disease": 1.8, "cancer": 1.4,
        "stroke": 2.0, "diabetes": 1.5, "depression": 2.5,
        "suicide_attempt": 4.0, "substance_abuse": 2.5,
    },
    4: {
        "ischemic_heart_disease": 2.0, "cancer": 1.6,
        "stroke": 2.4, "diabetes": 1.6, "depression": 3.0,
        "suicide_attempt": 6.0, "substance_abuse": 3.5,
    },
    5: {
        "ischemic_heart_disease": 2.3, "cancer": 1.7,
        "stroke": 2.8, "diabetes": 1.7, "depression": 3.5,
        "suicide_attempt": 8.0, "substance_abuse": 4.5,
    },
    6: {
        "ischemic_heart_disease": 2.5, "cancer": 1.8,
        "stroke": 3.2, "diabetes": 1.8, "depression": 4.0,
        "suicide_attempt": 10.0, "substance_abuse": 5.0,
    },
}

# ACEs 得分的通用风险倍率（简化版，用于 persona 风险分层）
# 第 0 格 = EI（不存在隐含值），直接从 1 开始
ACES_RISK_TIERS: dict[int, float] = {
    0: 1.0,   # 无 ACEs
    1: 1.5,   # 低 ACEs
    2: 2.0,   # 中低
    3: 3.0,   # 中等
    4: 4.5,   # 高危（原始研究中 ACE≥4 风险陡升）
    5: 6.0,   # 高危
    6: 8.0,   # 极高
    7: 10.0,  # 极高
    8: 12.0,  # 极高
    9: 15.0,  # 极端
    10: 18.0, # 极端
}


def aces_risk_multiplier(aces_score: int) -> float:
    """获取 ACEs 得分的通用风险倍率

    基于 Felitti et al. 的剂量-反应发现：
    ACEs 每增加 1 分，多种身心疾病风险增加 1.2-2.0 倍。
    这里取保守的中位值，用于 persona 生成中的风险量化。
    """
    clamped = min(max(aces_score, 0), 10)
    return ACES_RISK_TIERS.get(clamped, 1.0)


def aces_condition_risk(aces_score: int, condition: str) -> float:
    """获取特定健康状况在给定 ACEs 得分下的 OR"""
    clamped = min(max(aces_score, 0), 6)
    row = ACES_DOSE_RESPONSE[clamped]
    return row.get(condition, 1.0)


# =====================================================================
# 4. Stress Generation 模型 — Hammen (1991)
# =====================================================================

# 某些诊断本身会"生成"更多负性生活事件（stress generation hypothesis）
# 这是精神病理学领域最重要的发现之一：抑郁、人格障碍患者不仅是
# 生活事件的被动受害者，还会主动（但无意识）制造更多压力事件。

STRESS_GENERATION_WEIGHTS: dict[str, float] = {
    # 强 stress generation 效应
    "depressive": 1.8,        # Hammen 原研究发现抑郁患者生成事件率 2-3x
    "dysthymia": 1.5,         # 慢性轻度抑郁也有明显效应
    "bipolar_manic": 2.0,     # 躁期冲动决策制造大量事件
    "bipolar_dep": 1.5,
    "borderline_pd": 2.5,     # 人际危机不断生成事件
    "antisocial_pd": 2.0,     # 违法行为和人际关系破裂
    "substance": 2.0,         # 物质使用导致的继发性生活事件
    "alcohol": 1.8,
    "gambling": 2.0,
    # 中等 stress generation 效应
    "anxiety": 1.3,
    "panic": 1.3,
    "ocd": 1.2,
    "anorexia": 1.3,
    "bulimia": 1.4,
    # 弱或无 stress generation 效应
    "ptsd": 1.1,
    "asd": 0.8,               # 自闭谱系倾向于社交孤立而非生成事件
    "social_anxiety": 0.9,    # 回避减少事件暴露，可能降低事件数
    "agoraphobia": 0.7,
    "healthy": 1.0,           # 基线
}


def stress_generation_multiplier(
    diagnosis_key: str | None,
    comorbidity_keys: list[str] | None = None,
) -> float:
    """计算 stress generation 总乘数

    主诊断与共病的乘数取最大值（hammen 模型提示主导诊断影响最大）
    """
    multipliers = []
    if diagnosis_key and diagnosis_key in STRESS_GENERATION_WEIGHTS:
        multipliers.append(STRESS_GENERATION_WEIGHTS[diagnosis_key])
    if comorbidity_keys:
        for key in comorbidity_keys:
            if key in STRESS_GENERATION_WEIGHTS:
                multipliers.append(STRESS_GENERATION_WEIGHTS[key])
    if not multipliers:
        return 1.0
    return max(multipliers)


# =====================================================================
# 5. 综合应激负荷评估
# =====================================================================

def assess_stress_burden(
    events: list[LifeEvent],
    vulnerability: VulnerabilityFactors | None = None,
    diagnosis_key: str | None = None,
    age: int = 30,
) -> dict:
    """综合应激负荷评估

    整合四个理论维度：
    1. LCU 累积负荷（Holmes & Rahe）
    2. ACEs 得分与剂量-反应风险（Felitti）
    3. Brown & Harris 脆弱性因子交互
    4. Stress generation 效应权重（Hammen）

    Returns:
        包含完整评估结果的字典
    """
    lcu_summary = compute_lcu_summary(events)
    aces_score, aces_categories = calculate_aces(events)
    aces_mult = aces_risk_multiplier(aces_score)

    # 脆弱性评估
    vuln_result = {
        "vulnerability_count": 0,
        "vulnerability_factors": [],
        "risk_multiplier": 1.0,
        "diagnosis_adjusted_multiplier": 1.0,
    }
    if vulnerability:
        vuln_result = evaluate_vulnerability(vulnerability, diagnosis_key)

    # Stress generation
    sg_mult = stress_generation_multiplier(diagnosis_key)

    # 事件类型分布
    event_types: dict[str, int] = {}
    for e in events:
        etype = classify_event_type(e)
        event_types[etype] = event_types.get(etype, 0) + 1

    # 诊断敏感度
    diag_cfg = DIAGNOSIS_VULNERABILITY.get(diagnosis_key, {})
    required_events = 2
    if isinstance(diag_cfg, dict):
        required_events = diag_cfg.get("events_to_trigger", 3)

    # 综合风险评分
    total_risk = lcu_summary["total_lcu"] * vuln_result["diagnosis_adjusted_multiplier"]
    total_risk *= sg_mult
    total_risk *= aces_mult

    # 触发事件判定
    trigger_events_count = sum(1 for e in events if e.diagnosis_relation
                               and diagnosis_key in e.diagnosis_relation
                               and e.diagnosis_relation[diagnosis_key] == "trigger")
    sufficient_triggers = trigger_events_count >= required_events

    # 风险分层
    lcu_ratio = total_risk / 300.0  # 归一化：以 300 LCU 为"高风险"基线
    if lcu_ratio >= 2.0:
        risk_stratum = "极高"
    elif lcu_ratio >= 1.3:
        risk_stratum = "高"
    elif lcu_ratio >= 0.8:
        risk_stratum = "中等"
    elif lcu_ratio >= 0.4:
        risk_stratum = "低"
    else:
        risk_stratum = "低"

    return {
        "lcu_summary": lcu_summary,
        "aces": {
            "score": aces_score,
            "categories": aces_categories,
            "risk_multiplier": aces_mult,
        },
        "vulnerability": vuln_result,
        "stress_generation_multiplier": sg_mult,
        "event_type_distribution": event_types,
        "diagnosis": {
            "key": diagnosis_key,
            "required_triggers": required_events,
            "actual_triggers": trigger_events_count,
            "sufficient_triggers": sufficient_triggers,
        },
        "composite": {
            "total_weighted_risk": round(total_risk, 1),
            "risk_stratum": risk_stratum,
            "normalized_risk_score": round(min(lcu_ratio, 5.0), 2),
            "interpretation": _interpret_stress_burden(
                aces_score, vuln_result["vulnerability_count"],
                lcu_summary["total_lcu"], risk_stratum
            ),
        },
    }


def _interpret_stress_burden(
    aces: int, vulnerability_count: int,
    total_lcu: int, stratum: str,
) -> str:
    """生成应激负荷的文字解读（用于 persona 生成中的叙述文本）"""
    interpretations = {
        "极高": (
            f"多重应激因素叠加：ACE 得分 {aces}（童年逆境风险极高），"
            f"脆弱因子 {vulnerability_count} 项，LCU 累积 {total_lcu}。"
            f"属于心理疾病发病极高风险群体，临床干预优先级高。"
        ),
        "高": (
            f"显著应激负荷：ACE 得分 {aces}，脆弱因子 {vulnerability_count} 项，"
            f"LCU 累积 {total_lcu}。有较高临床风险，建议关注早期预警信号。"
        ),
        "中等": (
            f"中等应激负荷：ACE 得分 {aces}，脆弱因子 {vulnerability_count} 项，"
            f"LCU 累积 {total_lcu}。在遇到额外压力源时可能突破阈值。"
        ),
        "低": (
            f"低应激负荷：ACE 得分 {aces}，脆弱因子 {vulnerability_count} 项，"
            f"LCU 累积 {total_lcu}。目前风险处于可控范围。"
        ),
    }
    return interpretations.get(stratum, "")


# =====================================================================
# 6. 事件类型加权—改进的采样函数增强
# =====================================================================

def event_type_sensitivity_weights(
    events: list[LifeEvent],
    diagnosis_key: str | None = None,
) -> list[float]:
    """根据事件类型和诊断敏感度计算采样权重

    使采样更倾向于对特定诊断有触发效应的事件。

    Args:
        events: 候选事件列表
        diagnosis_key: 诊断键

    Returns:
        与 events 等长的权重数组（用于加权采样）
    """
    if not diagnosis_key:
        return [1.0] * len(events)

    diag_cfg = DIAGNOSIS_VULNERABILITY.get(diagnosis_key, {})

    weights = []
    for e in events:
        w = 1.0
        # 诊断关联事件加权
        if e.diagnosis_relation and diagnosis_key in e.diagnosis_relation:
            w *= 3.0  # 关联事件 3x 权重

        # 事件类型敏感度
        etype = classify_event_type(e)
        if etype == "loss":
            w *= diag_cfg.get("loss_sensitivity", 1.0)
        elif etype == "danger":
            w *= diag_cfg.get("danger_sensitivity", 1.0)
        elif etype == "humiliation":
            w *= diag_cfg.get("humiliation_sensitivity", 1.0)

        # LCU 加权
        w *= (1.0 + (e.lcu - 50) / 100)
        weights.append(max(0.1, w))

    return weights
