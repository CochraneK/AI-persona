"""International demographics sampler — 供全人类各行各业可用的多国语境底座.

Produces a coherent "demographics context" (continent / country / language /
cultural region / religion / ethnicity / name / urbanicity / income band) for
each generated persona, so the pool is genuinely international rather than
China-only.  Pure stdlib, deterministic under a given RNG.

Design notes
------------
- Countries are weighted by (approximate) share of world population so the
  5000+ pool skews realistically (India/China/Nigeria large, small states rare).
- Each country maps to a CULTURAL_REGION that determines the name pool,
  primary language, religion distribution and typical ethnicity.
- Name pools are full given+family names (no surname/given assembly) so the
  sampled "name" is always a plausible complete name.
"""
from __future__ import annotations

import random
from typing import Any

# =====================================================================
# 文化区 (name pools + language + religion priors + typical ethnicity)
# =====================================================================
# Each region:
#   label_cn / label_en : display label
#   male / female       : list of complete names
#   langs               : (primary_language_cn, primary_language_en, [extra L2 options])
#   religions           : dict {religion_cn: weight}  (sums ~1.0)
#   ethnicity           : typical ethnic/cultural label (Chinese)

CULTURAL_REGIONS: dict[str, dict[str, Any]] = {
    "chinese": {
        "label_cn": "东亚·汉",
        "label_en": "East Asian (Han)",
        "male": ["张伟", "王强", "李磊", "刘军", "陈杰", "杨涛", "赵明", "黄华",
                 "周建国", "吴国栋", "徐文斌", "孙立斌", "马超", "朱永刚",
                 "胡俊杰", "郭志远", "林晨曦", "何建军", "高翔", "罗浩然"],
        "female": ["王芳", "李娜", "张静", "刘丽", "陈敏", "杨秀英", "赵雪",
                   "黄燕", "周艳", "吴娟", "徐梅", "孙玲", "马婷婷", "朱雪梅",
                   "胡琳", "郭晓燕", "林雨欣", "何佳琪", "高梦洁", "罗诗涵"],
        "langs": ("中文", "Mandarin Chinese", ["英语"]),
        "religions": {"佛教": 0.16, "道教": 0.05, "民间信仰": 0.22,
                       "无宗教": 0.50, "伊斯兰教": 0.04, "基督教": 0.03},
        "ethnicity": "汉族",
    },
    "japanese": {
        "label_cn": "东亚·日本",
        "label_en": "Japanese",
        "male": ["Tanaka Kenji", "Sato Hiroshi", "Suzuki Takashi", "Yamamoto Koji",
                 "Watanabe Masato", "Nakamura Taro", "Kobayashi Daisuke",
                 "Kato Yoshinori", "Ito Naoki", "Fujita Shu", "Mori Daisuke",
                 "Inoue Keisuke"],
        "female": ["Tanaka Yuki", "Sato Sakura", "Suzuki Aiko", "Yamamoto Haruka",
                   "Watanabe Miyu", "Nakamura Rin", "Kobayashi Hana", "Kato Sora",
                   "Ito Miku", "Fujita Nao", "Mori Akane", "Inoue Riko"],
        "langs": ("日语", "Japanese", ["英语"]),
        "religions": {"神道教": 0.40, "佛教": 0.50, "无宗教": 0.05, "基督教": 0.05},
        "ethnicity": "大和民族",
    },
    "korean": {
        "label_cn": "东亚·韩国",
        "label_en": "Korean",
        "male": ["Kim Minjun", "Lee Jihun", "Park Seongho", "Choi Taeyang",
                 "Jung Hyeonjoong", "Kang Wooyeol", "Kim Daeho", "Lee Sangwoo",
                 "Park Yoonsang", "Choi Jinho", "Shin Jiho", "Han Sangjin"],
        "female": ["Kim Sooyeon", "Lee Mirae", "Park Hyejin", "Choi Jieun",
                   "Jung Sohyun", "Kang Eunbi", "Kim Hana", "Lee Yoojin",
                   "Park Minseo", "Choi Daehun", "Shin Jihye", "Han Soji"],
        "langs": ("韩语", "Korean", ["英语"]),
        "religions": {"无宗教": 0.55, "佛教": 0.17, "基督教": 0.20, "其他": 0.08},
        "ethnicity": "朝鲜族",
    },
    "south_asian": {
        "label_cn": "南亚·印度",
        "label_en": "South Asian (Indian)",
        "male": ["Rajesh Kumar", "Arun Sharma", "Vikram Singh", "Anil Gupta",
                 "Suresh Patel", "Ramesh Iyer", "Deepak Reddy", "Sanjay Mehta",
                 "Rohan Das", "Amit Joshi", "Manoj Nair", "Girish Kumar"],
        "female": ["Priya Sharma", "Anjali Gupta", "Sunita Singh", "Kavita Patel",
                   "Meera Iyer", "Lakshmi Reddy", "Pooja Mehta", "Nisha Das",
                   "Ritu Joshi", "Divya Sharma", "Sneha Nair", "Kiran Kumar"],
        "langs": ("印地语", "Hindi", ["英语", "泰米尔语", "泰卢固语"]),
        "religions": {"印度教": 0.80, "伊斯兰教": 0.13, "锡克教": 0.02,
                       "基督教": 0.03, "佛教": 0.01},
        "ethnicity": "印度裔",
    },
    "southeast_asian": {
        "label_cn": "东南亚",
        "label_en": "Southeast Asian",
        "male": ["Minh Nguyen", "Duc Tran", "Somchai Prasert", "Budi Santoso",
                 "Jose Santos", "Rafael Cruz", "Arif Rahman", "Wei Lim",
                 "Tien Pham", "Agus Wijaya"],
        "female": ["Linh Nguyen", "Mai Tran", "Somsri Prasert", "Siti Santoso",
                   "Ana Santos", "Grace Cruz", "Ayu Rahman", "Mei Lim",
                   "Huong Pham", "Dewi Wijaya"],
        "langs": ("越南语", "Vietnamese", ["印尼语", "泰语", "他加禄语", "英语"]),
        "religions": {"佛教": 0.45, "伊斯兰教": 0.30, "基督教": 0.20, "民间信仰": 0.05},
        "ethnicity": "东南亚各族",
    },
    "west_asian": {
        "label_cn": "西亚·中东",
        "label_en": "West Asian / Middle East",
        "male": ["Ahmed Hassan", "Muhammad Ali", "Omar Farouk", "Khalid Ibrahim",
                 "Yusuf Rahman", "Tariq Aziz", "Hassan Mahmoud", "Karim Nasser",
                 "Samir Haddad", "Nabil Qureshi", "Faisal Khalil", "Rashid Amin"],
        "female": ["Fatima Hassan", "Amina Ali", "Layla Farouk", "Sara Ibrahim",
                   "Nour Rahman", "Huda Aziz", "Amal Mahmoud", "Rania Nasser",
                   "Dina Haddad", "Maha Qureshi", "Yasmin Khalil", "Sana Amin"],
        "langs": ("阿拉伯语", "Arabic", ["英语", "波斯语", "土耳其语"]),
        "religions": {"伊斯兰教": 0.90, "基督教": 0.05, "犹太教": 0.02,
                       "其他": 0.03},
        "ethnicity": "阿拉伯族/波斯族/土耳其族",
    },
    "central_asian": {
        "label_cn": "中亚",
        "label_en": "Central Asian",
        "male": ["Temur Bekov", "Alikhan Nurlan", "Rustam Karimov",
                 "Jasur Rahimov", "Bolat Serik", "Daniyar Aliyev"],
        "female": ["Aigul Bekova", "Dinara Nurlanova", "Gulnara Karimova",
                   "Madina Rahimova", "Aruzhan Serik", "Layla Aliyeva"],
        "langs": ("哈萨克语", "Kazakh", ["俄语", "乌兹别克语"]),
        "religions": {"伊斯兰教": 0.88, "无宗教": 0.08, "东正教": 0.04},
        "ethnicity": "中亚突厥族",
    },
    "african_sub_saharan": {
        "label_cn": "撒哈拉以南非洲",
        "label_en": "Sub-Saharan African",
        "male": ["Kwame Mensah", "Chidi Okafor", "Jabari Hassan", "Tendai Moyo",
                 "Kofi Asante", "Emeka Obi", "Samuel Kato", "Ibrahim Diallo",
                 "Musa Traore", "David Okonkwo"],
        "female": ["Ama Mensah", "Adaeze Okafor", "Zanele Moyo", "Efua Asante",
                   "Nkechi Obi", "Akinyi Kato", "Aminata Diallo", "Fatou Ndiaye",
                   "Aisha Traore", "Blessing Okonkwo"],
        "langs": ("斯瓦希里语", "Swahili", ["英语", "约鲁巴语", "豪萨语"]),
        "religions": {"基督教": 0.55, "伊斯兰教": 0.25, "民间信仰": 0.15,
                       "其他": 0.05},
        "ethnicity": "非洲各族",
    },
    "north_african": {
        "label_cn": "北非·马格里布",
        "label_en": "North African (Maghreb)",
        "male": ["Mohamed Benali", "Ahmed El Amrani", "Karim Haddad",
                 "Youssef Benkirane", "Omar El Fassi", "Hassan El Idrissi",
                 "Anas Bakkali", "Said Mansouri"],
        "female": ["Fatima Benali", "Amina El Amrani", "Salma Haddad",
                   "Nadia Benkirane", "Yasmine El Fassi", "Khadija El Idrissi",
                   "Imane Bakkali", "Meriem Mansouri"],
        "langs": ("阿拉伯语", "Arabic", ["法语", "柏柏尔语"]),
        "religions": {"伊斯兰教": 0.98, "基督教": 0.01, "其他": 0.01},
        "ethnicity": "阿拉伯-柏柏尔族",
    },
    "western_european": {
        "label_cn": "西欧",
        "label_en": "Western European",
        "male": ["James Wilson", "Thomas Muller", "Pierre Dubois",
                 "Carlos Garcia", "Marco Rossi", "Joao Silva", "Lucas Weber",
                 "Antoine Martin", "Diego Fernandez", "Luca Bianchi",
                 "Lars Nielsen", "Jan de Vries"],
        "female": ["Emily Brown", "Anna Muller", "Marie Dubois", "Maria Garcia",
                   "Giulia Rossi", "Ana Silva", "Sophie Weber", "Claire Martin",
                   "Lucia Fernandez", "Chiara Bianchi", "Freja Nielsen",
                   "Eva de Vries"],
        "langs": ("英语", "English", ["德语", "法语", "西班牙语", "意大利语"]),
        "religions": {"基督教": 0.50, "无宗教": 0.35, "伊斯兰教": 0.08,
                       "其他": 0.07},
        "ethnicity": "西欧各族",
    },
    "eastern_european": {
        "label_cn": "东欧",
        "label_en": "Eastern European",
        "male": ["Ivan Petrov", "Marek Novak", "Andrei Ivanov", "Jakub Kowalski",
                 "Petru Popescu", "Nikolai Sokolov", "Viktor Horvat",
                 "Mihai Constantin"],
        "female": ["Olga Petrova", "Jana Novakova", "Anna Ivanova",
                   "Katarzyna Kowalska", "Elena Popescu", "Maria Sokolova",
                   "Ivana Horvat", "Ioana Constantin"],
        "langs": ("俄语", "Russian", ["波兰语", "捷克语", "罗马尼亚语"]),
        "religions": {"东正教": 0.55, "基督教": 0.25, "无宗教": 0.15,
                       "其他": 0.05},
        "ethnicity": "东欧各族",
    },
    "latin_american": {
        "label_cn": "拉丁美洲",
        "label_en": "Latin American",
        "male": ["Carlos Rodriguez", "Miguel Garcia", "Diego Fernandez",
                 "Jose Ramirez", "Andres Morales", "Rafael Castillo",
                 "Pablo Herrera", "Eduardo Vargas", "Alejandro Santos",
                 "Cristian Torres", "Fernando Diaz", "Luis Romero"],
        "female": ["Maria Rodriguez", "Lucia Garcia", "Camila Fernandez",
                   "Valentina Ramirez", "Sofia Morales", "Isabella Castillo",
                   "Fernanda Herrera", "Ana Vargas", "Daniela Santos",
                   "Mariana Torres", "Gabriela Diaz", "Paula Romero"],
        "langs": ("西班牙语", "Spanish", ["葡萄牙语", "英语"]),
        "religions": {"基督教": 0.75, "无宗教": 0.18, "其他": 0.07},
        "ethnicity": "拉美各族",
    },
    "north_american": {
        "label_cn": "北美·英语",
        "label_en": "North American (English)",
        "male": ["Michael Johnson", "David Smith", "Robert Brown", "James Wilson",
                 "Christopher Davis", "Daniel Martinez", "Matthew Garcia",
                 "Andrew Miller", "Kevin Anderson", "Ryan Thomas", "Brian Moore",
                 "Jason Taylor"],
        "female": ["Sarah Johnson", "Emily Smith", "Jessica Brown", "Ashley Wilson",
                   "Amanda Davis", "Megan Martinez", "Rachel Garcia", "Lauren Miller",
                   "Brittany Anderson", "Stephanie Thomas", "Nicole Moore",
                   "Amber Taylor"],
        "langs": ("英语", "English", ["西班牙语"]),
        "religions": {"基督教": 0.60, "无宗教": 0.25, "其他": 0.10,
                       "伊斯兰教": 0.03, "犹太教": 0.02},
        "ethnicity": "北美各族",
    },
    "oceania": {
        "label_cn": "大洋洲",
        "label_en": "Oceanian",
        "male": ["Jack Thompson", "Ryan Walker", "Oliver Bennett", "William Harris",
                 "James OConnor", "Liam Murphy", "Harry Cooper", "Thomas Wright",
                 "Noah Foster", "Ethan Clark"],
        "female": ["Emma Thompson", "Olivia Walker", "Charlotte Bennett",
                   "Amelia Harris", "Lily OConnor", "Grace Murphy", "Ruby Cooper",
                   "Sophia Wright", "Ivy Foster", "Mia Clark"],
        "langs": ("英语", "English", ["毛利语", "太平洋岛语"]),
        "religions": {"基督教": 0.65, "无宗教": 0.25, "其他": 0.10},
        "ethnicity": "大洋洲各族",
    },
}

