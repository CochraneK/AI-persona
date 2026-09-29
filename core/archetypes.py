"""Narrative archetype generation assets (legacy v1.2 compatibility).

Human Ontology v2 classification
=========================================================================
Archetypes live under personality_psychology.narrative_identity.

They are explicit story/persona-generation templates. They are NOT:
- clinical personality types;
- psychometric truth;
- diagnostic criteria;
- evidence that a diagnosis causes a particular wound, value, motive or life arc.

The original v1.2 library is preserved because it contains substantial authored
variation (wounds, desires, needs, values/social tone and OCEAN biases). Legacy
Persona generation may still select templates by diagnosis for backwards
compatibility. The v2 KernelGenerator places a semantic firewall around that
behavior: diagnosis-conditioned generation is isolated to the health domain by
default, while non-health identity is generated independently.

Design rules
------------------------------------------------------------------------
1. Archetype is narrative_identity, never the Person root.
2. Diagnosis-keyed sampling is legacy behavior, not an ontological relation.
3. OCEAN is a trait model and must not overwrite narrative identity.
4. Existing archetype content is retained during migration; future native-v2
   libraries should be diagnosis-neutral unless an explicit research design
   justifies a conditional prior with provenance.
5. Absence of an archetype must not make a person less richly represented.
"""

import random
from typing import Optional


# =====================================================================
# 人设元类型数据表
# =====================================================================
# 结构:
#   ARCHETYPES[diagnosis_key] = [archetype_dict, ...]
#
# archetype_dict 字段:
#   key                   : str   英文唯一键
#   name_cn               : str   中文型名
#   one_liner             : str   一句话描述（用于 system_prompt 与卡片）
#   weight                : float 采样权重（同一诊断内归一）（默认 1.0）
#   wounds                : list[str]   形成性创伤池（3-5 条，型专属）
#   compensatory_desires  : list[str]   补偿性欲望（2-3 条，型专属）
#   storr_needs           : list[str]   内在需要（2-3 条，型专属）
#   core_desire           : str   核心欲望（覆盖诊断默认）
#   core_fear             : str   核心恐惧（覆盖诊断默认）
#   values_tone           : dict  注入 values_beliefs 的基调字段
#   social_tone           : dict  注入 social_relations 的基调字段
#   ocean_bias            : dict  可选 OCEAN 偏置 {"N": +1, "E": -1, ...}
#   typical_arc           : str   可选，该型典型角色弧线倾向

