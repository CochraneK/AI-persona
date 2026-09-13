"""
触发器和生理特征模块 — 症状触发器 + 安全行为 + 生理/隐藏经历

=========================================================================
与 Lajos Egri 三维理论的对应
=========================================================================
- 触发器系统 → Egri 心理维度的"压力反应"
- 隐藏经历 → Egri 社会维度的"秘密"
- 生理特征 → Egri 生理维度的细化
=========================================================================
"""

import random
from typing import Optional

# =====================================================================
# 症状触发器 & 安全行为
# 每个诊断对应的：什么情境会恶化症状 + 患者用什么样的行为来控制症状
# =====================================================================

TRIGGERS_AND_SAFETY: dict[str, dict] = {
    "depressive": {
        "triggers": [
            "夜里独处时回忆过去的失败",
            "被批评或被拒绝后",
            "看到别人幸福快乐的样子",
            "长期没有获得正面反馈",
            "阴雨天或秋冬季节交替",
            "结束一段亲密关系后",
            "节日期间感到孤独",
        ],
        "safety_behaviors": [
            "卧床不起，逃避社交",
            "反复确认自己是不是被讨厌了",
            "用睡眠逃避现实",
            "回避一切可能触景生情的场合",
            "拒绝回复消息、切断外界联系",
        ],
    },
    "dysthymia": {
        "triggers": [
            "感觉每天都是一样的乏味循环",
            "他人的好消息（对比下的落差）",
            "长期的高压工作环境",
            "缺乏社交支持网络",
        ],
        "safety_behaviors": [
            "机械地维持日常基本活动",
            "回避深入的人际交流",
            "用单调的日常规律麻痹自己",
        ],
    },
    "bipolar_manic": {
        "triggers": [
            "工作上的重大成功或表扬",
            "睡眠减少连续 2-3 天",
            "春季日照增加",
            "停止服用心境稳定剂",
            "高刺激环境（音乐会、夜店）",
        ],
        "safety_behaviors": [
            "强迫自己减少活动量（无效）",
            "靠焦虑感短暂压制兴奋",
            "身边的人试图限制其行为",
        ],
    },
    "bipolar_dep": {
        "triggers": [
            "认识到自己无法维持亢奋状态",
            "被批评躁狂期的行为",
            "处理躁狂期的财务/人际关系后果",
        ],
        "safety_behaviors": [
            "和躁狂期一样的退缩和孤立",
            "后悔和对过去行为的羞耻",
        ],
    },
    "anxiety": {
        "triggers": [
            "不确定性高的情境",
            "要做决定时",
            "截止日期临近",
            "身体出现不明确的症状",
            "收到意料之外的消息",
            "社交场合中成为焦点",
            "担心家人安全而联系不上",
        ],
        "safety_behaviors": [
            "反复检查确认",
            "过度准备和预演",
            "寻求反复的保证",
            "回避不确定的情境",
            "制定多个备用计划",
        ],
    },
    "panic": {
        "triggers": [
            "拥挤的公共交通",
            "封闭空间（电梯、隧道）",
            "独自离家很远的地方",
            "高强度运动后心跳加速",
            "咖啡因或刺激性物质",
            "回忆上次发作的场景",
        ],
        "safety_behaviors": [
            "随身携带安定药物",
            "确保了解最近的医院位置",
            "避免独自外出",
            "离家时告知他人自己的行踪",
            "回避公共交通",
        ],
    },
    "social_anxiety": {
        "triggers": [
            "被要求公开发言或自我介绍",
            "被注视（排队、吃饭、走路）",
            "需要打电话（尤其是陌生人）",
            "不得不参加社交聚会",
            "犯了小错觉得所有人都在看",
            "被拍照或录像",
            "被突然点名发言",
        ],
        "safety_behaviors": [
            "提前准备逐字稿或台词",
            "社交前饮酒/服药",
            "选择角落或边缘位置",
            "避免眼神接触",
            "快速结束对话的退出策略",
            "尽可能不引人注目地穿着",
        ],
    },
    "agoraphobia": {
        "triggers": [
            "离开家去不熟悉的地方",
            "排队或拥挤场合",
            "独自在桥上或隧道中",
            "坐公共交通工具",
            "人多的大型商场或超市",
        ],
        "safety_behaviors": [
            "只去熟悉的地点",
            "必须有信任的人陪同",
            "确认所有出口的位置",
            "携带紧急联系方式",
            "避免离家太远",
        ],
    },
    "ptsd": {
        "triggers": [
            "与创伤相关的感官刺激（声音/气味/画面/触感）",
            "特定日期或地点",
            "突然的身体接触",
            "类似创伤事件场景的影视作品",
            "冲突或争吵中的高亢语气",
            "睡眠中的噩梦内容",
            "受限制的空间或姿势",
        ],
        "safety_behaviors": [
            "避免去与创伤相关的地点",
            "确保身体有足够的周围空间",
            "背对墙壁而坐以便观察",
            "携带自卫工具",
            "过度警觉地扫描环境",
            "回避暴力相关的影视内容",
        ],
    },
    "adjustment": {
        "triggers": [
            "生活环境的突然改变",
            "失去重要的关系或工作",
            "搬迁到新的城市",
            "学业或职业的重大转折",
        ],
        "safety_behaviors": [
            "试图维持旧的日常生活习惯",
            "频繁联系旧环境中的人",
            "回避适应新的环境",
        ],
    },
    "ocd": {
        "triggers": [
            "接触被认为「脏」的表面（门把手、扶手）",
            "不确定自己是否关好门窗/煤气",
            "脑子里出现「禁忌」的想法或画面",
            "物品摆放不对称",
            "看到数字或图案的不规律",
            "担心自己伤害了别人而不自知",
        ],
        "safety_behaviors": [
            "反复洗手或清洁",
            "重复检查开关和锁",
            "按固定顺序摆放物品",
            "在心里计数或重复特定短语",
            "回避触碰「脏」的物体",
            "仪式化行为以「抵消」坏念头",
        ],
    },
    "hoarding": {
        "triggers": [
            "看到有用的东西被丢弃",
            "促销/打折物品",
            "收到的信件和邮件积压",
            "家人试图清理空间",
        ],
        "safety_behaviors": [
            "收集和囤积物品",
            "拒绝别人触碰自己的物品",
            "为每一件物品找到「将来可能会用」的理由",
        ],
    },
    "body_dysmorphic": {
        "triggers": [
            "照镜子或看到自己的照片",
            "被别人注视",
            "反射表面（车窗、玻璃）",
            "比较自己与他人的外表",
        ],
        "safety_behaviors": [
            "反复照镜子检查",
            "用衣物或化妆遮盖",
            "回避拍照",
            "过度修饰或寻求美容手术",
            "避免社交活动",
        ],
    },
    "schizophrenia": {
        "triggers": [
            "睡眠严重不足",
            "高压力或冲突情境",
            "停用抗精神病药物",
            "大麻等精神活性物质",
            "孤立的独处时间过长",
            "缺乏结构的生活节奏",
        ],
        "safety_behaviors": [
            "信任特定的家人或医生",
            "维持固定的日常时间表",
            "用耳机听音乐隔绝声音",
            "回避人群和公共场合",
            "记录症状以监控病情变化",
        ],
    },
    "schizotypal": {
        "triggers": [
            "被迫在社交场合中伪装正常",
            "自己的奇特想法被否定或质疑",
            "长期被孤立或排挤",
        ],
        "safety_behaviors": [
            "减少社交以维持内心平衡",
            "沉浸在自己的兴趣和独特信念中",
            "保持与少数理解自己的人的交流",
        ],
    },
    "delusional": {
        "triggers": [
            "感受到被跟踪或被监控的迹象",
            "发现「证据」支持自己的猜测",
            "被亲近的人劝诫去看医生",
        ],
        "safety_behaviors": [
            "加强自我保护（锁门、检查）",
            "减少与他人的信任",
            "记录「证据」以证明自己的判断",
        ],
    },
    "adhd": {
        "triggers": [
            "需要长时间集中注意力的任务",
            "枯燥重复的工作流程",
            "多任务并行但每件都很紧急",
            "社交互动（无法追踪对话）",
            "需要守时的重要场合",
        ],
        "safety_behaviors": [
            "设置多个闹钟和提醒",
            "拖延到最后一刻才行动",
            "使用番茄工作法或分段完成任务",
            "经常变换任务以减少无聊",
            "依赖他人帮助组织和提醒",
        ],
    },
    "asd": {
        "triggers": [
            "日常生活规律被打破",
            "感官过载（太亮/太吵/多人同时说话）",
            "社交中突然被要求做出反应",
            "被触碰或过于靠近的身体距离",
            "计划外的变更和意外情况",
            "多人交谈中的社交信息过载",
        ],
        "safety_behaviors": [
            "严格遵守固定的日程和路线",
            "在刺激过载时关闭感官（捂耳朵/看别处/逃离）",
            "准备应对社交场景的脚本",
            "专注在特定的兴趣领域获得安慰",
            "使用耳机/墨镜作为感官过滤器",
        ],
    },
    "substance": {
        "triggers": [
            "看到或闻到熟悉的物质",
            "和之前一起使用的人在一起",
            "情绪低落或压力大时",
            "晚上独处时",
            "处于过去使用的环境",
        ],
        "safety_behaviors": [
            "更换社交圈和活动地点",
            "避免路过熟悉的购买点",
            "用其他活动填补空隙时间",
            "依赖戒断支持群体",
        ],
    },
    "alcohol": {
        "triggers": [
            "社交应酬场合",
            "下班后的习惯性饮酒时间",
            "情绪低落或人际关系冲突",
            "看到酒类广告或走进超市酒区",
        ],
        "safety_behaviors": [
            "选择无酒精餐厅和活动",
            "告诉身边人自己在戒酒",
            "避免晚间独处",
            "用运动和嗜好转移注意力",
        ],
    },
    "gambling": {
        "triggers": [
            "手头有一笔闲钱",
            "看到体育赛事或博彩广告",
            "生活中感到疏离或压力",
            "看到别人赢钱的消息",
            "欠债后想要翻盘的冲动",
        ],
        "safety_behaviors": [
            "将财务控制权交给家人",
            "屏蔽博彩网站和应用",
            "参加戒赌互助会",
            "设定消费限额自动提醒",
        ],
    },
    "anorexia": {
        "triggers": [
            "称体重或量体围",
            "看到镜中的自己",
            "在社交媒体上看到「完美身材」",
            "被评论外貌或体重",
            "吃「禁忌」食品后",
        ],
        "safety_behaviors": [
            "严格控制进食量和食物种类",
            "过度运动以消耗热量",
            "饭后立即去卫生间",
            "穿宽松衣物掩盖体型",
            "回避称体重和量体的场合",
        ],
    },
    "bulimia": {
        "triggers": [
            "暴食冲动出现后",
            "吃了高热量食物后的自责",
            "情绪波动（特别是愤怒或孤独）",
            "社交场合中进食失控",
            "看到大量食物",
        ],
        "safety_behaviors": [
            "暴食后催吐",
            "使用泻药或利尿剂",
            "暴食后过度运动",
            "秘密囤积食物以备暴食",
            "回避涉及大量食物的社交",
        ],
    },
    "binge": {
        "triggers": [
            "独处时感到情绪空虚",
            "节食一段时间后的反弹",
            "压力大或情绪低落",
            "睡不着时",
        ],
        "safety_behaviors": [
            "清空家里的零食储备",
            "设定严格的进食时间表",
            "用其他嗜好替代进食冲动",
        ],
    },
    "borderline_pd": {
        "triggers": [
            "重要的人不回消息或语气冷淡",
            "感受到被拒绝或抛弃的信号",
            "与信任的人发生冲突",
            "感到无聊或被冷落",
            "被提醒过去被抛弃的创伤",
            "觉得自己不重要了",
        ],
        "safety_behaviors": [
            "冲动地联系对方（电话轰炸、反复发消息）",
            "自伤行为以宣泄情绪",
            "先发制人地结束关系",
            "用极端的情绪表达引起关注",
            "立即找新的人填补情感空缺",
        ],
    },
    "antisocial_pd": {
        "triggers": [
            "感到被控制或被约束",
            "被权威人物命令",
            "无聊和缺乏刺激",
            "看到比自己更成功或受人喜爱的人",
            "被揭穿谎言或欺骗",
        ],
        "safety_behaviors": [
            "操控或欺骗以重获控制",
            "转移目标到更容易得手的人",
            "将责任推给他人",
            "以攻击回应感知到的冒犯",
        ],
    },
    "narcissistic_pd": {
        "triggers": [
            "被批评或质疑能力",
            "不是关注的焦点",
            "别人的成就不如自己却获得更多认可",
            "被拒绝或忽视",
            "暴露了自己的缺点或失败",
        ],
        "safety_behaviors": [
            "贬低他人以维护自尊",
            "夸大自己的成就和能力",
            "回避可能暴露弱点的场景",
            "选择性地记住被肯定的事",
            "与欣赏自己的人保持关系",
        ],
    },
    "avoidant_pd": {
        "triggers": [
            "需要与陌生人建立关系",
            "被邀请参加社交活动",
            "在工作中需要团队合作",
            "感受到被评价的场合",
        ],
        "safety_behaviors": [
            "拒绝邀请以避免可能的尴尬",
            "在关系可能变得更近时主动疏远",
            "预设被拒绝然后放弃尝试",
            "保持低调避免引起注意",
        ],
    },
    "dependent_pd": {
        "triggers": [
            "需要独自做重要决定",
            "被依赖的人批评或表达不满",
            "感觉到被抛弃的风险",
            "面临生活方式的重大变化",
        ],
        "safety_behaviors": [
            "不停地寻求建议和确认",
            "为了维持关系而完全顺从",
            "迅速找到新的依赖对象",
            "回避需要独立做决定的情况",
        ],
    },
    "obsessive_pd": {
        "triggers": [
            "事情没有按计划进行",
            "被要求改变已经形成的习惯",
            "别人没有按照「正确」的方法做事",
            "时间紧迫无法充分准备",
        ],
        "safety_behaviors": [
            "要求自己或他人反复检查",
            "制定极其详细的计划",
            "拒绝改变和偏离既定流程",
            "批评和纠正他人的做法",
        ],
    },
    "somatic_symptom": {
        "triggers": [
            "身体感受到任何不寻常的信号",
            "看到健康相关的信息或节目",
            "听说别人得了重病",
            "常规检查结果有轻微异常",
        ],
        "safety_behaviors": [
            "反复去医院做检查",
            "在网上搜索自己的症状",
            "频繁测量身体指标（血压/体温等）",
            "更换医生以寻求不同意见",
            "避免某些活动「以防」加重病情",
        ],
    },
    "dissociative": {
        "triggers": [
            "被提醒或接触到创伤记忆",
            "与创伤相关的地点或人物",
            "高情绪唤醒的情境",
            "亲密关系中感到危险",
        ],
        "safety_behaviors": [
            "自动切换到「不在场」状态",
            "遗忘或模糊创伤细节",
            "用碎片化的自我应对不同情境",
        ],
    },
    "insomnia": {
        "triggers": [
            "担心今晚又要失眠",
            "就寝时间接近时的焦虑感",
            "白天不小心午睡了",
            "睡前摄入咖啡因或酒精",
            "卧室温度不适或噪音",
        ],
        "safety_behaviors": [
            "过早躺床上试图入睡",
            "频繁看时间计算还有多少睡眠时间",
            "使用安眠药或褪黑素",
            "玩手机直到累倒",
            "规律的助眠仪式",
        ],
    },
    "healthy": {
        "triggers": [
            "重大生活压力事件",
            "长期过劳或睡眠不足",
            "人际关系冲突",
            "身体健康出现问题",
        ],
        "safety_behaviors": [
            "与亲友倾诉",
            "运动或放松活动减压",
            "寻求专业帮助（如咨询）",
            "给自己时间和空间休息",
            "制订计划解决问题",
        ],
    },
}