# =====================================================================
# 国家 (weighted by approx share of world population)
# =====================================================================
# code / cn / en / continent / region / urban(0..1) / income(low|mid|high) / w(pop weight)
COUNTRIES: list[dict[str, Any]] = [
    # ---- 亚洲 ----
    {"code": "CN", "cn": "中国", "en": "China", "continent": "亚洲", "region": "chinese", "urban": 0.65, "income": "high", "w": 14.1},
    {"code": "IN", "cn": "印度", "en": "India", "continent": "亚洲", "region": "south_asian", "urban": 0.35, "income": "mid", "w": 14.3},
    {"code": "JP", "cn": "日本", "en": "Japan", "continent": "亚洲", "region": "japanese", "urban": 0.92, "income": "high", "w": 1.2},
    {"code": "KR", "cn": "韩国", "en": "South Korea", "continent": "亚洲", "region": "korean", "urban": 0.81, "income": "high", "w": 0.46},
    {"code": "ID", "cn": "印度尼西亚", "en": "Indonesia", "continent": "亚洲", "region": "southeast_asian", "urban": 0.57, "income": "mid", "w": 2.7},
    {"code": "VN", "cn": "越南", "en": "Vietnam", "continent": "亚洲", "region": "southeast_asian", "urban": 0.38, "income": "mid", "w": 1.0},
    {"code": "TH", "cn": "泰国", "en": "Thailand", "continent": "亚洲", "region": "southeast_asian", "urban": 0.52, "income": "mid", "w": 0.7},
    {"code": "PH", "cn": "菲律宾", "en": "Philippines", "continent": "亚洲", "region": "southeast_asian", "urban": 0.48, "income": "mid", "w": 0.85},
    {"code": "MY", "cn": "马来西亚", "en": "Malaysia", "continent": "亚洲", "region": "southeast_asian", "urban": 0.78, "income": "mid", "w": 0.28},
    {"code": "PK", "cn": "巴基斯坦", "en": "Pakistan", "continent": "亚洲", "region": "south_asian", "urban": 0.37, "income": "low", "w": 1.6},
    {"code": "BD", "cn": "孟加拉国", "en": "Bangladesh", "continent": "亚洲", "region": "south_asian", "urban": 0.40, "income": "low", "w": 1.0},
    {"code": "SA", "cn": "沙特阿拉伯", "en": "Saudi Arabia", "continent": "亚洲", "region": "west_asian", "urban": 0.86, "income": "high", "w": 0.24},
    {"code": "IR", "cn": "伊朗", "en": "Iran", "continent": "亚洲", "region": "west_asian", "urban": 0.75, "income": "mid", "w": 0.44},
    {"code": "TR", "cn": "土耳其", "en": "Türkiye", "continent": "亚洲", "region": "west_asian", "urban": 0.77, "income": "mid", "w": 0.66},
    {"code": "IL", "cn": "以色列", "en": "Israel", "continent": "亚洲", "region": "west_asian", "urban": 0.93, "income": "high", "w": 0.09},
    {"code": "KZ", "cn": "哈萨克斯坦", "en": "Kazakhstan", "continent": "亚洲", "region": "central_asian", "urban": 0.60, "income": "mid", "w": 0.07},
    # ---- 欧洲 ----
    {"code": "RU", "cn": "俄罗斯", "en": "Russia", "continent": "欧洲", "region": "eastern_european", "urban": 0.75, "income": "mid", "w": 0.83},
    {"code": "DE", "cn": "德国", "en": "Germany", "continent": "欧洲", "region": "western_european", "urban": 0.78, "income": "high", "w": 0.55},
    {"code": "FR", "cn": "法国", "en": "France", "continent": "欧洲", "region": "western_european", "urban": 0.81, "income": "high", "w": 0.44},
    {"code": "GB", "cn": "英国", "en": "United Kingdom", "continent": "欧洲", "region": "western_european", "urban": 0.84, "income": "high", "w": 0.32},
    {"code": "ES", "cn": "西班牙", "en": "Spain", "continent": "欧洲", "region": "western_european", "urban": 0.82, "income": "high", "w": 0.26},
    {"code": "IT", "cn": "意大利", "en": "Italy", "continent": "欧洲", "region": "western_european", "urban": 0.79, "income": "high", "w": 0.23},
    {"code": "PT", "cn": "葡萄牙", "en": "Portugal", "continent": "欧洲", "region": "western_european", "urban": 0.69, "income": "high", "w": 0.11},
    {"code": "NL", "cn": "荷兰", "en": "Netherlands", "continent": "欧洲", "region": "western_european", "urban": 0.93, "income": "high", "w": 0.11},
    {"code": "PL", "cn": "波兰", "en": "Poland", "continent": "欧洲", "region": "eastern_european", "urban": 0.60, "income": "high", "w": 0.27},
    {"code": "RO", "cn": "罗马尼亚", "en": "Romania", "continent": "欧洲", "region": "eastern_european", "urban": 0.54, "income": "mid", "w": 0.12},
    {"code": "UA", "cn": "乌克兰", "en": "Ukraine", "continent": "欧洲", "region": "eastern_european", "urban": 0.68, "income": "low", "w": 0.15},
    {"code": "GR", "cn": "希腊", "en": "Greece", "continent": "欧洲", "region": "western_european", "urban": 0.79, "income": "mid", "w": 0.07},
    # ---- 非洲 ----
    {"code": "NG", "cn": "尼日利亚", "en": "Nigeria", "continent": "非洲", "region": "african_sub_saharan", "urban": 0.54, "income": "low", "w": 1.3},
    {"code": "EG", "cn": "埃及", "en": "Egypt", "continent": "非洲", "region": "north_african", "urban": 0.43, "income": "low", "w": 0.65},
    {"code": "ZA", "cn": "南非", "en": "South Africa", "continent": "非洲", "region": "african_sub_saharan", "urban": 0.68, "income": "mid", "w": 0.20},
    {"code": "KE", "cn": "肯尼亚", "en": "Kenya", "continent": "非洲", "region": "african_sub_saharan", "urban": 0.29, "income": "low", "w": 0.21},
    {"code": "MA", "cn": "摩洛哥", "en": "Morocco", "continent": "非洲", "region": "north_african", "urban": 0.63, "income": "low", "w": 0.19},
    {"code": "ET", "cn": "埃塞俄比亚", "en": "Ethiopia", "continent": "非洲", "region": "african_sub_saharan", "urban": 0.24, "income": "low", "w": 0.30},
    {"code": "GH", "cn": "加纳", "en": "Ghana", "continent": "非洲", "region": "african_sub_saharan", "urban": 0.58, "income": "low", "w": 0.10},
    {"code": "TZ", "cn": "坦桑尼亚", "en": "Tanzania", "continent": "非洲", "region": "african_sub_saharan", "urban": 0.37, "income": "low", "w": 0.18},
    {"code": "DZ", "cn": "阿尔及利亚", "en": "Algeria", "continent": "非洲", "region": "north_african", "urban": 0.73, "income": "mid", "w": 0.15},
    {"code": "CI", "cn": "科特迪瓦", "en": "Côte d'Ivoire", "continent": "非洲", "region": "african_sub_saharan", "urban": 0.46, "income": "low", "w": 0.12},
    # ---- 北美洲 ----
    {"code": "US", "cn": "美国", "en": "United States", "continent": "北美洲", "region": "north_american", "urban": 0.82, "income": "high", "w": 2.7},
    {"code": "CA", "cn": "加拿大", "en": "Canada", "continent": "北美洲", "region": "north_american", "urban": 0.82, "income": "high", "w": 0.12},
    {"code": "MX", "cn": "墨西哥", "en": "Mexico", "continent": "北美洲", "region": "latin_american", "urban": 0.80, "income": "mid", "w": 1.0},
    {"code": "GT", "cn": "危地马拉", "en": "Guatemala", "continent": "北美洲", "region": "latin_american", "urban": 0.53, "income": "low", "w": 0.11},
    # ---- 南美洲 ----
    {"code": "BR", "cn": "巴西", "en": "Brazil", "continent": "南美洲", "region": "latin_american", "urban": 0.86, "income": "mid", "w": 1.4},
    {"code": "AR", "cn": "阿根廷", "en": "Argentina", "continent": "南美洲", "region": "latin_american", "urban": 0.92, "income": "mid", "w": 0.14},
    {"code": "CO", "cn": "哥伦比亚", "en": "Colombia", "continent": "南美洲", "region": "latin_american", "urban": 0.81, "income": "mid", "w": 0.23},
    {"code": "CL", "cn": "智利", "en": "Chile", "continent": "南美洲", "region": "latin_american", "urban": 0.88, "income": "mid", "w": 0.06},
    {"code": "PE", "cn": "秘鲁", "en": "Peru", "continent": "南美洲", "region": "latin_american", "urban": 0.78, "income": "mid", "w": 0.16},
    {"code": "VE", "cn": "委内瑞拉", "en": "Venezuela", "continent": "南美洲", "region": "latin_american", "urban": 0.87, "income": "mid", "w": 0.07},
    {"code": "EC", "cn": "厄瓜多尔", "en": "Ecuador", "continent": "南美洲", "region": "latin_american", "urban": 0.66, "income": "mid", "w": 0.04},
    # ---- 大洋洲 ----
    {"code": "AU", "cn": "澳大利亚", "en": "Australia", "continent": "大洋洲", "region": "oceania", "urban": 0.86, "income": "high", "w": 0.12},
    {"code": "NZ", "cn": "新西兰", "en": "New Zealand", "continent": "大洋洲", "region": "oceania", "urban": 0.87, "income": "high", "w": 0.01},
    {"code": "FJ", "cn": "斐济", "en": "Fiji", "continent": "大洋洲", "region": "oceania", "urban": 0.43, "income": "mid", "w": 0.001},
]