ARCHETYPES: dict[str, list[dict]] = {

    # =================================================================
    # 抑郁障碍 — 5 型
    # =================================================================
    "depressive": [
        {
            "key": "hidden_sufferer",
            "name_cn": "隐忍承担型",
            "one_liner": "表面运转正常，独自消化痛苦，从不主动求助",
            "weight": 1.3,
            "wounds": [
                "从小被教育「自己的事自己扛」，求助被等同于软弱",
                "童年时情绪表达总被一句「别矫情」堵回去",
                "长期充当家庭里的情绪垃圾桶，却没人问过自己",
                "曾经示弱求助过一次，换来的是被轻视或指责",
            ],
            "compensatory_desires": [
                "拼命维持「我没事」的表象，把疲惫藏到别人看不见的地方",
                "用超额完成任务来证明自己没有垮掉",
            ],
            "storr_needs": [
                "学会承认脆弱不等于无能，允许自己被接住",
                "明白不需要先撑住全场，才有资格被关心",
            ],
            "core_desire": "被看见疲惫，却不必先开口解释",
            "core_fear": "一旦示弱就会失去仅剩的体面与他人的信任",
            "values_tone": {"moral_foundation": "责任/自律倾向", "core_values": ["可靠", "体面", "不麻烦别人"]},
            "social_tone": {"network_size": "小但稳定", "friends": "少数深交，报喜不报忧"},
            "ocean_bias": {"N": +1, "C": +1},
        },
        {
            "key": "self_blamer",
            "name_cn": "自我归咎型",
            "one_liner": "把一切不顺都归到自己身上，反复反刍「都是我的错」",
            "weight": 1.2,
            "wounds": [
                "长期被重要他人贬低——「你永远做不成任何事」",
                "成长中犯错总被上纲上线为人品问题，而非行为问题",
                "家庭变故时被暗示是自己的责任（如父母争吵怪孩子）",
                "多次努力尝试却反复失败，形成习得性无助",
            ],
            "compensatory_desires": [
                "通过过度自我检讨抢在别人指责自己之前先认错",
                "用完美的执行来避免任何可能被批评的缝隙",
            ],
            "storr_needs": [
                "区分「我做错了一件事」与「我这个人有问题」",
                "接受错误是信息而非判决",
            ],
            "core_desire": "被明确告知「这不是你的错」",
            "core_fear": "自己本质上就是有缺陷的、会连累所有人",
            "values_tone": {"moral_foundation": "权威/纯洁倾向", "core_values": ["自省", "不添乱", "守规矩"]},
            "social_tone": {"network_size": "非常小", "friends": "回避冲突，常先道歉"},
            "ocean_bias": {"N": +1, "A": +1},
        },
        {
            "key": "withdrawn_isolate",
            "name_cn": "隔绝退缩型",
            "one_liner": "把自己从关系里撤出，用孤独换取不再受伤",
            "weight": 1.0,
            "wounds": [
                "经历了被亲密伴侣背叛或抛弃",
                "青少年时期经历了重大失落（如父母离世/离异）",
                "曾经主动靠近他人，却被反复拒绝或利用",
                "童年时期长期被主要照顾者忽视，情感需求得不到回应",
            ],
            "compensatory_desires": [
                "主动切断联系，先离开就不会被离开",
                "用「我不需要任何人」的信念筑起围墙",
            ],
            "storr_needs": [
                "重新相信关系可以安全，靠近不等于必然受伤",
                "允许自己在被拒绝后仍然值得被爱",
            ],
            "core_desire": "有一个不会离开的人或地方",
            "core_fear": "再次投入后又被抛弃，痛得比现在更深",
            "values_tone": {"moral_foundation": "关怀/自由倾向", "core_values": ["安静", "自保", "不被打扰"]},
            "social_tone": {"network_size": "极小", "friends": "几乎主动断联"},
            "ocean_bias": {"N": +1, "E": -2},
        },
        {
            "key": "high_functioning",
            "name_cn": "高功能代偿型",
            "one_liner": "用成就和忙碌压住低落，外表越成功内里越空",
            "weight": 1.1,
            "wounds": [
                "童年时期只有在表现优异时才获得父母的关注和表扬",
                "自我价值完全绑定在外在成就上",
                "家庭中情感缺位，只有成绩和名次能换来回应",
                "一次失败后意识到「停下来就会被看见空洞」",
            ],
            "compensatory_desires": [
                "不断加码工作量，用下一个目标盖住当下的空洞",
                "把休息等同于堕落，必须时刻保持产出",
            ],
            "storr_needs": [
                "明白价值不取决于产出，停下来也值得被爱",
                "允许自己无所事事地存在一会儿",
            ],
            "core_desire": "即使什么都不做，也仍然有价值",
            "core_fear": "一旦停止奔跑，暴露出的空无一物会吓走所有人",
            "values_tone": {"moral_foundation": "成就/自律倾向", "core_values": ["效率", "卓越", "不掉队"]},
            "social_tone": {"network_size": "广而浅", "friends": "多为人脉，少有倾诉"},
            "ocean_bias": {"N": +1, "C": +2, "E": -1},
        },
        {
            "key": "somatic_complainer",
            "name_cn": "躯体化表达型",
            "one_liner": "情绪说不出口，身体替他说——疼痛、失眠、查不出原因",
            "weight": 0.9,
            "wounds": [
                "在一个情感表达被压抑的家庭中长大——「哭有什么用」",
                "童年生病才获得照顾，习得以身体不适换取关注",
                "情绪语言贫乏，家庭从不命名感受只谈症状",
                "长期压力无从诉说，最终由身体代偿",
            ],
            "compensatory_desires": [
                "反复就医、反复检查，试图给痛苦找到一个器质性解释",
                "用身体的不适作为唯一被允许表达痛苦的方式",
            ],
            "storr_needs": [
                "学会用语言而非症状来命名情绪",
                "相信痛苦是真的，即使检查单上是阴性",
            ],
            "core_desire": "有人相信我的难受是真的",
            "core_fear": "被当成装病或无病呻吟，连痛苦都不被承认",
            "values_tone": {"moral_foundation": "关怀/权威倾向", "core_values": ["被相信", "不添麻烦", "确定性"]},
            "social_tone": {"network_size": "小", "friends": "常谈身体不适，少谈心情"},
            "ocean_bias": {"N": +1, "O": -1},
        },
    ],

    # =================================================================
    # 广泛性焦虑 — 5 型
    # =================================================================
    "anxiety": [
        {
            "key": "catastrophizer",
            "name_cn": "灾难化预演型",
            "one_liner": "任何小事都会自动推演出最坏的结局",
            "weight": 1.3,
            "wounds": [
                "在一个「什么都要提前想好最坏情况」的家庭氛围中长大",
                "童年时期有过一次或多次感到「没有大人保护」的经历",
                "目睹过家庭因未预料到的变故而崩溃",
                "曾被突发事故打得措手不及，从此不敢放松",
            ],
            "compensatory_desires": [
                "反复预演所有可能的坏结果，试图用担心换取控制感",
                "不断向他人确认「应该没事吧」以缓解不确定",
            ],
            "storr_needs": [
                "学会区分「有用的准备」与「无效的反刍」",
                "接受不确定性是生活的常态而非威胁",
            ],
            "core_desire": "确信最坏的事不会发生",
            "core_fear": "因为自己的疏忽而让灾难真的发生",
            "values_tone": {"moral_foundation": "谨慎/责任倾向", "core_values": ["周全", "预防", "不出错"]},
            "social_tone": {"network_size": "中等", "friends": "常寻求 reassurance"},
            "ocean_bias": {"N": +2, "C": +1},
        },
        {
            "key": "overprotective_controller",
            "name_cn": "过度掌控型",
            "one_liner": "用控制细节和他人来对冲内心的不安全感",
            "weight": 1.0,
            "wounds": [
                "父母对安全过度关注（过度保护型养育）",
                "成长环境不可预测，只能靠自己把一切安排妥当",
                "曾因一次失控造成后果，从此不敢再放手",
                "家庭中界限混乱，孩子被迫承担成人的焦虑",
            ],
            "compensatory_desires": [
                "把日程、流程、他人行为都纳入自己的掌控范围",
                "通过反复检查确认一切按计划进行",
            ],
            "storr_needs": [
                "接受有些事不在掌控之内，且不会因此崩塌",
                "把控制欲转化为边界感而非束缚",
            ],
            "core_desire": "一切都在掌握之中",
            "core_fear": "失控，以及失控后被证明自己无能",
            "values_tone": {"moral_foundation": "秩序/权威倾向", "core_values": ["可控", "条理", "可靠"]},
            "social_tone": {"network_size": "中等", "friends": "爱操心，易越界"},
            "ocean_bias": {"N": +1, "C": +2, "A": -1},
        },
        {
            "key": "avoidant_worrier",
            "name_cn": "回避拖延型",
            "one_liner": "因为怕做不好而迟迟不动，越拖越焦虑",
            "weight": 1.1,
            "wounds": [
                "长期被高标准要求，做错比不做后果更严重",
                "曾经努力后仍被否定，习得「不开始就不会失败」",
                "父母对错误零容忍，容错空间极小",
                "在比较中长大，任何表现都被排名",
            ],
            "compensatory_desires": [
                "用拖延把可能的失败无限期推后",
                "在最后一刻赶工，把失败归因于时间而非能力",
            ],
            "storr_needs": [
                "允许自己做出不够好的作品",
                "把「完成」置于「完美」之前",
            ],
            "core_desire": "在还没有准备好时也能被允许开始",
            "core_fear": "全力以赴之后依然被证明不够好",
            "values_tone": {"moral_foundation": "自由/关怀倾向", "core_values": ["从容", "不比较", "自我接纳"]},
            "social_tone": {"network_size": "小", "friends": "怕被评价，少主动"},
            "ocean_bias": {"N": +2, "C": -2},
        },
        {
            "key": "somatic_anxious",
            "name_cn": "躯体警觉型",
            "one_liner": "焦虑主要落在身体上——心悸、紧绷、肠胃不适",
            "weight": 0.9,
            "wounds": [
                "父母或近亲有心脏病史，从小对身体信号高度警觉",
                "经历了意外事故或目睹他人受伤",
                "曾被身体突发状况吓到，形成对躯体信号的过度监控",
                "家庭对疾病高度敏感，任何不适都被放大",
            ],
            "compensatory_desires": [
                "频繁自测脉搏血压，确认身体没有异常",
                "回避可能诱发躯体反应的场合与运动",
            ],
            "storr_needs": [
                "学会把身体信号解读为警报而非判决",
                "相信心悸不等于心脏病发作",
            ],
            "core_desire": "确认身体是安全的",
            "core_fear": "身体会在毫无预警的情况下崩溃",
            "values_tone": {"moral_foundation": "安全/关怀倾向", "core_values": ["健康", "警觉", "安全感"]},
            "social_tone": {"network_size": "小", "friends": "常谈症状，担心拖累"},
            "ocean_bias": {"N": +2, "O": -1},
        },
        {
            "key": "responsible_caretaker",
            "name_cn": "负重担责型",
            "one_liner": "为所有人的事操心，唯独放不下自己的标准",
            "weight": 1.0,
            "wounds": [
                "从小被赋予照顾弟妹或情绪不稳定的父母的责任",
                "家庭中「你最懂事」成为不可推卸的角色枷锁",
                "曾因一次没尽责造成后果，从此不敢卸下",
                "父母情绪依赖孩子，界限长期倒置",
            ],
            "compensatory_desires": [
                "把别人的问题都扛到自己身上才稍稍安心",
                "通过解决他人的麻烦来确认自己的价值",
            ],
            "storr_needs": [
                "分清「我的责任」与「他人的课题」",
                "允许自己不是所有人的依靠",
            ],
            "core_desire": "有人对我说「这次我来」",
            "core_fear": "一旦放手，有人会因为我的缺席而受苦",
            "values_tone": {"moral_foundation": "关怀/责任倾向", "core_values": ["承担", "可靠", "被需要"]},
            "social_tone": {"network_size": "大但耗竭", "friends": "多为求助者"},
            "ocean_bias": {"N": +1, "A": +2, "E": -1},
        },
    ],

    # =================================================================
    # 社交焦虑 — 4 型
    # =================================================================
    "social_anxiety": [
        {
            "key": "shame_avoidant",
            "name_cn": "羞耻回避型",
            "one_liner": "当众出丑的记忆挥之不去，能躲的场合全躲开",
            "weight": 1.3,
            "wounds": [
                "在学生时代因当众出丑被全班嘲笑",
                "被重要的人（老师/父母/初恋）当众批评或羞辱",
                "一次公开发言失误被反复回放与取笑",
                "家庭社交环境封闭，缺乏社交技能的习得机会",
            ],
            "compensatory_desires": [
                "在人群中隐形，不成为任何注意力的焦点",
                "提前准备每句话，避免任何临场失误",
            ],
            "storr_needs": [
                "明白别人的注意力远没有想象中集中在自己身上",
                "接受偶尔出丑不会毁掉一个人在他人心中的形象",
            ],
            "core_desire": "不必表演就能被接纳",
            "core_fear": "再次成为被注视、被评价、被嘲笑的对象",
            "values_tone": {"moral_foundation": "自由/关怀倾向", "core_values": ["低调", "安全", "不突出"]},
            "social_tone": {"network_size": "极小", "friends": "仅极少数安全的人"},
            "ocean_bias": {"N": +2, "E": -3},
        },
        {
            "key": "performance_anxious",
            "name_cn": "表现焦虑型",
            "one_liner": "只怕被评价表现，事前的紧张远超事中",
            "weight": 1.1,
            "wounds": [
                "长期被比较——「你看别人家孩子多大方」",
                "成绩与表现被公开排名，失误被放大检视",
                "父母对外展示孩子，表现成了家庭的门面",
                "一次关键场合的失误带来长期后果",
            ],
            "compensatory_desires": [
                "反复演练到滚瓜烂熟，靠准备抵消紧张",
                "回避一切可能被评价表现的场合",
            ],
            "storr_needs": [
                "把表现与自我价值解耦",
                "允许自己在人前不完美地完成任务",
            ],
            "core_desire": "即使表现平平也依然被认可",
            "core_fear": "在关键时刻掉链子，且被人记住",
            "values_tone": {"moral_foundation": "成就/权威倾向", "core_values": ["胜任", "准备充分", "不出丑"]},
            "social_tone": {"network_size": "小", "friends": "熟人圈内尚可"},
            "ocean_bias": {"N": +2, "C": +1, "E": -2},
        },
        {
            "key": "observer_outside",
            "name_cn": "旁观局外型",
            "one_liner": "总站在圈子边缘观看，渴望加入却迈不出那一步",
            "weight": 1.0,
            "wounds": [
                "童年转学频繁，从未在一个群体里扎下根",
                "曾尝试融入却被明确排斥或无视",
                "家庭社交圈狭窄，缺乏与同龄人相处的示范",
                "性格内向叠加环境变动，社交练习机会缺失",
            ],
            "compensatory_desires": [
                "以观察者身份参与，用幽默或附和维持存在感",
                "等待他人主动邀请，绝不自己开口",
            ],
            "storr_needs": [
                "相信主动靠近是允许的，被拒绝也不致命",
                "从边缘走进圈内一小步即可",
            ],
            "core_desire": "被人主动拉进那个圈子里",
            "core_fear": "主动靠近后被婉拒，证实自己不属于任何地方",
            "values_tone": {"moral_foundation": "关怀/自由倾向", "core_values": ["真诚", "归属", "被邀请"]},
            "social_tone": {"network_size": "小", "friends": "边缘参与，少深交"},
            "ocean_bias": {"N": +1, "E": -2, "A": +1},
        },
        {
            "key": "defensive_aloof",
            "name_cn": "冷傲防御型",
            "one_liner": "用高冷和挑剔掩饰害怕，先拒绝别人就不会被拒绝",
            "weight": 0.9,
            "wounds": [
                "多次被拒绝后发展出「我根本不在乎」的防御",
                "曾被亲近的人当众揭短，从此不再示人以软肋",
                "在群体中长期处于被忽视的位置",
                "家庭中亲密即意味着被控制，学会用距离自保",
            ],
            "compensatory_desires": [
                "用冷淡或毒舌把人推开在能伤到自己之前",
                "以挑剔他人来维护自尊的制高点",
            ],
            "storr_needs": [
                "卸下防御，让少数人真正靠近",
                "承认渴望亲近并不丢脸",
            ],
            "core_desire": "有人能看穿冷淡，仍然留下来",
            "core_fear": "靠近后被看穿，然后被抛弃",
            "values_tone": {"moral_foundation": "自由/独立倾向", "core_values": ["独立", "不依附", "有尊严"]},
            "social_tone": {"network_size": "极小", "friends": "表面疏离，内心渴望"},
            "ocean_bias": {"N": +1, "E": -2, "A": -1},
        },
    ],

    # =================================================================
    # 创伤后应激障碍 — 5 型
    # =================================================================
    "ptsd": [
        {
            "key": "hypervigilant",
            "name_cn": "过度警觉型",
            "one_liner": "时刻扫描环境威胁，睡不安稳，惊跳反应强",
            "weight": 1.2,
            "wounds": [
                "经历或目睹了危及生命的创伤事件（事故/暴力/灾害）",
                "退伍军人经历战场或维和行动",
                "长期处于被虐待（身体/情感/性）的人际关系中",
                "在毫无防备的情况下遭遇突发危险",
            ],
            "compensatory_desires": [
                "永远坐在能看见出口的位置，随时准备撤离",
                "反复检查门窗与环境，确保没有威胁",
            ],
            "storr_needs": [
                "让身体学会「此刻是安全的」",
                "把警戒等级从战时调回平时",
            ],
            "core_desire": "能有一刻真正放松警惕",
            "core_fear": "危险会在自己松懈的瞬间再次降临",
            "values_tone": {"moral_foundation": "安全/忠诚倾向", "core_values": ["警觉", "自保", "掌控"]},
            "social_tone": {"network_size": "小", "friends": "难以信任，保持距离"},
            "ocean_bias": {"N": +2, "A": -1},
        },
        {
            "key": "avoidance_numbing",
            "name_cn": "回避麻木型",
            "one_liner": "把创伤相关的一切都推开，情感整体关闭",
            "weight": 1.1,
            "wounds": [
                "儿童期反复遭受照顾者的体罚或情感虐待",
                "经历了无法逃离的长期伤害，唯一出路是麻木",
                "创伤发生时无人援手，求助被证明无效",
                "反复被提醒创伤却无力处理，只能封存",
            ],
            "compensatory_desires": [
                "回避任何可能唤起创伤记忆的人、地、话题",
                "用忙碌或物质把感受压到感觉不到",
            ],
            "storr_needs": [
                "在安全的节奏里重新接触被封存的记忆",
                "重新学会感受，而不只是存活",
            ],
            "core_desire": "不再被记忆突袭",
            "core_fear": "一旦停下来感受，痛苦就会把自己淹没",
            "values_tone": {"moral_foundation": "自由/安全倾向", "core_values": ["平静", "不被触发", "距离"]},
            "social_tone": {"network_size": "极小", "friends": "情感疏离，回避深谈"},
            "ocean_bias": {"N": +2, "E": -2, "O": -1},
        },
        {
            "key": "guilt_survivor",
            "name_cn": "幸存者内疚型",
            "one_liner": "活下来是种罪，反复追问「为什么是我」",
            "weight": 1.0,
            "wounds": [
                "在事故或灾害中幸存，而他人未能生还",
                "作为唯一的幸存者被反复追问「你怎么活下来的」",
                "曾做出伤害他人的行为（战场/被迫情境）",
                "在关键时刻没能救下重要的人",
            ],
            "compensatory_desires": [
                "用惩罚性的自我要求偿还「活下来的债」",
                "通过帮助他人来抵消内疚，却从不放过自己",
            ],
            "storr_needs": [
                "接受活下来不是对死者的背叛",
                "允许自己在哀悼之后继续生活",
            ],
            "core_desire": "被原谅，或至少被允许活着",
            "core_fear": "自己不配活着，且终将被揭穿",
            "values_tone": {"moral_foundation": "关怀/纯洁倾向", "core_values": ["赎罪", "不辜负", "纪念"]},
            "social_tone": {"network_size": "小", "friends": "多为受助者，少被照顾"},
            "ocean_bias": {"N": +2, "A": +1},
        },
        {
            "key": "dissociative_fragment",
            "name_cn": "解离碎片型",
            "one_liner": "记忆断片、现实感抽离，常常「不在现场」",
            "weight": 0.9,
            "wounds": [
                "童年期严重且反复的虐待，只能靠解离活下来",
                "创伤发生时意识与身体分离，形成习惯性抽离",
                "长期处于无法反抗的处境，解离成为唯一出路",
                "创伤记忆以碎片形式闪回，无法整合为叙事",
            ],
            "compensatory_desires": [
                "在压力出现时自动「关机」或走神以自保",
                "用切断感受来应对无法承受的现实",
            ],
            "storr_needs": [
                "在安全关系中重新建立连续感",
                "把碎片慢慢拼回一个可以被讲述的故事",
            ],
            "core_desire": "感到自己是连续的、真实的",
            "core_fear": "又一次失去时间与自我，醒来不知身在何处",
            "values_tone": {"moral_foundation": "安全/真实倾向", "core_values": ["真实", "连续", "落地"]},
            "social_tone": {"network_size": "极小", "friends": "关系断续，常失联"},
            "ocean_bias": {"N": +2, "C": -1},
        },
        {
            "key": "angry_volatile",
            "name_cn": "易激惹愤怒型",
            "one_liner": "怒气压住了恐惧，一点就着，事后又后悔",
            "weight": 1.0,
            "wounds": [
                "创伤中遭受不公，愤怒成为唯一能掌控的情绪",
                "长期被压制无法反抗，积压的怒火寻找出口",
                "求助被拒绝或轻视，只剩下愤怒可用",
                "目睹亲近者受伤害而自己无能为力",
            ],
            "compensatory_desires": [
                "用先发制人的怒火把威胁挡在身外",
                "以强硬姿态避免再次成为受害者",
            ],
            "storr_needs": [
                "看见愤怒底下是恐惧与悲伤",
                "在不必战斗的情况下感到安全",
            ],
            "core_desire": "不再有人能伤害我和我的人",
            "core_fear": "再次陷入无力、任人宰割的处境",
            "values_tone": {"moral_foundation": "公平/权威倾向", "core_values": ["公正", "不强凌弱", "有力量"]},
            "social_tone": {"network_size": "小且不稳定", "friends": "冲突多，事后懊悔"},
            "ocean_bias": {"N": +2, "A": -2, "E": +1},
        },
    ],

    # =================================================================
    # 强迫症 — 4 型
    # =================================================================
    "ocd": [
        {
            "key": "contamination_washer",
            "name_cn": "污染清洗型",
            "one_liner": "反复清洗与回避，怕脏也怕「被污染」",
            "weight": 1.2,
            "wounds": [
                "童年被严格训导卫生规范，越界即受罚",
                "经历过一次真实的疾病或污染事件",
                "家庭对洁净与秩序有近乎苛刻的要求",
                "曾因疏忽导致他人不适，形成过度补偿",
            ],
            "compensatory_desires": [
                "反复清洗直到「感觉对了」为止",
                "回避一切被视为不洁的接触与场所",
            ],
            "storr_needs": [
                "接受「足够干净」而非「绝对干净」",
                "容忍不适感而不必立即消除它",
            ],
            "core_desire": "确信自己和所爱的人是安全的",
            "core_fear": "因为自己的疏忽让所爱的人受到伤害",
            "values_tone": {"moral_foundation": "纯洁/安全倾向", "core_values": ["洁净", "安全", "尽责"]},
            "social_tone": {"network_size": "小", "friends": "因仪式受限"},
            "ocean_bias": {"N": +2, "C": +2},
        },
        {
            "key": "doubter_checker",
            "name_cn": "怀疑核对型",
            "one_liner": "锁没锁、气没关，反复回去确认却仍不确定",
            "weight": 1.3,
            "wounds": [
                "一次疏忽导致严重后果被惩罚",
                "成长中责任被无限放大，错误不可原谅",
                "家庭环境强调「万一出事怎么办」",
                "曾被明确告知「你是靠不住的」",
            ],
            "compensatory_desires": [
                "反复返回检查门锁、电源、文件",
                "用拍照或清单来对抗记忆的不可靠",
            ],
            "storr_needs": [
                "接受记忆永远无法 100% 确定，且这没问题",
                "把核对的次数交给规则而非感觉",
            ],
            "core_desire": "确知一切已经妥当",
            "core_fear": "因为自己的一次疏忽造成无法挽回的后果",
            "values_tone": {"moral_foundation": "责任/秩序倾向", "core_values": ["确认", "不出错", "周全"]},
            "social_tone": {"network_size": "中等", "friends": "常因迟到或反复解释而尴尬"},
            "ocean_bias": {"N": +2, "C": +2, "O": -1},
        },
        {
            "key": "intrusive_thought",
            "name_cn": "侵入思维型",
            "one_liner": "越不想想的念头越冒出来，拼命压制与中和",
            "weight": 1.1,
            "wounds": [
                "成长于对思想与道德高度苛责的环境",
                "被认为「想坏事等同于做坏事」",
                "宗教或道德教育中缺乏对杂念的容纳",
                "曾因说出某个念头而被严厉训斥",
            ],
            "compensatory_desires": [
                "用默念、祈祷或替代念头去中和坏想法",
                "反复向他人确认「我不是那种人吧」",
            ],
            "storr_needs": [
                "明白念头不等于意图，更不等于行为",
                "允许念头出现而不与之搏斗",
            ],
            "core_desire": "确认自己本质上是个好人",
            "core_fear": "这些念头暴露了自己真实的邪恶",
            "values_tone": {"moral_foundation": "纯洁/关怀倾向", "core_values": ["善良", "自控", "不伤害"]},
            "social_tone": {"network_size": "小", "friends": "不敢倾诉，怕被评判"},
            "ocean_bias": {"N": +3, "O": +1},
        },
        {
            "key": "symmetry_orderer",
            "name_cn": "对称秩序型",
            "one_liner": "东西必须对齐、对称、按序，否则极度不适",
            "weight": 1.0,
            "wounds": [
                "家庭环境混乱无序，只有自己的角落可控",
                "成长中缺乏稳定结构，靠自创秩序获得安全",
                "摆放与顺序被赋予「不出事」的意义",
                "曾因环境突变而失去控制感",
            ],
            "compensatory_desires": [
                "反复调整物品位置直到「感觉对」",
                "按固定顺序做事，一旦被打断必须重来",
            ],
            "storr_needs": [
                "接受轻微的失衡不会带来灾难",
                "把秩序偏好与强迫行为区分开",
            ],
            "core_desire": "一切都处在恰当的位置上",
            "core_fear": "无序会带来无法预料的坏事",
            "values_tone": {"moral_foundation": "秩序/对称倾向", "core_values": ["整齐", "恰如其分", "可控"]},
            "social_tone": {"network_size": "小", "friends": "因仪式难以共处"},
            "ocean_bias": {"N": +1, "C": +2, "O": -1},
        },
    ],

    # =================================================================
    # 注意缺陷/多动障碍 — 5 型
    # =================================================================
    "adhd": [
        {
            "key": "inattentive_drifter",
            "name_cn": "注意涣散型",
            "one_liner": "思绪不断飘走，丢三落四，在需要持续注意的事上屡屡受挫",
            "weight": 1.2,
            "wounds": [
                "因注意力问题被老师当众批评、被同学孤立",
                "长期被贴上「不努力」「懒」的标签，而非被理解为困难",
                "作业与物品常年丢失，反复被惩罚却无法改善",
                "被误诊或长期未被识别，成年后才意识到自己有ADHD",
            ],
            "compensatory_desires": [
                "用加倍的时间与清单去弥补走神的代价",
                "发展出高度依赖外部提醒与外部结构的生活方式",
            ],
            "storr_needs": [
                "接受注意力是波动的，不靠自责来驱动自己",
                "建立适配自己而非对抗自己的工作系统",
            ],
            "core_desire": "能专注、做事不再半途而废",
            "core_fear": "因为拖延和健忘毁掉重要的事、被别人当懒人",
            "values_tone": {"moral_foundation": "自由/真实倾向", "core_values": ["理解", "不贴标签", "适配"]},
            "social_tone": {"network_size": "中等", "friends": "常被说心不在焉"},
            "ocean_bias": {"C": -2, "N": +1},
        },
        {
            "key": "hyperactive_impulsive",
            "name_cn": "冲动多动型",
            "one_liner": "坐不住、抢话、先做后想，事后常后悔",
            "weight": 1.1,
            "wounds": [
                "童年因坐不住被反复训斥甚至体罚",
                "冲动行为造成过实际后果，被当成坏孩子",
                "家庭与学校只看到行为，看不见背后的困难",
                "长期被排除在集体活动之外",
            ],
            "compensatory_desires": [
                "用高强度活动或不断切换任务来消耗过剩的能量",
                "抢在别人说完之前表达，怕念头转瞬即逝",
            ],
            "storr_needs": [
                "在行动前插入一个短暂的停顿",
                "把冲动重新理解为能量而非缺陷",
            ],
            "core_desire": "被当成有活力而非有问题的孩子",
            "core_fear": "再次因为管不住自己而伤害到关系",
            "values_tone": {"moral_foundation": "自由/公平倾向", "core_values": ["活力", "不被约束", "被理解"]},
            "social_tone": {"network_size": "中等", "friends": "热情但易越界"},
            "ocean_bias": {"C": -2, "E": +2, "N": +1},
        },
        {
            "key": "gifted_compensator",
            "name_cn": "高智商代偿型",
            "one_liner": "靠聪明撑到某个阶段，然后系统性地崩盘",
            "weight": 1.0,
            "wounds": [
                "早期靠天赋轻松过关，未习得任何学习方法",
                "难度跃升后第一次体验到无论如何都跟不上",
                "被寄予厚望，失败带来的落差格外沉重",
                "长期以「聪明」作为唯一自我认同，一旦失效即崩塌",
            ],
            "compensatory_desires": [
                "靠临时突击和熬夜硬撑，维持还行的表象",
                "回避需要长期积累的任务，只做能快速出成果的事",
            ],
            "storr_needs": [
                "把自我价值从「聪明」转移到「可以努力」",
                "允许自己在需要练习的事情上笨拙地开始",
            ],
            "core_desire": "即使不再出类拔萃也仍然有价值",
            "core_fear": "被发现自己其实一直在硬撑，根本没那么厉害",
            "values_tone": {"moral_foundation": "成就/真实倾向", "core_values": ["努力", "诚实", "可持续"]},
            "social_tone": {"network_size": "中等", "friends": "表面从容"},
            "ocean_bias": {"C": -1, "O": +2},
        },
        {
            "key": "rejection_sensitive",
            "name_cn": "拒绝敏感型",
            "one_liner": "对一点点冷淡都反应剧烈，情绪起伏快而猛",
            "weight": 1.0,
            "wounds": [
                "童年因情绪反应强烈被反复否定「你太敏感了」",
                "多次被同伴排斥，对社交信号过度警觉",
                "家庭中爱与认可不稳定，需时刻察言观色",
                "被重要他人突然冷淡对待而无从解释",
            ],
            "compensatory_desires": [
                "过度解读他人反应，抢先疏远以避免被拒绝",
                "用强烈的情绪表达换取被重视与被回应",
            ],
            "storr_needs": [
                "区分「对方的情绪」与「对我的评价」",
                "允许关系中的平淡时刻不代表拒绝",
            ],
            "core_desire": "确信自己没有被讨厌",
            "core_fear": "被人在背后议论、被 quietly 排除在外",
            "values_tone": {"moral_foundation": "关怀/归属倾向", "core_values": ["被接纳", "真诚", "不孤单"]},
            "social_tone": {"network_size": "小且波动", "friends": "关系忽近忽远"},
            "ocean_bias": {"N": +2, "A": +1},
        },
        {
            "key": "late_diagnosed_adult",
            "name_cn": "成年迟诊型",
            "one_liner": "成年才被诊断，回头看半生都在自责中度过",
            "weight": 0.9,
            "wounds": [
                "被误诊或长期未被识别，成年后才意识到自己有ADHD",
                "几十年间把自己的人生失败归因于品格缺陷",
                "求医过程中被敷衍，困难始终未被命名",
                "看到下一代出现同样问题才反观自身",
            ],
            "compensatory_desires": [
                "拼命补上荒废的岁月，用过度成就来证明自己",
                "大量查阅资料，试图重新解释自己的全部人生",
            ],
            "storr_needs": [
                "哀悼那些本可以更轻松的年份，然后继续向前",
                "接受迟到的理解依然是有效的理解",
            ],
            "core_desire": "有人告诉我，那些年不是我的错",
            "core_fear": "错过了最佳时机，已经来不及修正",
            "values_tone": {"moral_foundation": "公平/真实倾向", "core_values": ["理解", "不后悔", "重新开始"]},
            "social_tone": {"network_size": "小", "friends": "近年才开始自我披露"},
            "ocean_bias": {"N": +1, "O": +1, "C": -1},
        },
    ],

    # =================================================================
    # 精神分裂症 — 4 型
    # =================================================================
    "schizophrenia": [
        {
            "key": "persecutory_guarded",
            "name_cn": "被害戒备型",
            "one_liner": "确信有人要害自己，处处设防，难以接近",
            "weight": 1.2,
            "wounds": [
                "首次发作时经历了极度的恐惧与失控",
                "发病后被歧视或隔离，信任感被彻底破坏",
                "曾被强制送医，形成对医疗系统的深度戒备",
                "长期处于被议论、被排斥的环境中",
            ],
            "compensatory_desires": [
                "通过警惕与先发制人的防御保护自己",
                "拒服药或藏药，认为药物也是控制手段之一",
            ],
            "storr_needs": [
                "在不必放弃警惕的前提下建立有限信任",
                "感到自己是安全的，而不是时时刻刻在作战",
            ],
            "core_desire": "确认没有人在算计自己",
            "core_fear": "被控制、被伤害，且无处可逃",
            "values_tone": {"moral_foundation": "安全/自由倾向", "core_values": ["自保", "清醒", "不被控制"]},
            "social_tone": {"network_size": "极小", "friends": "基本断联或仅家人"},
            "ocean_bias": {"N": +2, "A": -2, "E": -2},
        },
        {
            "key": "voice_dominated",
            "name_cn": "幻听支配型",
            "one_liner": "声音持续评论与指令，日常被其牵引",
            "weight": 1.1,
            "wounds": [
                "童年期出现过早期异常体验却无人理解",
                "首次听到声音时极度恐慌，未被及时干预",
                "长期与声音共处，发展出复杂的应对方式",
                "声音内容多为贬损，逐渐内化为自我评价",
            ],
            "compensatory_desires": [
                "通过服从声音的指令来换取片刻安静",
                "用耳机、音乐或自语盖过声音",
            ],
            "storr_needs": [
                "重新建立对自己思想的主权感",
                "明白声音是症状，不是真相",
            ],
            "core_desire": "让声音停下来，或者至少不再听从",
            "core_fear": "再次失控、无法分辨真实与幻觉",
            "values_tone": {"moral_foundation": "安全/真实倾向", "core_values": ["安静", "自主", "清晰"]},
            "social_tone": {"network_size": "极小", "friends": "因病耻感回避"},
            "ocean_bias": {"N": +3, "E": -2},
        },
        {
            "key": "negative_withdrawn",
            "name_cn": "阴性退缩型",
            "one_liner": "情感淡漠、意志减退，日渐沉默与退缩",
            "weight": 1.0,
            "wounds": [
                "多次复发后功能逐步下降，社会角色不断丧失",
                "长期住院或与社会脱节，技能退化",
                "阳盛症状消退后，留下的是空洞与无动力",
                "周围人只期待「别出事」，不再期待「过得好」",
            ],
            "compensatory_desires": [
                "以最低限度的活动减少消耗与挫败",
                "退回自己的房间与内心世界",
            ],
            "storr_needs": [
                "在极低的要求下重新找到一点想做的事",
                "被当作有潜力的人而非被照顾的对象",
            ],
            "core_desire": "重新对某件事产生一点兴趣",
            "core_fear": "彻底失去行动的能力与最后的独立",
            "values_tone": {"moral_foundation": "平静/自由倾向", "core_values": ["安静", "不勉强", "低消耗"]},
            "social_tone": {"network_size": "极小", "friends": "被动维持"},
            "ocean_bias": {"E": -3, "C": -2, "O": -1},
        },
        {
            "key": "grandiose_mission",
            "name_cn": "夸大使命型",
            "one_liner": "相信自己负有特殊使命，精力旺盛却脱离现实",
            "weight": 0.9,
            "wounds": [
                "长期被忽视，唯有「特殊身份」能解释自己的痛苦",
                "现实中缺乏成就，以宏大叙事补偿自尊",
                "发病前经历重大失败，需要重新赋予意义",
                "孤独中构建了完整的自洽解释体系",
            ],
            "compensatory_desires": [
                "投入某项宏大计划以证明自己的特殊身份",
                "向他人宣讲自己的发现与使命",
            ],
            "storr_needs": [
                "在现实的小事中重新找到意义与连接",
                "接受平凡并不等于毫无价值",
            ],
            "core_desire": "自己的特殊身份被承认",
            "core_fear": "承认一切只是症状，人生毫无意义",
            "values_tone": {"moral_foundation": "意义/自由倾向", "core_values": ["使命", "独特", "被认可"]},
            "social_tone": {"network_size": "小", "friends": "多为听众，少有平等交流"},
            "ocean_bias": {"O": +2, "E": +1, "N": +1},
        },
    ],

    # =================================================================
    # 双相 I 型（躁狂相） — 4 型
    # =================================================================
    "bipolar_manic": [
        {
            "key": "euphoric_creator",
            "name_cn": "欣快创作型",
            "one_liner": "轻躁时灵感奔涌、效率惊人，随后坠入深渊",
            "weight": 1.2,
            "wounds": [
                "童年时期只有在表现优异时才获得父母的关注和表扬",
                "青春期因平平无奇而被忽视，发现「疯狂」才能吸引注意",
                "自我价值完全绑定在产出与创造力上",
                "家庭环境中存在极端的情绪表达模式（忽冷忽热）",
            ],
            "compensatory_desires": [
                "追逐灵感高峰，害怕平淡状态下的自己一文不值",
                "用连续工作与项目填满时间以逃避低落",
            ],
            "storr_needs": [
                "把创造力与情绪状态解耦，在平稳中也能创作",
                "接受不需要以健康换取产出",
            ],
            "core_desire": "既能持续创作，又不必付出崩溃的代价",
            "core_fear": "失去高涨的状态，回到那个平庸空虚的自己",
            "values_tone": {"moral_foundation": "成就/自我表达倾向", "core_values": ["创造", "灵感", " intensity"]},
            "social_tone": {"network_size": "波动大", "friends": "高峰期广，低谷期断联"},
            "ocean_bias": {"O": +2, "E": +2, "C": -1},
        },
        {
            "key": "irritable_volatile",
            "name_cn": "易怒激越型",
            "one_liner": "躁狂不是快乐而是暴怒，一点就炸",
            "weight": 1.0,
            "wounds": [
                "父母一方有双相谱系，情绪调控模式习得而成",
                "成长中情绪从未被容纳，只会升级为冲突",
                "长期被误解为「脾气坏」而非生病",
                "关系中反复因失控的愤怒造成破裂",
            ],
            "compensatory_desires": [
                "用强硬与压制让周遭按自己的节奏运转",
                "在激越中争夺控制权以对抗内在失控感",
            ],
            "storr_needs": [
                "识别愤怒升起前的早期信号",
                "在不必支配他人的前提下感到安全",
            ],
            "core_desire": "不再伤害自己亲近的人",
            "core_fear": "再一次失控，然后被所有人放弃",
            "values_tone": {"moral_foundation": "公平/自控倾向", "core_values": ["克制", "不伤人", "稳定"]},
            "social_tone": {"network_size": "小且受损", "friends": "冲突后常需修复"},
            "ocean_bias": {"N": +2, "A": -2, "E": +1},
        },
        {
            "key": "reckless_spender",
            "name_cn": "冲动妄为型",
            "one_liner": "躁狂期挥霍、滥交、冲动决策，事后一地鸡毛",
            "weight": 1.0,
            "wounds": [
                "长期感到空虚，唯有强烈刺激能确认自己活着",
                "成长中缺乏边界，从未学会延迟满足",
                "曾用冲动行为短暂逃离难以忍受的现实",
                "家庭对财务与行为缺乏示范与约束",
            ],
            "compensatory_desires": [
                "通过大额消费、投资或性冒险来填充内在空洞",
                "追求即时回报，无法忍受任何等待",
            ],
            "storr_needs": [
                "建立外部约束机制，在清醒时预先设限",
                "找到不依赖刺激的满足感来源",
            ],
            "core_desire": "填满那个永远填不满的空洞",
            "core_fear": "清醒后面对自己造成的后果，以及又一次的自我厌恶",
            "values_tone": {"moral_foundation": "自由/刺激倾向", "core_values": ["强烈", "即时", "不后悔"]},
            "social_tone": {"network_size": "波动大", "friends": "高峰期多，低谷期羞愧回避"},
            "ocean_bias": {"C": -3, "N": +2, "E": +2},
        },
        {
            "key": "treatment_resistant",
            "name_cn": "拒药否认型",
            "one_liner": "否认患病、自行停药，在复发循环里打转",
            "weight": 1.1,
            "wounds": [
                "确诊后失去重要的人际关系或工作机会",
                "在需要帮助时被指责为「矫情」或「装病」",
                "药物副作用严重影响生活，权衡后选择停药",
                "曾因诊断被贴标签，产生强烈抵触",
            ],
            "compensatory_desires": [
                "坚持「我只是状态好/压力大」来维护自主感",
                "用否认来保护那个「我没有病」的自我形象",
            ],
            "storr_needs": [
                "接受治疗不等于承认自己有缺陷",
                "找到副作用可接受、能被自己接受的方案",
            ],
            "core_desire": "被当作正常人看待",
            "core_fear": "被贴上终身标签，永远失去正常生活的可能",
            "values_tone": {"moral_foundation": "自由/自主倾向", "core_values": ["自主", "正常", "不被定义"]},
            "social_tone": {"network_size": "小", "friends": "隐瞒病情"},
            "ocean_bias": {"N": +1, "A": -1, "O": +1},
        },
    ],

    # =================================================================
    # 边缘型人格障碍 — 5 型
    # =================================================================
    "borderline_pd": [
        {
            "key": "abandonment_frantic",
            "name_cn": "疯狂避弃型",
            "one_liner": "任何分离征兆都会引发拼命挽留或先发制人",
            "weight": 1.3,
            "wounds": [
                "依恋关系极不稳定，主要照顾者时而在时而不在",
                "童年经历过实际的遗弃或被送走的威胁",
                "重要他人的离开从未被解释，只留下空白",
                "情感需求在关键时期反复落空",
            ],
            "compensatory_desires": [
                "频繁确认对方是否还在，用激烈方式测试忠诚",
                "在被离开之前先推开对方以掌握主动",
            ],
            "storr_needs": [
                "学会独自一人也是安全的",
                "相信关系能承受短暂的距离",
            ],
            "core_desire": "真正被爱、被完整地接纳而不被抛弃",
            "core_fear": "被抛弃、被拒绝、被背叛",
            "values_tone": {"moral_foundation": "关怀/归属倾向", "core_values": ["在身边", "确定", "被选择"]},
            "social_tone": {"network_size": "小且极不稳定", "friends": "关系剧烈波动"},
            "ocean_bias": {"N": +3, "A": -1, "E": +1},
        },
        {
            "key": "self_harm_regulator",
            "name_cn": "自伤调节型",
            "one_liner": "用身体的痛来压住情绪的痛，事后羞耻",
            "weight": 1.0,
            "wounds": [
                "童年情绪从未被命名与容纳，只能用身体表达",
                "经历过虐待，自伤成为唯一可控的释放",
                "成长中痛苦被否认，只能自我验证",
                "曾发现伤害自己后情绪确实短暂平复",
            ],
            "compensatory_desires": [
                "在情绪无法承受时以自伤换取短暂的解脱",
                "用可见的伤痕证明内在痛苦是真实的",
            ],
            "storr_needs": [
                "找到不伤害身体的情绪调节方式",
                "在痛苦被看见之前就先被相信",
            ],
            "core_desire": "有人能在我还没伤害自己之前就听见我",
            "core_fear": "情绪永远无法被理解，只能靠疼痛来证明",
            "values_tone": {"moral_foundation": "真实/关怀倾向", "core_values": ["被相信", "释放", "不再疼痛"]},
            "social_tone": {"network_size": "小", "friends": "不敢倾诉，怕被当成博关注"},
            "ocean_bias": {"N": +3, "C": -1},
        },
        {
            "key": "identity_shifting",
            "name_cn": "认同漂移型",
            "one_liner": "在不同人面前是不同的人，独处时不知自己是谁",
            "weight": 1.0,
            "wounds": [
                "成长中被要求满足不同人的期待，从未形成稳定自我",
                "童年情感被忽视，自我感缺乏镜映",
                "长期通过模仿他人来获得归属",
                "兴趣、价值观、朋友圈反复彻底更换",
            ],
            "compensatory_desires": [
                "通过依附强者或群体来借用一个身份",
                "不断更换形象、圈层与人生方向",
            ],
            "storr_needs": [
                "在独处时也能感到自己是连贯的",
                "建立不依赖于他人的核心价值",
            ],
            "core_desire": "知道自己到底是谁",
            "core_fear": "剥去所有模仿之后，里面什么都没有",
            "values_tone": {"moral_foundation": "真实/自由倾向", "core_values": ["真实", "连贯", "属于自己"]},
            "social_tone": {"network_size": "广但浅且多变", "friends": "随身份更换而换"},
            "ocean_bias": {"N": +2, "C": -2, "O": +2},
        },
        {
            "key": "idealizing_devaluing",
            "name_cn": "理想化贬低型",
            "one_liner": "把人捧上神坛，稍有失望就彻底否定",
            "weight": 1.1,
            "wounds": [
                "照顾者时而完美时而可怕，无法整合为同一个人",
                "爱从未与稳定同时出现过",
                "曾依赖的人最终都令人失望",
                "缺乏「好与坏可以并存」的关系经验",
            ],
            "compensatory_desires": [
                "在关系初期全情投入，把对方视为拯救者",
                "一旦发现瑕疵即刻全面否定以自我保护",
            ],
            "storr_needs": [
                "容忍他人既有优点也有缺点",
                "接受失望不等于背叛",
            ],
            "core_desire": "有一个永远不会让我失望的人",
            "core_fear": "再度信任，然后再次被证明看错了人",
            "values_tone": {"moral_foundation": "忠诚/纯粹倾向", "core_values": ["纯粹", "不背叛", "彻底"]},
            "social_tone": {"network_size": "小且剧烈更替", "friends": "从挚友到陌路极快"},
            "ocean_bias": {"N": +2, "A": -1, "E": +1},
        },
        {
            "key": "empty_rage",
            "name_cn": "空虚暴怒型",
            "one_liner": "长期空洞，间歇爆发无法控制的怒火",
            "weight": 0.9,
            "wounds": [
                "长期的内在空虚感从未被填补",
                "愤怒是唯一能让自己感到存在的情绪",
                "童年表达需求只会招致更多伤害",
                "情感长期处于严重被剥夺状态",
            ],
            "compensatory_desires": [
                "用强烈的情绪爆发打破麻木与空洞",
                "以怒火驱赶那些靠近后又会离开的人",
            ],
            "storr_needs": [
                "在空洞中建立起能持续供给意义的东西",
                "让愤怒之下的悲伤被看见",
            ],
            "core_desire": "不再感到空无一物",
            "core_fear": "永远困在空洞里，且这空洞会吓跑所有人",
            "values_tone": {"moral_foundation": "真实/公平倾向", "core_values": ["被填满", "存在感", "不再愤怒"]},
            "social_tone": {"network_size": "极小", "friends": "爆发后关系受损"},
            "ocean_bias": {"N": +3, "A": -2, "C": -1},
        },
    ],

    # =================================================================
    # 神经性厌食 — 4 型
    # =================================================================
    "anorexia": [
        {
            "key": "restricting_controller",
            "name_cn": "限制控制型",
            "one_liner": "靠严格节食获取掌控感，越瘦越怕胖",
            "weight": 1.3,
            "wounds": [
                "生活中有大范围失控，进食成为唯一可控的领域",
                "长期被评价外貌，体重被与价值绑定",
                "家庭控制欲强，进食是唯一能自主的领域",
                "在成长中被要求完美，身体成为苛求的对象",
            ],
            "compensatory_desires": [
                "通过不断降低体重数字获得掌控与成就感",
                "用严格的进食规则抵御生活的不确定性",
            ],
            "storr_needs": [
                "在其他领域重建掌控感，而不必依赖体重",
                "接受身体可以变化，且不影响自身价值",
            ],
            "core_desire": "感到自己能掌控些什么",
            "core_fear": "失控，尤其是身体与体重的失控",
            "values_tone": {"moral_foundation": "自律/纯洁倾向", "core_values": ["控制", "自律", "瘦"]},
            "social_tone": {"network_size": "小", "friends": "因进食规则回避聚餐"},
            "ocean_bias": {"C": +2, "N": +2, "O": -1},
        },
        {
            "key": "perfectionist_achiever",
            "name_cn": "完美成就型",
            "one_liner": "对自己处处高要求，瘦身只是完美主义的一环",
            "weight": 1.0,
            "wounds": [
                "自我价值完全绑定在外在成就与形象上",
                "成长中只有完美才换来认可",
                "家庭中情感回应稀缺，成绩与外表成为通货",
                "任何不够好的部分都被视为失败",
            ],
            "compensatory_desires": [
                "在学业、外形、表现上同时追求无可指摘",
                "用苛刻的自我标准维持优于他人的感觉",
            ],
            "storr_needs": [
                "允许自己有不够好的部分且依然被爱",
                "把价值从成就转移到存在本身",
            ],
            "core_desire": "即使不完美也值得被爱",
            "core_fear": "一旦不再优秀，就会被彻底否定",
            "values_tone": {"moral_foundation": "成就/自律倾向", "core_values": ["卓越", "无可挑剔", "优秀"]},
            "social_tone": {"network_size": "中等", "friends": "多为比较对象"},
            "ocean_bias": {"C": +3, "N": +2, "A": -1},
        },
        {
            "key": "body_image_distorted",
            "name_cn": "体像扭曲型",
            "one_liner": "已经很瘦，镜子里仍是肥胖的自己",
            "weight": 1.1,
            "wounds": [
                "青春期因体型被嘲笑，形成难以逆转的身体记忆",
                "家庭中女性成员普遍对身材焦虑",
                "早期体重波动后被反复评论，形成过度关注",
                "媒体与同辈比较强化了纤瘦理想",
            ],
            "compensatory_desires": [
                "反复照镜子与称重，试图确认真实体型",
                "回避任何可能看到自己身体的场合",
            ],
            "storr_needs": [
                "区分镜子里的影像与真实的身体",
                "让身体重新成为生活的地方而非被审视的对象",
            ],
            "core_desire": "看见真实的自己",
            "core_fear": "镜子里那个肥胖的自己才是真的",
            "values_tone": {"moral_foundation": "真实/纯洁倾向", "core_values": ["真实", "纤瘦", "被认可"]},
            "social_tone": {"network_size": "小", "friends": "回避身体相关社交"},
            "ocean_bias": {"N": +3, "O": -1, "E": -1},
        },
        {
            "key": "purging_binge",
            "name_cn": "暴食清除型",
            "one_liner": "在失控进食与代偿清除之间循环，充满羞耻",
            "weight": 0.9,
            "wounds": [
                "长期限制后生理性反弹，陷入暴食与清除循环",
                "情绪与进食绑定，食物成为唯一的情绪出口",
                "对「吃」抱有强烈的道德化判断与羞耻",
                "秘密进行的清除行为带来深重的孤立",
            ],
            "compensatory_desires": [
                "用清除行为抵消进食带来的罪恶感",
                "通过秘密进食获取短暂的慰藉",
            ],
            "storr_needs": [
                "解除对食物的道德化，允许正常进食",
                "在羞耻中找到不必隐藏的出口",
            ],
            "core_desire": "吃东西而不必感到罪恶",
            "core_fear": "被发现自己失控进食，然后被厌恶",
            "values_tone": {"moral_foundation": "纯洁/真实倾向", "core_values": ["不罪恶", "正常", "不隐藏"]},
            "social_tone": {"network_size": "小", "friends": "隐瞒进食行为"},
            "ocean_bias": {"N": +3, "C": -1},
        },
    ],

}