# =====================================================================
# 生理特征模板
# 用于补充 Persona 的外貌描述
# =====================================================================

PHYSICAL_APPEARANCE_TEMPLATES: dict[str, dict[str, list[str]]] = {
    "tall": ["高大", "修长", "中等身材"],
    "short": ["娇小", "矮小", "中等身材"],
    "build_lean": ["偏瘦", "身材瘦削", "体格纤细"],
    "build_heavy": ["偏胖", "身材丰满", "体格壮实"],
    "build_muscular": ["肌肉结实", "体格强健", "身材匀称"],
    "build_average": ["中等身材", "体型匀称", "普通体格"],
    "face": [
        "圆脸", "方脸", "长脸", "瓜子脸",
        "五官端正", "面色苍白", "面色红润",
        "眉目清秀", "相貌普通", "面带倦容",
    ],
    "hair": [
        "黑短发", "长发", "灰白头发", "稀疏头发",
        "蓬松卷发", "直发", "板寸头",
    ],
    "eyes": [
        "眼神明亮", "目光躲闪", "眼神疲惫",
        "眼神锐利", "目光温和", "眼窝深陷",
        "眼神空洞", "眼睛有神",
    ],
    "expression": [
        "表情严肃", "面带微笑", "神情紧张",
        "脸色忧郁", "表情放松", "面无表情",
        "总是心事重重的样子", "平静从容",
    ],
    "posture": [
        "挺拔", "微微佝偻", "坐姿端正",
        "总靠着墙或桌子", "不安地变换姿势",
        "放松舒展", "肩膀下垂",
    ],
}

