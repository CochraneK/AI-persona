"""
职业分类模块 — 基于《中华人民共和国职业分类大典(2022年版)》

数据结构来源：人社部/市监局/统计局联合发布，2022年9月审定。
包含：8大类 × 79中类，标注 S(数字职业) / L(绿色职业)。

=========================================================================
取舍逻辑（重要 — 见 README）
=========================================================================
粒度选择：79 中类而非 1636 细类。
理由：
  1. Persona 不需要精确职业代码（如"软件工程师 2-02-10-03"），
     中类粒度（如"工程技术人员"）足够刻画人口学锚点。
  2. 79 中类在命令行可读且可筛选（--occupation-filter），
     1636 细类会淹没 CLI 参数且无实际收益。
  3. 若需更精确的职业描述，可在 persona.system_prompt 中
     通过 occupation_detail 字段自然语言描述具体岗位。

职业分布概率：
  - 默认按大类 2(专业技术) / 4(生活服务) / 6(生产制造) 加权更高，
    因为这些大类覆盖了绝大多数劳动人口。
  - 大类 1(党政机关) / 7(军人) 采样概率较低。
  - 可通过 --occupation-weights 参数自定义分布。

精神障碍职业关联（stress_level）：
  - high: 高压职业（如医疗、金融、法律）→ 与焦虑/抑郁/物质使用障碍强相关
  - medium: 中等压力
  - low: 低压职业
=========================================================================
"""

from dataclasses import dataclass, field
from typing import Optional

# =====================================================================
# 数据类型
# =====================================================================

@dataclass
class OccupationCategory:
    """职业中类"""
    code: str               # 中类编码，如 "2-02"
    gbm_code: str           # GBM编码，如 "GBM 20200"
    name_cn: str            # 中文名称
    name_en: str            # 英文翻译
    major_category: int     # 所属大类 1-8
    major_name: str         # 大类名称
    description: str        # 简要描述
    stress_level: str       # "high" / "medium" / "low" — 职业压力水平
    is_digital: bool        # 是否数字职业(S)
    is_green: bool          # 是否绿色职业(L)
    typical_roles: list[str] = field(default_factory=list)  # 常见具体岗位示例


# =====================================================================
# 79 个中类完整数据
# =====================================================================