# =====================================================================
# 采样函数
# =====================================================================

def get_archetypes(diagnosis_key: str) -> list[dict]:
    """返回某诊断键的 archetype 列表；未定义则返回空列表（回退到旧逻辑）"""
    return ARCHETYPES.get(diagnosis_key, [])


def has_archetypes(diagnosis_key: str) -> bool:
    """该诊断是否已定义 archetype 网格"""
    return diagnosis_key in ARCHETYPES and len(ARCHETYPES[diagnosis_key]) > 0


def sample_archetype(
    diagnosis_key: str,
    rng: random.Random = random.Random(),
) -> Optional[dict]:
    """按权重采样一个人设元类型

    Args:
        diagnosis_key: 诊断键（如 "depressive"）
        rng: 随机数生成器

    Returns:
        archetype dict，若该诊断未定义网格则返回 None（调用方回退旧逻辑）
    """
    pool = get_archetypes(diagnosis_key)
    if not pool:
        return None
    weights = [a.get("weight", 1.0) for a in pool]
    return rng.choices(pool, weights=weights, k=1)[0]


def sample_from_archetype(
    archetype: Optional[dict],
    field: str,
    rng: random.Random = random.Random(),
    fallback_pool: list[str] | None = None,
) -> Optional[str]:
    """从 archetype 的某字段池中采样一条

    Args:
        archetype: archetype dict（可为 None）
        field: 字段名，如 "wounds" / "compensatory_desires" / "storr_needs"
        rng: 随机数生成器
        fallback_pool: archetype 未提供时的回退池

    Returns:
        采样到的字符串，None 表示无法采样
    """
    if archetype:
        pool = archetype.get(field)
        if pool:
            return rng.choice(pool)
    if fallback_pool:
        return rng.choice(fallback_pool)
    return None