# 按性别微调
PHYSICAL_APPEARANCE_GENDER_MAP: dict[str, dict[str, list[str]]] = {
    "男": {
        "face": ["方脸", "国字脸", "棱角分明", "胡子拉碴", "清秀"],
        "hair": ["板寸", "短发", "光头", "中长发", "发际线高"],
        "build": ["魁梧", "瘦高", "啤酒肚", "精瘦", "健壮"],
    },
    "女": {
        "face": ["鹅蛋脸", "圆脸", "瓜子脸", "棱角分明", "温柔面容"],
        "hair": ["长发及肩", "短发", "马尾辫", "烫卷发", "盘发"],
        "build": ["纤细", "丰满", "娇小", "高挑", "匀称"],
    },
}


def sample_physical_appearance(
    gender: str,
    age: int,
    rng: random.Random = random.Random(),
    ocean: dict[str, int] | None = None,
) -> list[str]:
    """采样一组外貌描述关键词"""
    features = []

    # 身高体型
    height_pool = PHYSICAL_APPEARANCE_TEMPLATES.get("tall", []) + PHYSICAL_APPEARANCE_TEMPLATES.get("short", [])
    features.append(rng.choice(height_pool))

    # 体型（按年龄倾向）
    if age > 50:
        build = rng.choice(PHYSICAL_APPEARANCE_TEMPLATES["build_average"] + PHYSICAL_APPEARANCE_TEMPLATES["build_heavy"] + ["略有发福"])
    elif age < 25:
        build = rng.choice(PHYSICAL_APPEARANCE_TEMPLATES["build_lean"] + PHYSICAL_APPEARANCE_TEMPLATES["build_average"] + PHYSICAL_APPEARANCE_TEMPLATES["build_muscular"])
    else:
        build = rng.choice(PHYSICAL_APPEARANCE_TEMPLATES["build_average"] + PHYSICAL_APPEARANCE_TEMPLATES["build_lean"])
    features.append(build)

    # 性别微调
    gmap = PHYSICAL_APPEARANCE_GENDER_MAP.get(gender, {})
    if "face" in gmap:
        features.append(rng.choice(gmap["face"]))
    else:
        features.append(rng.choice(PHYSICAL_APPEARANCE_TEMPLATES["face"]))
    if "hair" in gmap:
        features.append(rng.choice(gmap["hair"]))
    else:
        features.append(rng.choice(PHYSICAL_APPEARANCE_TEMPLATES["hair"]))

    # 眼神
    features.append(rng.choice(PHYSICAL_APPEARANCE_TEMPLATES["eyes"]))

    # 表情（按年龄倾向）
    if age > 60:
        features.append(rng.choice(["面带风霜", "神情安详", "目光慈祥", "满脸皱纹但精神不错"]))
    else:
        features.append(rng.choice(PHYSICAL_APPEARANCE_TEMPLATES["expression"]))

    # 体态
    features.append(rng.choice(PHYSICAL_APPEARANCE_TEMPLATES["posture"]))

    # 约束: OCEAN→外貌 (约束13)
    if ocean is not None:
        from .cross_constraints import adjust_physical_appearance_by_ocean
        features = adjust_physical_appearance_by_ocean(features, ocean, rng)

    return features