_COUNTRY_BY_CODE = {c["code"]: c for c in COUNTRIES}
_CONTINENTS = tuple(sorted({c["continent"] for c in COUNTRIES}))

# Per-country primary-language overrides (region default is otherwise used).
# Keeps e.g. Indonesia→Indonesian, Turkey→Turkish, Nigeria→English correct.
LANG_OVERRIDES: dict[str, tuple[str, str]] = {
    "ID": ("印尼语", "Indonesian"), "VN": ("越南语", "Vietnamese"),
    "TH": ("泰语", "Thai"), "PH": ("他加禄语", "Tagalog"),
    "MY": ("马来语", "Malay"), "PK": ("乌尔都语", "Urdu"),
    "BD": ("孟加拉语", "Bengali"), "TR": ("土耳其语", "Turkish"),
    "IL": ("希伯来语", "Hebrew"), "NG": ("英语", "English"),
    "GH": ("英语", "English"), "KE": ("斯瓦希里语", "Swahili"),
    "TZ": ("斯瓦希里语", "Swahili"), "ZA": ("英语", "English"),
    "EG": ("阿拉伯语", "Arabic"), "MA": ("阿拉伯语", "Arabic"),
    "DZ": ("阿拉伯语", "Arabic"), "CI": ("法语", "French"),
    "BR": ("葡萄牙语", "Portuguese"),
    # European country overrides (region default 英语/俄语 does not fit most)
    "DE": ("德语", "German"), "FR": ("法语", "French"),
    "ES": ("西班牙语", "Spanish"), "IT": ("意大利语", "Italian"),
    "PT": ("葡萄牙语", "Portuguese"), "NL": ("荷兰语", "Dutch"),
    "GR": ("希腊语", "Greek"), "PL": ("波兰语", "Polish"),
    "RO": ("罗马尼亚语", "Romanian"), "UA": ("乌克兰语", "Ukrainian"),
    "IR": ("波斯语", "Persian"), "ET": ("阿姆哈拉语", "Amharic"),
}

