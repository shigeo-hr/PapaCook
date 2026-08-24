# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

PapaCook (パパクック) is a Django web app that lets users enter ingredients they have at home and get AI-generated recipe suggestions (via OpenAI GPT-4o-mini) suitable for both kids and adults. It also lets users register a child profile (likes/dislikes, allergies) to tailor suggestions, and — planned for a later release — record post-meal feedback ("eaten"/"left") to improve future suggestions. Full product background, target users, and the feature roadmap are documented in `README.md` (in Japanese) — read it for product/UX context before implementing user-facing features.

The repository is currently just the initial Django project skeleton (`config/`) committed via `django-admin startproject`; no Django apps, models, views, or templates exist yet.

## Tech stack

- Django 6.1, Python 3.12
- PostgreSQL (via `psycopg2-binary`), configured through `python-decouple` reading from `.env`
- Planned: OpenAI API (GPT-4o-mini) for recipe generation, Chart.js for data visualization
- Deploy target: Render
- No frontend framework planned — server-rendered Django templates only (see README §10-3 for the conditions under which this would be revisited)

## Setup and commands

```bash
source venv/bin/activate       # activate the existing virtualenv
python manage.py runserver     # run the dev server
python manage.py migrate       # apply migrations
python manage.py makemigrations <app>
python manage.py createsuperuser
python manage.py test          # run tests (once apps/tests exist)
python manage.py startapp <name>
```

```bash
pip install -r requirements.txt   # install dependencies
pip freeze > requirements.txt     # regenerate after adding a new dependency
```

## Configuration

- `config/settings.py` reads DB credentials (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) from `.env` via `python-decouple`'s `config()`. `.env` is gitignored — never commit it.
- `SECRET_KEY` and `DEBUG` are currently hardcoded in `config/settings.py` rather than read from `.env`, even though both also appear in `.env`. Be aware of this mismatch if working on settings/config.
- `MAILERS` in `config/settings.py` is set up as if for a mail backend dict but Django's actual mail setting is `EMAIL_BACKEND`/`EMAIL_*` — this looks like a leftover/misconfiguration, not an intentional custom setup.

## デザイン方針(現時点)

- 現在CSSフレームワークは未導入。全機能の実装を優先し、装飾は後回しにする方針。
- 各ページのHTML/テンプレートは、装飾なしのシンプルな構造(bare HTML)のまま実装すること。
- インラインスタイルや個別ページごとの独自CSSは書かないこと。全機能実装後にBootstrap等のCSSフレームワークを一括導入し、まとめてデザインを整える予定のため。
- クラス名は将来Bootstrapのクラス(例: btn, form-control, container など)を当てはめやすいよう、意味のある命名(例: ingredient-form, recipe-card)にしておくこと。

## Architecture notes

- Single Django project (`config`) with the standard settings/urls/wsgi/asgi layout; no apps have been created yet. When adding features, they should live in their own Django apps (e.g. `recipes`, `ingredients`, `children`, `accounts`) rather than in `config`.
- Per the README, **all pages require login except signup/login** (the app handles family members' personal data), so auth needs to be built in from the start of any view/URL work.
- The planned data model (see README §"ER図" for the diagram) centers on: users, child profiles (with likes/dislikes/allergies), ingredients, AI-suggested recipes, and post-cooking feedback (eaten/left) — feedback data is meant to feed back into future AI suggestions, which is the app's core differentiator.