OCCUPATIONS: list[OccupationCategory] = [
    # ===== 第一大类 GBM 10000: 党的机关、国家机关、群众团体和社会组织、企事业单位负责人 =====
    OccupationCategory("1-01", "GBM 10100", "中国共产党机关负责人",
        "CPC Organization Leaders", 1, "党的机关、国家机关、群众团体和社会组织、企事业单位负责人",
        "在党中央和地方各级机关及其工作机构中担任领导职务的人员", "medium", False, False,
        typical_roles=["党委书记", "党总支书记", "党支部书记"]),
    OccupationCategory("1-02", "GBM 10200", "国家机关负责人",
        "State Organ Leaders", 1, "党的机关、国家机关、群众团体和社会组织、企事业单位负责人",
        "在各级人大常委会、政府、政协、监察、法院、检察院中担任领导职务的人员", "high", False, False,
        typical_roles=["市长", "局长", "处长", "法院院长"]),
    OccupationCategory("1-03", "GBM 10300", "民主党派和工商联负责人",
        "Democratic Party & Federation of Industry Leaders", 1, "党的机关、国家机关、群众团体和社会组织、企事业单位负责人",
        "在民主党派和工商联各级组织机构中担任领导职务的人员", "medium", False, False,
        typical_roles=["民主党派负责人", "工商联负责人"]),
    OccupationCategory("1-04", "GBM 10400", "人民团体和群众团体、社会组织及其他成员组织负责人",
        "Mass Organizations & Social Organizations Leaders", 1, "党的机关、国家机关、群众团体和社会组织、企事业单位负责人",
        "在工会、共青团、妇联等人民团体及社会团体、基金会等担任领导职务的人员", "medium", False, False,
        typical_roles=["工会主席", "团委书记", "妇联主席", "基金会理事长"]),
    OccupationCategory("1-05", "GBM 10500", "基层群众自治组织负责人",
        "Grassroots Self-governance Organization Leaders", 1, "党的机关、国家机关、群众团体和社会组织、企事业单位负责人",
        "在居民委员会和村民委员会中担任领导职务的人员", "medium", False, False,
        typical_roles=["居委会主任", "村委会主任"]),
    OccupationCategory("1-06", "GBM 10600", "企事业单位负责人",
        "Enterprise & Institution Leaders", 1, "党的机关、国家机关、群众团体和社会组织、企事业单位负责人",
        "在企业和教育、科技、文化、卫生等事业单位中担任领导职务的人员", "high", False, False,
        typical_roles=["企业董事", "企业经理", "事业单位负责人"]),

    # ===== 第二大类 GBM 20000: 专业技术人员 =====
    OccupationCategory("2-01", "GBM 20100", "科学研究人员",
        "Scientific Researchers", 2, "专业技术人员",
        "从事自然科学、社会科学等研究的人员", "medium", False, False,
        typical_roles=["研究员", "助理研究员", "实验员"]),
    OccupationCategory("2-02", "GBM 20200", "工程技术人员",
        "Engineering Technicians", 2, "专业技术人员",
        "从事各类工程技术工作的专业人员，涵盖多个工程领域", "high", True, False,
        typical_roles=["软件工程师", "硬件工程师", "土木工程师", "电气工程师"]),
    OccupationCategory("2-03", "GBM 20300", "农业技术人员",
        "Agricultural Technicians", 2, "专业技术人员",
        "从事农业科学研究、技术推广和服务的专业人员", "low", False, True,
        typical_roles=["农艺师", "畜牧师", "农业技术推广员"]),
    OccupationCategory("2-04", "GBM 20400", "飞机和船舶技术人员",
        "Aircraft & Ship Technicians", 2, "专业技术人员",
        "从事飞机、船舶驾驶和工程技术工作的专业人员", "high", False, False,
        typical_roles=["飞行员", "船长", "轮机长"]),
    OccupationCategory("2-05", "GBM 20500", "卫生专业技术人员",
        "Health Professionals", 2, "专业技术人员",
        "从事医疗、预防、保健、护理、康复、药学等工作的专业人员", "high", False, False,
        typical_roles=["医生", "护士", "药师", "检验师"]),
    OccupationCategory("2-06", "GBM 20600", "经济和金融专业人员",
        "Economic & Finance Professionals", 2, "专业技术人员",
        "从事经济分析、金融业务、会计审计等工作的专业人员", "high", False, False,
        typical_roles=["会计师", "审计师", "证券分析师", "银行信贷员"]),
    OccupationCategory("2-07", "GBM 20700", "监察、法律、社会和宗教专业人员",
        "Supervision, Legal, Social & Religious Professionals", 2, "专业技术人员",
        "从事监察、法律、社会工作、宗教事务的专业人员", "high", False, False,
        typical_roles=["律师", "法官", "检察官", "社会工作师"]),
    OccupationCategory("2-08", "GBM 20800", "教学人员",
        "Teaching Professionals", 2, "专业技术人员",
        "从事各级各类教育教学工作的专业人员", "medium", False, False,
        typical_roles=["大学教师", "中小学教师", "幼教", "培训机构讲师"]),
    OccupationCategory("2-09", "GBM 20900", "文学艺术、体育专业人员",
        "Literature, Arts & Sports Professionals", 2, "专业技术人员",
        "从事文学创作、艺术表演、体育训练比赛等工作的专业人员", "medium", False, False,
        typical_roles=["作家", "演员", "画家", "运动员", "教练"]),
    OccupationCategory("2-10", "GBM 21000", "新闻出版、文化专业人员",
        "Journalism, Publishing & Culture Professionals", 2, "专业技术人员",
        "从事新闻采编、出版发行、档案图书文博等工作的专业人员", "medium", False, False,
        typical_roles=["记者", "编辑", "图书管理员", "博物馆员"]),
    OccupationCategory("2-99", "GBM 29900", "其他专业技术人员",
        "Other Professionals", 2, "专业技术人员",
        "不属于上述中类的其他专业技术人员", "medium", False, False,
        typical_roles=[]),

    # ===== 第三大类 GBM 30000: 办事人员和有关人员 =====
    OccupationCategory("3-01", "GBM 30100", "行政办事及辅助人员",
        "Administrative Clerks", 3, "办事人员和有关人员",
        "从事行政办公、公文处理、后勤保障等事务的人员", "medium", False, False,
        typical_roles=["行政专员", "文秘", "档案管理员", "前台"]),
    OccupationCategory("3-02", "GBM 30200", "安全和消防及辅助人员",
        "Security & Firefighting Personnel", 3, "办事人员和有关人员",
        "从事公共安全、消防、应急救援等工作的人员", "high", False, False,
        typical_roles=["警察", "消防员", "安保人员", "应急救援员"]),
    OccupationCategory("3-03", "GBM 30300", "法律事务及辅助人员",
        "Legal Affairs Personnel", 3, "办事人员和有关人员",
        "从事法律辅助事务的人员，如书记员、法警等", "medium", False, False,
        typical_roles=["书记员", "法警", "法律助理"]),
    OccupationCategory("3-99", "GBM 39900", "其他办事人员和有关人员",
        "Other Clerks", 3, "办事人员和有关人员",
        "不属于上述中类的其他办事人员", "medium", False, False,
        typical_roles=[]),

    # ===== 第四大类 GBM 40000: 社会生产服务和生活服务人员 =====
    OccupationCategory("4-01", "GBM 40100", "批发与零售服务人员",
        "Wholesale & Retail Service Personnel", 4, "社会生产服务和生活服务人员",
        "从事商品批发、零售、购销等服务的人员", "medium", False, False,
        typical_roles=["销售员", "收银员", "导购", "电商运营"]),
    OccupationCategory("4-02", "GBM 40200", "交通运输、仓储物流和邮政业服务人员",
        "Transport, Logistics & Postal Service Personnel", 4, "社会生产服务和生活服务人员",
        "从事客货运输、仓储配送、邮政快递等服务的人员", "high", False, False,
        typical_roles=["司机", "快递员", "仓库管理员", "物流专员"]),
    OccupationCategory("4-03", "GBM 40300", "住宿和餐饮服务人员",
        "Accommodation & Catering Service Personnel", 4, "社会生产服务和生活服务人员",
        "从事酒店住宿、餐饮制作与服务的人员", "medium", False, False,
        typical_roles=["厨师", "服务员", "酒店前台", "店长"]),
    OccupationCategory("4-04", "GBM 40400", "信息传输、软件和信息技术服务人员",
        "IT & Software Service Personnel", 4, "社会生产服务和生活服务人员",
        "从事通信、互联网、软件技术等服务的人员", "high", True, False,
        typical_roles=["网络工程师", "数据分析师", "IT运维", "客服代表"]),
    OccupationCategory("4-05", "GBM 40500", "金融服务人员",
        "Financial Service Personnel", 4, "社会生产服务和生活服务人员",
        "从事银行、证券、保险等金融服务的人员", "high", False, False,
        typical_roles=["银行柜员", "保险代理人", "证券经纪人", "理财顾问"]),
    OccupationCategory("4-06", "GBM 40600", "房地产服务人员",
        "Real Estate Service Personnel", 4, "社会生产服务和生活服务人员",
        "从事房地产经纪、物业管理等服务的人员", "medium", False, False,
        typical_roles=["房产经纪人", "物业管理员", "房地产估价师"]),
    OccupationCategory("4-07", "GBM 40700", "租赁和商务服务人员",
        "Rental & Business Service Personnel", 4, "社会生产服务和生活服务人员",
        "从事设备租赁、法律服务、会计服务、企业管理咨询等服务的人员", "medium", False, False,
        typical_roles=["保安", "保洁", "猎头顾问", "咨询顾问"]),
    OccupationCategory("4-08", "GBM 40800", "技术辅助服务人员",
        "Technical Support Service Personnel", 4, "社会生产服务和生活服务人员",
        "从事测绘、检验检测、环境监测等技术辅助服务的人员", "medium", False, False,
        typical_roles=["检验员", "测绘员", "环境监测员", "实验员"]),
    OccupationCategory("4-09", "GBM 40900", "水利、环境和公共设施管理服务人员",
        "Water, Environment & Public Facility Service Personnel", 4, "社会生产服务和生活服务人员",
        "从事水利管理、环境卫生、园林绿化、公共设施管护等服务的人员", "low", False, True,
        typical_roles=["环卫工人", "园林工", "污水处理工", "河道管理员"]),
    OccupationCategory("4-10", "GBM 41000", "居民服务人员",
        "Resident Service Personnel", 4, "社会生产服务和生活服务人员",
        "从事家政、美容美发、洗浴、殡葬等居民生活服务的人员", "low", False, False,
        typical_roles=["家政服务员", "美发师", "美容师", "殡仪服务员"]),
    OccupationCategory("4-11", "GBM 41100", "电力、燃气及水供应服务人员",
        "Electricity, Gas & Water Supply Service Personnel", 4, "社会生产服务和生活服务人员",
        "从事电力、燃气、水的供应服务及抄表收费等工作的人员", "low", False, False,
        typical_roles=["抄表员", "收费员", "燃气检修员"]),
    OccupationCategory("4-12", "GBM 41200", "修理及制作服务人员",
        "Repair & Manufacturing Service Personnel", 4, "社会生产服务和生活服务人员",
        "从事各类设备、器具的修理及手工制作服务的人员", "medium", False, False,
        typical_roles=["家电维修工", "汽车修理工", "钟表修理工", "缝纫工"]),
    OccupationCategory("4-13", "GBM 41300", "文化和教育服务人员",
        "Culture & Education Service Personnel", 4, "社会生产服务和生活服务人员",
        "从事图书档案、群众文化、教育培训辅助等服务的人员", "medium", False, False,
        typical_roles=["图书管理员", "导游", "讲解员", "教务人员"]),
    OccupationCategory("4-14", "GBM 41400", "健康、体育和休闲服务人员",
        "Health, Sports & Recreation Service Personnel", 4, "社会生产服务和生活服务人员",
        "从事健身指导、休闲娱乐、健康管理、养老服务等服务的人员", "medium", False, False,
        typical_roles=["健身教练", "养老护理员", "足疗师", "游乐设施操作员"]),
    OccupationCategory("4-99", "GBM 49900", "其他社会生产服务和生活服务人员",
        "Other Service Personnel", 4, "社会生产服务和生活服务人员",
        "不属于上述中类的其他社会生产服务和生活服务人员", "medium", False, False,
        typical_roles=[]),

    # ===== 第五大类 GBM 50000: 农、林、牧、渔业生产及辅助人员 =====
    OccupationCategory("5-01", "GBM 50100", "农业生产人员",
        "Agricultural Producers", 5, "农、林、牧、渔业生产及辅助人员",
        "从事谷物、蔬菜、水果等农作物种植生产的人员", "low", False, False,
        typical_roles=["农民", "种植户", "农场工人"]),
    OccupationCategory("5-02", "GBM 50200", "林业生产人员",
        "Forestry Producers", 5, "农、林、牧、渔业生产及辅助人员",
        "从事林木培育、森林管护等林业生产的人员", "low", False, True,
        typical_roles=["林农", "护林员", "育苗工"]),
    OccupationCategory("5-03", "GBM 50300", "畜牧业生产人员",
        "Animal Husbandry Producers", 5, "农、林、牧、渔业生产及辅助人员",
        "从事畜禽养殖、畜牧生产的人员", "low", False, False,
        typical_roles=["养殖户", "畜牧工人", "兽医辅助"]),
    OccupationCategory("5-04", "GBM 50400", "渔业生产人员",
        "Fishery Producers", 5, "农、林、牧、渔业生产及辅助人员",
        "从事水产养殖、捕捞等渔业生产的人员", "low", False, False,
        typical_roles=["渔民", "水产养殖员"]),
    OccupationCategory("5-05", "GBM 50500", "农、林、牧、渔业生产辅助人员",
        "Agricultural Support Personnel", 5, "农、林、牧、渔业生产及辅助人员",
        "从事农产品初加工、农机操作等农林牧渔辅助生产的人员", "low", False, False,
        typical_roles=["农机手", "农产品加工员", "灌溉管理员"]),
    OccupationCategory("5-99", "GBM 59900", "其他农、林、牧、渔业生产及辅助人员",
        "Other Agricultural Personnel", 5, "农、林、牧、渔业生产及辅助人员",
        "不属于上述中类的其他农业从业人员", "low", False, False,
        typical_roles=[]),

    # ===== 第六大类 GBM 60000: 生产制造及有关人员 =====
    OccupationCategory("6-01", "GBM 60100", "农副产品加工人员",
        "Agricultural By-product Processors", 6, "生产制造及有关人员",
        "从事粮食、油脂、肉类、乳品等农副产品加工的人员", "medium", False, False,
        typical_roles=["粮油加工工", "屠宰工", "乳品加工工"]),
    OccupationCategory("6-02", "GBM 60200", "食品、饮料生产加工人员",
        "Food & Beverage Producers", 6, "生产制造及有关人员",
        "从事烘焙食品、糖果、饮料、酿酒等生产加工的人员", "medium", False, False,
        typical_roles=["面包师", "酿酒工", "饮料罐装工"]),
    OccupationCategory("6-03", "GBM 60300", "烟草及其制品加工人员",
        "Tobacco Product Processors", 6, "生产制造及有关人员",
        "从事烟草加工和卷烟生产的人员", "medium", False, False,
        typical_roles=["烟叶调制工", "卷烟卷接工"]),
    OccupationCategory("6-04", "GBM 60400", "纺织、针织、印染人员",
        "Textile, Knitting & Dyeing Workers", 6, "生产制造及有关人员",
        "从事纺织、针织、染色、印花等生产加工的人员", "medium", False, False,
        typical_roles=["纺织工", "印染工", "挡车工"]),
    OccupationCategory("6-05", "GBM 60500", "纺织品、服装和皮革、毛皮制品加工制作人员",
        "Textile, Garment & Leather Product Makers", 6, "生产制造及有关人员",
        "从事服装裁剪缝纫、皮革/毛皮加工等制作的人员", "medium", False, False,
        typical_roles=["缝纫工", "制鞋工", "服装打版师"]),
    OccupationCategory("6-06", "GBM 60600", "木材加工、家具与木制品制作人员",
        "Wood Processing & Furniture Makers", 6, "生产制造及有关人员",
        "从事木材加工、人造板制造、家具制作的人员", "medium", False, False,
        typical_roles=["木工", "家具制造工", "木材干燥工"]),
    OccupationCategory("6-07", "GBM 60700", "纸及纸制品生产加工人员",
        "Paper & Paper Product Makers", 6, "生产制造及有关人员",
        "从事纸浆制造、造纸、纸制品加工的人员", "medium", False, False,
        typical_roles=["造纸工", "纸箱工", "纸浆工"]),
    OccupationCategory("6-08", "GBM 60800", "印刷和记录媒介复制人员",
        "Printing & Recording Media Reproduction Workers", 6, "生产制造及有关人员",
        "从事印刷、制版、装订、记录媒介复制的人员", "medium", False, False,
        typical_roles=["印刷工", "制版工", "装订工"]),
    OccupationCategory("6-09", "GBM 60900", "文教、工美、体育和娱乐用品制造人员",
        "Cultural, Arts & Sports Goods Makers", 6, "生产制造及有关人员",
        "从事文具、工艺品、乐器、玩具、体育用品等制造的人员", "medium", False, False,
        typical_roles=["工艺美术师", "玩具制造工", "乐器制作工"]),
    OccupationCategory("6-10", "GBM 61000", "石油加工和炼焦、煤化工生产人员",
        "Petroleum Processing & Coking Workers", 6, "生产制造及有关人员",
        "从事石油炼制、炼焦、煤化工生产操作的人员", "medium", False, False,
        typical_roles=["炼油工", "焦化工", "煤化工操作员"]),
    OccupationCategory("6-11", "GBM 61100", "化学原料和化学制品制造人员",
        "Chemical Raw Material & Product Makers", 6, "生产制造及有关人员",
        "从事基础化学原料、化肥、农药、涂料等制造的人员", "medium", False, False,
        typical_roles=["化工操作工", "化验员", "涂料生产工"]),
    OccupationCategory("6-12", "GBM 61200", "医药制造人员",
        "Pharmaceutical Product Makers", 6, "生产制造及有关人员",
        "从事化学药品、中药、生物制品等制造的人员", "medium", False, False,
        typical_roles=["制药工", "中药炮制工", "疫苗生产工"]),
    OccupationCategory("6-13", "GBM 61300", "化学纤维制造人员",
        "Chemical Fiber Makers", 6, "生产制造及有关人员",
        "从事化学纤维生产制造的人员", "medium", False, False,
        typical_roles=["化纤纺丝工", "化纤后处理工"]),
    OccupationCategory("6-14", "GBM 61400", "橡胶和塑料制品制造人员",
        "Rubber & Plastic Product Makers", 6, "生产制造及有关人员",
        "从事轮胎、胶管、塑料制品等生产制造的人员", "medium", False, False,
        typical_roles=["橡胶炼胶工", "塑料注塑工", "硫化工"]),
    OccupationCategory("6-15", "GBM 61500", "非金属矿物制品制造人员",
        "Non-metallic Mineral Product Makers", 6, "生产制造及有关人员",
        "从事水泥、玻璃、陶瓷、砖瓦等非金属矿物制品制造的人员", "medium", False, False,
        typical_roles=["水泥生产工", "玻璃熔化工", "陶瓷烧成工"]),
    OccupationCategory("6-16", "GBM 61600", "采矿人员",
        "Mining Workers", 6, "生产制造及有关人员",
        "从事煤炭、金属、非金属等矿产资源开采作业的人员", "high", False, False,
        typical_roles=["采矿工", "掘进工", "通风工", "矿山安全员"]),
    OccupationCategory("6-17", "GBM 61700", "金属冶炼和压延加工人员",
        "Metal Smelting & Rolling Workers", 6, "生产制造及有关人员",
        "从事黑色和有色金属冶炼、轧制等加工的人员", "medium", False, False,
        typical_roles=["炼钢工", "轧钢工", "铸造工", "热处理工"]),
    OccupationCategory("6-18", "GBM 61800", "机械制造基础加工人员",
        "Basic Machinery Manufacturing Workers", 6, "生产制造及有关人员",
        "从事机械冷加工、热加工、表面处理等基础加工的人员", "medium", False, False,
        typical_roles=["车工", "铣工", "焊工", "钳工", "数控操作工"]),
    OccupationCategory("6-19", "GBM 61900", "金属制品制造人员",
        "Metal Product Makers", 6, "生产制造及有关人员",
        "从事结构性金属制品、金属工具等制造的人员", "medium", False, False,
        typical_roles=["钣金工", "铆工", "金属构件工"]),
    OccupationCategory("6-20", "GBM 62000", "通用设备制造人员",
        "General Equipment Makers", 6, "生产制造及有关人员",
        "从事锅炉、发动机、泵阀等通用设备制造的人员", "medium", False, False,
        typical_roles=["锅炉设备制造工", "泵阀装配工", "压缩机工"]),
    OccupationCategory("6-21", "GBM 62100", "专用设备制造人员",
        "Specialized Equipment Makers", 6, "生产制造及有关人员",
        "从事矿山、冶金、化工、纺织等专用设备制造的人员", "medium", False, False,
        typical_roles=["矿山设备制造工", "纺织设备保全工"]),
    OccupationCategory("6-22", "GBM 62200", "汽车制造人员",
        "Automobile Manufacturing Workers", 6, "生产制造及有关人员",
        "从事汽车整车及零部件制造的人员", "medium", False, False,
        typical_roles=["汽车装配工", "汽车焊装工", "涂装工"]),
    OccupationCategory("6-23", "GBM 62300", "铁路、船舶、航空设备制造人员",
        "Railway, Ship & Aircraft Manufacturing Workers", 6, "生产制造及有关人员",
        "从事铁路机车车辆、船舶、航空航天器制造的人员", "medium", False, False,
        typical_roles=["船舶装配工", "航空装配工", "铁路车辆工"]),
    OccupationCategory("6-24", "GBM 62400", "电气机械和器材制造人员",
        "Electrical Machinery & Equipment Makers", 6, "生产制造及有关人员",
        "从事电机、变压器、电池、家用电器等电气设备制造的人员", "medium", False, False,
        typical_roles=["电机装配工", "电池制造工", "家电装配工"]),
    OccupationCategory("6-25", "GBM 62500", "计算机、通信和其他电子设备制造人员",
        "Computer, Communication & Electronic Equipment Makers", 6, "生产制造及有关人员",
        "从事计算机、通信设备、电子元器件等制造的人员", "medium", True, False,
        typical_roles=["电子装配工", "半导体芯片工", "SMT操作工"]),
    OccupationCategory("6-26", "GBM 62600", "仪器仪表制造人员",
        "Instrument & Meter Makers", 6, "生产制造及有关人员",
        "从事工业自动化仪表、电子测量仪器等制造的人员", "medium", False, False,
        typical_roles=["仪器装配工", "仪表调试工"]),
    OccupationCategory("6-27", "GBM 62700", "再生资源综合利用人员",
        "Renewable Resource Utilization Workers", 6, "生产制造及有关人员",
        "从事废旧物资回收、再生资源加工利用的人员", "low", False, True,
        typical_roles=["再生资源回收工", "废料加工工"]),
    OccupationCategory("6-28", "GBM 62800", "电力、热力、气体、水生产和输配人员",
        "Power, Heat, Gas & Water Production Workers", 6, "生产制造及有关人员",
        "从事发电、输配电、供热、供气、供水及处理的人员", "medium", False, False,
        typical_roles=["发电运行工", "输电运检工", "变电站值班员"]),
    OccupationCategory("6-29", "GBM 62900", "建筑施工人员",
        "Construction Workers", 6, "生产制造及有关人员",
        "从事房屋建筑、土木工程、装饰装修等施工的人员", "high", False, False,
        typical_roles=["砌筑工", "钢筋工", "混凝土工", "架子工", "装修工"]),
    OccupationCategory("6-30", "GBM 63000", "运输设备和通用工程机械操作人员及有关人员",
        "Transport & Engineering Equipment Operators", 6, "生产制造及有关人员",
        "从事起重机械、挖掘机、叉车等工程机械操作的人员", "medium", False, False,
        typical_roles=["起重机司机", "叉车工", "挖掘机司机", "塔吊司机"]),
    OccupationCategory("6-31", "GBM 63100", "生产辅助人员",
        "Production Support Workers", 6, "生产制造及有关人员",
        "从事包装、仓储、搬运等生产辅助工作的人员", "low", False, False,
        typical_roles=["包装工", "搬运工", "仓库保管员", "质检员"]),
    OccupationCategory("6-99", "GBM 69900", "其他生产制造及有关人员",
        "Other Manufacturing Workers", 6, "生产制造及有关人员",
        "不属于上述中类的其他生产制造人员", "medium", False, False,
        typical_roles=[]),

    # ===== 第七大类 GBM 70000: 军队人员 =====
    OccupationCategory("7-01", "GBM 70100", "军官(警官)",
        "Military & Police Officers", 7, "军队人员",
        "在军队和武装警察部队中担任军官职务的人员", "high", False, False,
        typical_roles=["军官", "武警警官"]),
    OccupationCategory("7-02", "GBM 70200", "军士(警士)",
        "Non-commissioned Officers", 7, "军队人员",
        "在军队和武装警察部队中担任军士职务的人员", "high", False, False,
        typical_roles=["军士长", "警士"]),
    OccupationCategory("7-03", "GBM 70300", "义务兵",
        "Conscripts", 7, "军队人员",
        "按照兵役法服义务兵役的人员", "high", False, False,
        typical_roles=["义务兵"]),
    OccupationCategory("7-04", "GBM 70400", "文职人员",
        "Civilian Staff in Military", 7, "军队人员",
        "在军队工作的非现役文职人员", "medium", False, False,
        typical_roles=["军队文职"]),

    # ===== 第八大类 GBM 80000: 不便分类的其他从业人员 =====
    OccupationCategory("8-00", "GBM 80000", "不便分类的其他从业人员",
        "Unclassified Workers", 8, "不便分类的其他从业人员",
        "不属于上述各类的其他从业人员", "medium", False, False,
        typical_roles=["自由职业者", "灵活就业人员"]),
]