# =====================================================================
# 隐藏经历
# 每个人物都有 1-2 个"当前隐瞒的事情"——临床中没人会主动暴露一切
# =====================================================================

HIDDEN_EXPERIENCES: dict[str, list[str]] = {
    "depressive": [
        "曾经尝试过自杀，但从未告诉任何人",
        "辞职的真实原因是抑郁发作，对外称「想换个环境」",
        "每天起床都需要巨大的心理挣扎，但对外掩饰得很好",
        "在社交媒体上装出正常的样子，实际上非常痛苦",
    ],
    "anxiety": [
        "会议中焦虑发作时用去洗手间作为借口",
        "其实经常偷偷用酒精来缓解社交焦虑",
        "简历上有半年空白期是因为焦虑无法工作",
        "跟医生隐瞒了真实症状的严重程度",
    ],
    "social_anxiety": [
        "为了避开一个社交活动，装病请假",
        "在洗手间里待了很久逃避聚会",
        "在路上远远看到熟人会绕道走",
        "点外卖是因为不想和店员说话",
    ],
    "ptsd": [
        "从未完整跟任何人讲述过创伤经历的全貌",
        "对某些特定的声音或气味有强烈的回避反应但不解释原因",
        "晚上做噩梦惊醒后从不告诉同住的人",
        "对某些日期格外敏感，但从不说明",
    ],
    "schizophrenia": [
        "在没人的时候也会听到声音，但告诉别人「一切都好」",
        "有一次因为觉得自己被监视而报了警，事后谎称误会",
        "偷偷减少了药量或停药因为不喜欢副作用",
        "保留了一本笔记记录「异常」的想法，从不让别人看",
    ],
    "borderline_pd": [
        "在关系好的时候其实极度害怕对方离开，但从不表现",
        "有过自伤行为，但在长袖衣服下藏得很好",
        "对自己说过的最难听的话从不对别人讲",
        "为了不被抛弃而压抑自己的真实感受",
    ],
    "ocd": [
        "上班路上有一块地砖没按习惯踩到，一整天都在想这件事",
        "睡前仪式如果没完成会偷偷起床重做",
        "从不和别人共用杯子或餐具",
        "反复检查门锁但从不告诉家人",
    ],
    "adhd": [
        "这个月的账单又忘记交了",
        "上次的承诺其实不是不想做，是忘了",
        "快速做完一个项目的原因只是越接近截止日期越兴奋",
        "手机里至少有 20 个没回的消息和邮件",
    ],
    "asd": [
        "社交后需要在黑暗安静的环境里独处至少半小时恢复",
        "总是在心里背诵社交礼仪但还是会说错话",
        "有些声音别人听不到但让自己非常烦躁",
        "多年的习惯因为一次改变而崩溃",
    ],
    "substance": [
        "告诉家人自己在「戒烟」，其实还在用别的",
        "用社交费用来购买物质",
        "偷偷保留了紧急情况下的「备用」",
    ],
    "anorexia": [
        "自称「吃过了」但其实还没吃",
        "会在别人不注意的时候把食物倒掉",
        "淋浴时用冷水冲洗以消耗热量",
        "在体重数据上撒谎",
    ],
    "psychotic": [
        "有时候不确定自己的想法到底是自己的还是别人植入的",
        "害怕精神科医生不相信自己说的某些事",
        "在公共场所出现幻觉后假装在接电话",
    ],
    "healthy": [
        "有时候也会感到孤独，但不认为这是需要就医的事",
        "曾经失眠过几周，自己调节好了",
        "有自己缓解压力的小嗜好没对别人说过",
    ],
}

