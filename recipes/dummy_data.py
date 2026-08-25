"""issue #26(AIレシピ提案ロジック)実装までの仮データ。

issue #14はUI作成のみがスコープのため、OpenAI APIとの連携は行わず、
画面の見た目を確認できる静的なレシピデータをここに置いている。
issue #26で実際のAI生成ロジックに置き換わる想定。
"""

DUMMY_RECIPES = [
    {
        'id': 1,
        'name': '豚肉と野菜の甘辛炒め',
        'summary': '豚肉と余りがちな野菜を使った、子供も食べやすい甘辛味の炒め物です。',
        'for_kids': True,
        'quick': True,
        'materials': ['豚肉', '玉ねぎ', 'にんじん', 'ピーマン', '醤油', '砂糖'],
        'steps': [
            '野菜を一口大に切る。',
            '豚肉を炒め、色が変わったら野菜を加える。',
            '醤油と砂糖で味付けし、全体に火が通ったら完成。',
        ],
    },
    {
        'id': 2,
        'name': '鶏肉と根菜の煮物',
        'summary': 'じっくり煮込んだ、優しい味わいの和風煮物です。',
        'for_kids': True,
        'quick': False,
        'materials': ['鶏肉', 'じゃがいも', 'にんじん', '醤油', 'みりん', 'だし'],
        'steps': [
            '鶏肉と野菜を一口大に切る。',
            '鍋で鶏肉を軽く炒め、野菜を加える。',
            'だし・醤油・みりんを加えて煮込み、味がしみたら完成。',
        ],
    },
    {
        'id': 3,
        'name': 'トマトと卵の中華風炒め',
        'summary': '短時間で作れる、トマトの酸味と卵のまろやかさが人気の一品です。',
        'for_kids': False,
        'quick': True,
        'materials': ['トマト', 'たまご', 'ねぎ', '塩', 'ごま油'],
        'steps': [
            'トマトをくし切り、卵を溶いておく。',
            'フライパンで卵を半熟に炒め、一度取り出す。',
            'トマトを炒め、卵を戻し入れて塩とごま油で味を整える。',
        ],
    },
]


def get_dummy_recipes(for_kids=False, quick=False):
    recipes = DUMMY_RECIPES
    if for_kids:
        recipes = [r for r in recipes if r['for_kids']]
    if quick:
        recipes = [r for r in recipes if r['quick']]
    return recipes


def get_dummy_recipe(recipe_id):
    for recipe in DUMMY_RECIPES:
        if recipe['id'] == recipe_id:
            return recipe
    return None
