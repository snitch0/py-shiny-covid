def create_pref_dict():
    en_list = [
        "ALL",
        "hokkaido", "aomori", "iwate", "miyagi", "akita", "yamagata", "fukushima",
        "ibaraki", "tochigi", "gunma", "saitama", "chiba", "tokyo", "kanagawa",
        "niigata", "toyama", "ishikawa", "fukui", "yamanashi", "nagano", "gifu",
        "shizuoka", "aichi", "mie", "shiga", "kyoto", "osaka", "hyogo", "nara",
        "wakayama", "tottori", "shimane", "okayama", "hiroshima", "yamaguchi",
        "tokushima", "kagawa", "ehime", "kochi", "fukuoka", "saga", "nagasaki",
        "kumamoto", "oita", "miyazaki", "kagoshima", "okinawa"
    ]
    en_c_list = [s.capitalize() if s.islower() else s for s in en_list]
    ja_list = [
        "全国",
        "北海道", "青森", "岩手", "宮城", "秋田", "山形", "福島", "茨城", "栃木", "群馬", 
        "埼玉", "千葉", "東京", "神奈川", "新潟", "富山", "石川", "福井", "山梨", "長野", 
        "岐阜", "静岡", "愛知", "三重", "滋賀", "京都", "大阪", "兵庫", "奈良", "和歌山", 
        "鳥取", "島根", "岡山", "広島", "山口", "徳島", "香川", "愛媛", "高知", "福岡",
        "佐賀", "長崎", "熊本", "大分", "宮崎", "鹿児島", "沖縄"
    ]
    pref_dict = {key:[val1, val2] for key, val1, val2 in zip(
        ja_list, en_c_list, range(len(ja_list)))}

    return pref_dict