# 通用的隐藏经历（不绑定診断）
GENERIC_HIDDEN = [
    "对家人隐瞒真正的收入状况",
    "有一段从未跟任何人提起过的感情经历",
    "有一个不为人知的业余爱好或特长",
    "在社交媒体上有一个匿名的账号",
    "暗中存了一笔应急金，谁也不知道",
    "青春期做过一件至今觉得丢脸的事",
    "对某个家人有愧疚感，但从没说过",
    "曾经欠过一笔钱，自己默默还清了",
    "有一个不为人知的职业梦想",
    "一直暗恋着某个人，从未表白",
    "对某个家庭成员有积怨但没有表达过",
    "曾经在网上做过匿名求助",
]


# =====================================================================
# 采样函数
# =====================================================================

def sample_triggers(diagnosis_key: str,
                     rng: random.Random = random.Random(),
                     n_triggers: int = 3,
                     ocean: dict[str, int] | None = None) -> list[str]:
    """采样症状触发器"""
    default = TRIGGERS_AND_SAFETY.get("healthy", {"triggers": []})
    entry = TRIGGERS_AND_SAFETY.get(diagnosis_key, default)
    pool = entry.get("triggers", [])
    result = rng.sample(pool, min(n_triggers, len(pool)))

    # 约束: OCEAN→触发器类型 (约束11)
    if ocean is not None:
        from .cross_constraints import adjust_triggers_by_ocean
        result = adjust_triggers_by_ocean(result, ocean, rng, n_triggers=n_triggers)

    return result