# Per-country name overrides for high-weight countries whose region pool is a
# mix (e.g. southeast_asian spans VN/TH/ID/PH). Country override wins so a
# persona's name matches their country; the region pool is the fallback.
NAME_OVERRIDES: dict[str, dict[str, list[str]]] = {
    "IN": {"male": ["Arjun Sharma", "Rohan Patel", "Vikram Singh", "Karan Mehta", "Aditya Iyer", "Sanjay Gupta"],
           "female": ["Ananya Sharma", "Priya Patel", "Kavya Singh", "Diya Iyer", "Meera Gupta", "Sana Khan"]},
    "ID": {"male": ["Budi Santoso", "Agus Wijaya", "Rizky Pratama", "Dedi Kurniawan", "Andi Saputra", "Eko Prasetyo"],
           "female": ["Siti Rahayu", "Dewi Lestari", "Ratna Wulandari", "Nur Aini", "Ayu Handayani", "Maya Sari"]},
    "VN": {"male": ["Minh Nguyen", "Duc Tran", "Tuan Le", "Binh Vo", "Quang Nguyen", "Huy Pham"],
           "female": ["Linh Nguyen", "Mai Tran", "Thuy Le", "Lan Pham", "Hong Vo", "Hoa Nguyen"]},
    "TH": {"male": ["Somchai Prasert", "Kittipong Srisai", "Anan Wongchai", "Pongsak Chaiyasit", "Warat Thongdee", "Chaiya Bunnag"],
           "female": ["Somsri Prasert", "Naree Srisai", "Wannasri Wongchai", "Malee Chaiyasit", "Duangjai Thongdee", "Boonruang Bunnag"]},
    "PH": {"male": ["Juan Dela Cruz", "Miguel Santos", "Jose Ramirez", "Carlos Reyes", "Alfredo Gonzales", "Marco Villanueva"],
           "female": ["Maria Santos", "Ana Dela Cruz", "Lucia Ramirez", "Beatriz Reyes", "Carmen Gonzales", "Angela Villanueva"]},
    "PK": {"male": ["Ahmed Khan", "Muhammad Ali", "Usman Sheikh", "Bilal Ahmed", "Hamza Malik", "Imran Hussain"],
           "female": ["Fatima Khan", "Ayesha Ali", "Zainab Sheikh", "Maryam Ahmed", "Hina Malik", "Sana Hussain"]},
    "BD": {"male": ["Rakib Hasan", "Tanvir Ahmed", "Mahmud Islam", "Shiraz Chowdhury", "Naim Rahman", "Faisal Karim"],
           "female": ["Nusrat Jahan", "Sadia Akter", "Farhana Rahman", "Taslima Chowdhury", "Rokeya Karim", "Shorna Islam"]},
    "NG": {"male": ["Chinedu Okafor", "Emeka Obi", "Tunde Adeyemi", "Ibrahim Musa", "Femi Bakare", "Seyi Johnson"],
           "female": ["Chiamaka Okafor", "Adaeze Obi", "Amina Musa", "Funke Adeyemi", "Ngozi Eze", "Zainab Bello"]},
    "EG": {"male": ["Ahmed Hassan", "Mohamed Ali", "Omar Farouk", "Khalid Ibrahim", "Tarek Mostafa", "Mahmoud Adel"],
           "female": ["Fatima Hassan", "Amina Ali", "Layla Farouk", "Sara Ibrahim", "Nour Mostafa", "Salma Adel"]},
    "SA": {"male": ["Abdulaziz AlSaud", "Faisal AlQahtani", "Sultan AlOtaibi", "Khalid AlHarbi", "Bandar AlShammari", "Tariq AlDosari"],
           "female": ["Noura AlSaud", "Reem AlQahtani", "Sarah AlOtaibi", "Hessa AlHarbi", "Maha AlShammari", "Lama AlDosari"]},
    "IR": {"male": ["Ali Rezaei", "Mohammad Hosseini", "Amir Karimi", "Reza Ahmadi", "Saeed Mousavi", "Hassan Jafari"],
           "female": ["Fatemeh Rezaei", "Maryam Hosseini", "Zahra Karimi", "Negar Ahmadi", "Niloofar Mousavi", "Shirin Jafari"]},
    "TR": {"male": ["Mehmet Yilmaz", "Ahmet Kaya", "Mustafa Demir", "Hasan Celik", "Ali Sahin", "Emre Aydin"],
           "female": ["Fatma Yilmaz", "Ayse Kaya", "Zeynep Demir", "Elif Celik", "Merve Sahin", "Deniz Aydin"]},
    "RU": {"male": ["Ivan Petrov", "Dmitry Volkov", "Alexei Smirnov", "Nikolai Ivanov", "Sergei Fedorov", "Andrei Kozlov"],
           "female": ["Anna Petrova", "Maria Volkova", "Elena Smirnova", "Olga Ivanova", "Tatiana Fedorova", "Daria Kozlova"]},
    "BR": {"male": ["Joao Silva", "Pedro Santos", "Carlos Oliveira", "Lucas Souza", "Rafael Costa", "Thiago Almeida"],
           "female": ["Maria Silva", "Ana Santos", "Julia Oliveira", "Camila Souza", "Larissa Costa", "Beatriz Almeida"]},
    "MX": {"male": ["Carlos Garcia", "Jose Hernandez", "Miguel Rodriguez", "Juan Martinez", "Diego Lopez", "Andres Torres"],
           "female": ["Maria Garcia", "Ana Hernandez", "Sofia Rodriguez", "Valentina Martinez", "Camila Lopez", "Isabella Torres"]},
    "KE": {"male": ["John Otieno", "David Kipchoge", "Samuel Ochieng", "Peter Mwangi", "Joseph Kamau", "Brian Kiptoo"],
           "female": ["Grace Otieno", "Faith Kipchoge", "Mercy Ochieng", "Ruth Mwangi", "Joy Kamau", "Wanjiru Kiptoo"]},
}


