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

# 判断是否是自定义值
def is_custom_value(field, value):
    all_options = RELATIONSHIP_OPTIONS if field == 'relationship' else \
                 NICKNAME_OPTIONS if field == 'nickname' else \
                 PERSONALITY_OPTIONS
    
    all_values = all_options['free'] + all_options['premium']
    return value not in all_values 