# =====================================================================
# 查找与辅助函数
# =====================================================================

# 按大类分组
OCCUPATIONS_BY_MAJOR: dict[int, list[OccupationCategory]] = {}
for occ in OCCUPATIONS:
    OCCUPATIONS_BY_MAJOR.setdefault(occ.major_category, []).append(occ)


def get_occupation_by_code(code: str) -> OccupationCategory | None:
    """按中类编号查找"""
    for occ in OCCUPATIONS:
        if occ.code == code:
            return occ
    return None


def get_occupations_by_major(major: int) -> list[OccupationCategory]:
    """按大类编号获取所有中类"""
    return OCCUPATIONS_BY_MAJOR.get(major, [])


def get_filtered_occupations(major_filter: list[int] | None = None,
                              stress_filter: list[str] | None = None,
                              digital_only: bool = False,
                              green_only: bool = False) -> list[OccupationCategory]:
    """按条件筛选职业中类"""
    result = list(OCCUPATIONS)
    if major_filter:
        result = [o for o in result if o.major_category in major_filter]
    if stress_filter:
        result = [o for o in result if o.stress_level in stress_filter]
    if digital_only:
        result = [o for o in result if o.is_digital]
    if green_only:
        result = [o for o in result if o.is_green]
    return result


def get_default_occupation_weights() -> dict[int, float]:
    """默认职业大类采样权重
    
    大类2(专业技术)、4(生活服务)、6(生产制造)权重最高，
    因为这些大类覆盖了绝大多数劳动人口。
    大类1(党政机关)、7(军人)权重较低。
    大类8(不便分类)最低。
    """
    return {
        1: 0.05,   # 党政机关负责人 — 比例较小
        2: 0.30,   # 专业技术人员 — 高权重
        3: 0.10,   # 办事人员
        4: 0.25,   # 社会生产服务和生活服务人员 — 高权重
        5: 0.08,   # 农林牧渔
        6: 0.18,   # 生产制造 — 高权重
        7: 0.02,   # 军人 — 小比例
        8: 0.02,   # 其他
    }


def list_occupations_summary() -> str:
    """生成职业分类概览文本"""
    lines = ["职业分类总览（《中华人民共和国职业分类大典(2022年版)》79中类）", "=" * 60]
    for major in sorted(OCCUPATIONS_BY_MAJOR.keys()):
        major_name = OCCUPATIONS_BY_MAJOR[major][0].major_name
        cats = OCCUPATIONS_BY_MAJOR[major]
        lines.append(f"\n第{major}大类：{major_name}（{len(cats)}中类）")
        for occ in cats:
            flags = ""
            if occ.is_digital: flags += " [S数字]"
            if occ.is_green: flags += " [L绿色]"
            lines.append(f"  {occ.code} {occ.name_cn}{flags}")
    return "\n".join(lines)
