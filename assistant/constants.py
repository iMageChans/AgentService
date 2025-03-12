# 关系选项
RELATIONSHIP_OPTIONS = {
    'free': ['Newbie', 'Companion', 'Buddy'],
    'premium': ['BF', 'GF', 'BFF', 'Muse', 'Mystery', 'Crush', 'Money Guru', 'Butler', 'Boss']
}

# 昵称选项
NICKNAME_OPTIONS = {
    'free': ['Friend', 'Mate', 'Dude'],
    'premium': ['Babe', 'Angel', 'Champ', 'Sweetie', 'Stranger', 'Master', 'Bestie', 'Cutie', 'Rookie']
}

# 性格选项
PERSONALITY_OPTIONS = {
    'free': ['Cheerful', 'Cute'],
    'premium': ['Friendly & Warm', 'Romantic & Flirty', 'Professional & Smart', 
                'Fun & Humorous', 'Calm & Caring', 'Unique & Fantasy']
}

# 付费关系选项
PREMIUM_RELATIONSHIP_OPTIONS = [
    "BF", "GF", "BFF", "Muse", "Mystery", "Crush", 
    "Money Guru", "Butler", "Boss", "Customization"
]

# 付费昵称选项
PREMIUM_NICKNAME_OPTIONS = [
    "Babe", "Angel", "Champ", "Sweetie", "Stranger", 
    "Master", "Bestie", "Cutie", "Rookie", "Customization"
]

# 付费性格选项
PREMIUM_PERSONALITY_OPTIONS = [
    "Friendly & Warm", "Romantic & Flirty", "Professional & Smart", 
    "Fun & Humorous", "Calm & Caring", "Unique & Fantasy", "Customization"
]

# 免费关系选项
FREE_RELATIONSHIP_OPTIONS = ["Newbie", "Companion", "Buddy"]

# 免费昵称选项
FREE_NICKNAME_OPTIONS = ["Friend", "Mate", "Dude"]

# 免费性格选项
FREE_PERSONALITY_OPTIONS = ["Cheerful", "Cute"]

# 判断是否是自定义值
def is_custom_value(field, value):
    all_options = RELATIONSHIP_OPTIONS if field == 'relationship' else \
                 NICKNAME_OPTIONS if field == 'nickname' else \
                 PERSONALITY_OPTIONS
    
    all_values = all_options['free'] + all_options['premium']
    return value not in all_values 