def _weighted_pick(rng: random.Random, items: list, weights: list[float]):
    return rng.choices(items, weights=weights, k=1)[0]


def _weighted_pick_dict(rng: random.Random, mapping: dict[str, float]) -> str:
    keys = list(mapping.keys())
    return _weighted_pick(rng, keys, [max(mapping[k], 0.0) for k in keys])


def get_country(code: str) -> dict[str, Any] | None:
    return _COUNTRY_BY_CODE.get(code)


def list_continents() -> tuple[str, ...]:
    return _CONTINENTS


def sample_country(rng: random.Random, *, continent: str | None = None) -> dict[str, Any]:
    """Sample a country (optionally restricted to one continent), weighted by population."""
    pool = [c for c in COUNTRIES if continent is None or c["continent"] == continent]
    if not pool:
        pool = list(COUNTRIES)
    return _weighted_pick(rng, pool, [c["w"] for c in pool])


def _sample_language(rng: random.Random, country: dict[str, Any], region: dict[str, Any]) -> tuple[str, str]:
    """Return (language_cn, language_en). Country override wins over region default."""
    if country["code"] in LANG_OVERRIDES:
        return LANG_OVERRIDES[country["code"]]
    primary_cn, primary_en, extras = region["langs"]
    return primary_cn, primary_en


