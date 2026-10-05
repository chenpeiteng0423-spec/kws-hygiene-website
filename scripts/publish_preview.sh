#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
git diff --quiet
git diff --cached --quiet
python3 scripts/check_site.py
python3 scripts/prepare_pages.py --url https://kws-hygiene-preview.pages.dev --output _cloudflare_site
cp website/_headers website/_redirects _cloudflare_site/
npx --yes wrangler@4.147.0 pages deploy _cloudflare_site --project-name kws-hygiene-preview --branch main --commit-hash "$(git rev-parse HEAD)"