def sample_safety_behaviors(diagnosis_key: str,
                             rng: random.Random = random.Random(),
                             n_behaviors: int = 2,
                             ocean: dict[str, int] | None = None) -> list[str]:
    """采样安全行为"""
    default = TRIGGERS_AND_SAFETY.get("healthy", {"safety_behaviors": []})
    entry = TRIGGERS_AND_SAFETY.get(diagnosis_key, default)
    pool = entry.get("safety_behaviors", [])
    result = rng.sample(pool, min(n_behaviors, len(pool)))

    # 约束: OCEAN→安全行为 (约束12)
    if ocean is not None:
        from .cross_constraints import adjust_safety_behaviors_by_ocean
        result = adjust_safety_behaviors_by_ocean(result, ocean, rng, n_behaviors=n_behaviors)

    return result


def sample_hidden_experiences(diagnosis_key: str,
                               rng: random.Random = random.Random(),
                               n: int = 2,
                               ocean: dict[str, int] | None = None) -> list[str]:
    """采样隐藏经历（诊断相关 + 通用混合）"""
    result = []

    # 诊断相关的隐藏经历
    diag_pool = HIDDEN_EXPERIENCES.get(diagnosis_key, [])
    if diag_pool:
        n_diag = min(1, len(diag_pool))
        result.extend(rng.sample(diag_pool, n_diag))

    # 通用的隐藏经历
    remaining = n - len(result)
    if remaining > 0:
        generic_pool = [h for h in GENERIC_HIDDEN if h not in result]
        result.extend(rng.sample(generic_pool, min(remaining, len(generic_pool))))

    # 约束: OCEAN→隐藏经历 (约束14)
    if ocean is not None:
        from .cross_constraints import adjust_hidden_experiences_by_ocean
        result = adjust_hidden_experiences_by_ocean(result, ocean, rng, n=n)

    return result