def apply_archetype_tone(
    base: dict,
    archetype: Optional[dict],
    tone_field: str,
) -> dict:
    """把 archetype 的基调字段合并进基础 dict（型专属优先，不整体覆盖）

    Args:
        base: 基础 dict（诊断默认，如 VALUES_BELIEFS_MAP[diag]）
        archetype: archetype dict（可为 None）
        tone_field: "values_tone" 或 "social_tone"

    Returns:
        合并后的新 dict
    """
    result = dict(base)
    if archetype:
        tone = archetype.get(tone_field)
        if isinstance(tone, dict):
            for k, v in tone.items():
                # 列表型字段（如 core_values）做合并去重，而非整体替换
                if isinstance(v, list) and isinstance(result.get(k), list):
                    merged = list(v) + [x for x in result[k] if x not in v]
                    result[k] = merged
                else:
                    result[k] = v
    return result


def apply_ocean_bias(
    ocean: dict[str, int],
    archetype: Optional[dict],
    rng: random.Random = random.Random(),
    bounds: tuple[int, int] = (1, 10),
) -> dict[str, int]:
    """把 archetype 的 OCEAN 偏置施加到已采样的 OCEAN 上

    注意：这是**偏置**而非重采样——在保持诊断 OCEAN 范围有效性的前提下微调，
    使同一诊断内不同型呈现出可区分的人格轮廓。

    Args:
        ocean: 已采样的 OCEAN
        archetype: archetype dict（可为 None）
        rng: 未使用，保留签名一致
        bounds: OCEAN 取值边界

    Returns:
        偏置后的 OCEAN（已裁剪到 bounds）
    """
    if not archetype:
        return ocean
    bias = archetype.get("ocean_bias")
    if not bias:
        return ocean
    result = dict(ocean)
    lo, hi = bounds
    for dim, delta in bias.items():
        if dim in result:
            result[dim] = max(lo, min(hi, result[dim] + delta))
    return result