def sample_demographics(
    rng: random.Random,
    *,
    continent: str | None = None,
    country_code: str | None = None,
    gender: str = "男",
) -> dict[str, Any]:
    """Sample a coherent international demographics context for one persona.

    Parameters
    ----------
    rng          : RNG (determines reproducibility).
    continent    : optional continent restriction (亚洲/欧洲/...).
    country_code : optional forced country code (e.g. "BR").
    gender       : "男" / "女" — selects the matching name pool.

    Returns a dict with keys:
      continent, country_code, country_cn, country_en,
      region_key, region_cn, region_en,
      language_cn, language_en,
      religion, ethnicity, name,
      urbanicity (0..1), income (low/mid/high),
      urbanicity_label (城市/城镇/农村)
    """
    if country_code:
        country = _COUNTRY_BY_CODE.get(country_code)
        if country is None:
            raise ValueError(f"Unknown country_code: {country_code}")
    else:
        country = sample_country(rng, continent=continent)

    region = CULTURAL_REGIONS[country["region"]]
    override = NAME_OVERRIDES.get(country["code"])
    if override:
        name_pool = override["male"] if gender != "女" else override["female"]
    else:
        name_pool = region["male"] if gender != "女" else region["female"]
    name = rng.choice(name_pool)
    language_cn, language_en = _sample_language(rng, country, region)
    religion = _weighted_pick_dict(rng, region["religions"])

    urbanicity = country["urban"]
    if urbanicity >= 0.75:
        urbanicity_label = "城市"
    elif urbanicity >= 0.45:
        urbanicity_label = "城镇"
    else:
        urbanicity_label = "农村"

    return {
        "continent": country["continent"],
        "country_code": country["code"],
        "country_cn": country["cn"],
        "country_en": country["en"],
        "region_key": country["region"],
        "region_cn": region["label_cn"],
        "region_en": region["label_en"],
        "language_cn": language_cn,
        "language_en": language_en,
        "religion": religion,
        "ethnicity": region["ethnicity"],
        "name": name,
        "urbanicity": round(urbanicity, 3),
        "income": country["income"],
        "urbanicity_label": urbanicity_label,
    }


if __name__ == "__main__":
    import json
    _rng = random.Random(7)
    seen_countries: set[str] = set()
    for _ in range(2000):
        d = sample_demographics(_rng)
        seen_countries.add(d["country_code"])
    print("countries sampled / total:", len(seen_countries), "/", len(COUNTRIES))
    print("continents:", list_continents())
    print("sample (seed=7, first 3):")
    _rng2 = random.Random(7)
    for _ in range(3):
        print("  ", json.dumps(sample_demographics(_rng2), ensure_ascii=False))


