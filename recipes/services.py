import json
import re

from django.conf import settings
from openai import OpenAI, OpenAIError

MODEL = 'gpt-4o-mini'

SYSTEM_PROMPT = (
    'あなたは家庭料理のレシピ提案アシスタントです。'
    '料理経験の少ない30〜40代の家庭のパパでも作れるよう、手順は平易な言葉で書いてください。'
    '生の食材から加熱不十分になるレシピは提案せず、一般的な家庭にある調理器具の範囲で作れるものにしてください。'
    '除外食材として指定された食材(アレルギー・苦手な食材)は、たとえ使える食材リストに含まれていても絶対に使用しないでください。'
    '必ず指定されたJSON形式のみで出力してください。'
)

RESPONSE_JSON_SCHEMA = {
    'name': 'recipe_suggestions',
    'strict': True,
    'schema': {
        'type': 'object',
        'properties': {
            'recipes': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'title': {'type': 'string'},
                        'for_kids': {'type': 'boolean'},
                        'quick': {'type': 'boolean'},
                        'materials': {'type': 'array', 'items': {'type': 'string'}},
                        'steps': {'type': 'array', 'items': {'type': 'string'}},
                    },
                    'required': ['title', 'for_kids', 'quick', 'materials', 'steps'],
                    'additionalProperties': False,
                },
            },
        },
        'required': ['recipes'],
        'additionalProperties': False,
    },
}

_SPLIT_PATTERN = re.compile(r'[、,\n]')


class RecipeGenerationError(Exception):
    pass


def extract_excluded_ingredients(children):
    names = []
    for child in children:
        for field_value in (child.allergies, child.dislikes):
            names += [name.strip() for name in _SPLIT_PATTERN.split(field_value) if name.strip()]

    deduped = []
    seen = set()
    for name in names:
        if name not in seen:
            seen.add(name)
            deduped.append(name)
    return deduped


def _build_user_prompt(ingredient_names, for_kids, quick, excluded_ingredients, count):
    ingredients_list = '\n'.join(f'- {name}' for name in ingredient_names)
    excluded_list = '\n'.join(f'- {name}' for name in excluded_ingredients) if excluded_ingredients else 'なし'

    return (
        f'以下の食材を使って、家庭で作れるレシピを{count}件提案してください。\n\n'
        f'【使える食材】\n{ingredients_list}\n\n'
        '【条件】\n'
        f'- 子供向け: {"はい" if for_kids else "指定なし"}\n'
        f'- 時短: {"はい" if quick else "指定なし"}\n\n'
        f'【除外食材(アレルギー・苦手な食材)】\n{excluded_list}\n\n'
        '条件に「子供向け」が指定された場合は、辛味や苦味を抑えるなど子供が食べやすい味付け・調理法にしてください。\n'
        '条件に「時短」が指定された場合は、調理時間が短く済む工程を優先してください。\n'
        '除外食材に挙がっている食材は、材料としても、他の材料に含まれる形でも使用しないでください。\n'
        '食材リストにない材料を使う場合は、家庭に常備されていることが多い調味料'
        '(醤油・塩・砂糖・油など、除外食材を除く)に限定してください。\n'
        '各レシピについて、実際に使った食材リスト(materials)と、手順を1文ずつに分けたリスト(steps)を出力してください。\n'
        '\n'
        '【for_kids / quick フィールドの設定ルール】\n'
        '- for_kids は、上記の条件で「子供向け: はい」の場合のみ true にしてください。'
        '「子供向け: 指定なし」の場合は、そのレシピが子供でも食べられる内容であっても必ず false にしてください。\n'
        '- quick は、上記の条件で「時短: はい」の場合のみ true にしてください。'
        '「時短: 指定なし」の場合は、そのレシピが短時間で作れる内容であっても必ず false にしてください。\n'
        '- これらのフィールドは「あなたがレシピをどう評価したか」ではなく「ユーザーがその条件を指定したか」を表します。'
    )


def _validate_recipes(data, expected_count):
    if not isinstance(data, dict) or 'recipes' not in data:
        raise RecipeGenerationError('レスポンスに recipes キーがありません。')

    recipes = data['recipes']
    if not isinstance(recipes, list) or len(recipes) != expected_count:
        raise RecipeGenerationError(f'レシピ件数が{expected_count}件ではありません。')

    for recipe in recipes:
        if not isinstance(recipe.get('title'), str) or not recipe['title'].strip():
            raise RecipeGenerationError('title が不正です。')
        if not isinstance(recipe.get('for_kids'), bool) or not isinstance(recipe.get('quick'), bool):
            raise RecipeGenerationError('for_kids / quick が不正です。')
        materials = recipe.get('materials')
        steps = recipe.get('steps')
        if not isinstance(materials, list) or not materials or not all(isinstance(m, str) and m.strip() for m in materials):
            raise RecipeGenerationError('materials が不正です。')
        if not isinstance(steps, list) or not steps or not all(isinstance(s, str) and s.strip() for s in steps):
            raise RecipeGenerationError('steps が不正です。')

    return recipes


def generate_recipes(*, ingredient_names, for_kids, quick, excluded_ingredients, count=3):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    user_prompt = _build_user_prompt(ingredient_names, for_kids, quick, excluded_ingredients, count)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': user_prompt},
            ],
            response_format={'type': 'json_schema', 'json_schema': RESPONSE_JSON_SCHEMA},
        )
    except OpenAIError as exc:
        raise RecipeGenerationError('OpenAI APIの呼び出しに失敗しました。') from exc

    content = response.choices[0].message.content
    try:
        data = json.loads(content)
    except (json.JSONDecodeError, TypeError) as exc:
        raise RecipeGenerationError('OpenAI APIのレスポンスがJSONとして解析できません。') from exc

    return _validate_recipes(data, count)