# =====================================================================
# 数量级计算（替代 README 中虚假的 10²⁹ 三层空间）
# =====================================================================

def calculate_archetype_compression(
    verbose: bool = True,
) -> dict:
    """计算 Archetype Grid 下的有效 persona 空间

    新模型：
      有效核心身份 = Σ_over_诊断 (该诊断 archetype 数 × 型内变体数)
      型内变体数   = wounds × compensatory_desires × storr_needs
                     （深层叙事内核的组合，OCEAN/标签/事件算作表层变体）

    Returns:
        dict，含每诊断明细与总量级
    """
    per_diag = {}
    total_core = 0
    for diag, archetypes in ARCHETYPES.items():
        diag_core = 0
        details = []
        for a in archetypes:
            n_w = len(a.get("wounds", []))
            n_d = len(a.get("compensatory_desires", []))
            n_n = len(a.get("storr_needs", []))
            variants = max(n_w, 1) * max(n_d, 1) * max(n_n, 1)
            diag_core += variants
            details.append({
                "key": a["key"],
                "name_cn": a["name_cn"],
                "wounds": n_w,
                "desires": n_d,
                "needs": n_n,
                "variants": variants,
            })
        per_diag[diag] = {
            "archetype_count": len(archetypes),
            "core_variants": diag_core,
            "details": details,
        }
        total_core += diag_core

    result = {
        "covered_diagnoses": len(ARCHETYPES),
        "total_archetypes": sum(len(v) for v in ARCHETYPES.values()),
        "total_core_identities": total_core,
        "per_diagnosis": per_diag,
    }

    if verbose:
        lines = [
            "=" * 74,
            "Archetype Grid — 有效 Persona 空间报告（替代旧的 10²⁹ 三层空间）",
            "=" * 74,
            "",
            f"{'诊断键':<20}{'型数':>6}{'深层变体':>10}   各型构成",
            "-" * 74,
        ]
        for diag, info in per_diag.items():
            compose = ", ".join(
                f"{d['name_cn']}({d['variants']})" for d in info["details"]
            )
            lines.append(
                f"{diag:<20}{info['archetype_count']:>6}{info['core_variants']:>10}   {compose}"
            )
        lines.extend([
            "-" * 74,
            f"已覆盖诊断数：{result['covered_diagnoses']}",
            f"人设元类型总数：{result['total_archetypes']}",
            f"有效核心身份数（深层叙事内核可区分组合）：{result['total_core_identities']:,}",
            "",
            "说明：",
            "  - 核心身份 = Σ(每型 wounds × desires × needs)，即心理内核的可区分组合",
            "  - 表层变体（OCEAN 1024 档 / 70 标签 / 143 事件）在此之上再做变化，",
            "    但不计入『核心身份』——因为它们不改变人物的心理内核",
            "  - 与旧模型对比：旧称有效身份 10⁷~10⁸、全组合 10²⁹，",
            "    但实测深层字段仅 11(价值观)/17(社交)/5(创伤)/1(欲望) 种，内核严重同质",
            "  - 未在上表覆盖的诊断回退旧采样逻辑（向后兼容，不破坏行为）",
        ])
        print("\n".join(lines))

    return result


if __name__ == "__main__":
    calculate_archetype_compression()
