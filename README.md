# KWS Hygiene & Fragrance website

东莞市凯卫莎实业有限公司原网站内容迁移与官网重建。English source: https://www.scentairmachines.com/.

## Local preview

```sh
python3 scripts/build.py
python3 scripts/serve.py --port 4173
```

Open http://127.0.0.1:4173/. The preview serves only `website/`, not original archives or migration reports.

## Content and build

- `research/`: original public HTML and original media archives. Never execute source scripts or serve this folder as the public site.
- `content/products.json`: stable source-page IDs, real product fields, category, local image references and sanitized descriptions.
- `content/resources.json`: product demonstrations and news.
- `content/certificates.json`: document records, deduplicated by standard, number and date; all supplied scans retained.
- `content/migration-audit.json`, `gallery-audit.json`: retrieval failures and mechanically verified normalizations.
- `content/url-map.csv`: original English page paths and replacement paths.
- `website/`: generated static website, local media, CSS and vanilla JavaScript.
- `evidence/`: verification reports and desktop/mobile screenshots.
- `planning/`: initial content inventory and wireframe plan.

Already installed Python dependencies are recorded in `requirements.txt`. No JavaScript application framework, database or CMS is required to preview or build. JSON content files are not a working management backend. A CMS can be added when editing roles, publishing workflows and hosting requirements are specified.

To refresh the original-source archive deliberately:

```sh
python3 scripts/import_content.py
python3 scripts/migrate_videos.py
python3 scripts/refine_content.py
python3 scripts/build.py
python3 scripts/check_site.py
```

The import uses cached source files and media. Refresh specific records by removing their cached files only after retaining a backup. Archived source material is preserved separately from cleaned public content. Never replace confirmed owner edits with a bulk source refresh without reviewing the diff.

## Inquiry behavior

The form validates required fields and generates a draft in the browser. The user reviews it and opens their email app or WhatsApp. No message is submitted automatically, no success message implies delivery, and no mail credentials or website inquiry database are configured. Tests do not send messages to the company. To enable server-side delivery later, configure an authorized mail service and verify real receiving, validation, errors, rate limits and privacy text.

## Production configuration

The default build is a local preview with `noindex,nofollow` and `robots.txt` blocking indexing. No production domain, DNS or account was changed. When the actual public URL and hosting are authorized:

```sh
SITE_URL=https://YOUR-AUTHORIZED-DOMAIN python3 scripts/build.py
```

This sets canonical links and a production sitemap. Configure the generated `_redirects` / `_headers` using the actual hosting provider. HTML redirect documents are also emitted for the archived English URLs. A live deployment, redirect responses and form receiving still require deployment verification. Multilingual subdomains and the legacy VR service have not been recreated.

## Content decisions

Contradictory workforce/revenue figures are kept in the original archive and excluded from public promotional text. The company narrative uses the Dongguan entity consistently, while the historical Shenzhen entity remains in the sourced timeline. Product entries are not merged just because model numbers look similar. Certificate applicability and current status must be confirmed per order. Ordering conditions remain attached to their source product.

## Video dependency

Source HLS media is archived into `website/assets/video/` rather than depending on the old site's playback service. Chrome playback uses the local `hls.js` light build v1.7.3; Safari can use native HLS. The upstream BSD-2-Clause license is retained in `website/assets/vendor/hls-LICENSE.txt`.

Upstream: https://github.com/video-dev/hls.js/releases/tag/v1.7.3
npm archive SHA256: `a7290f1645f7c605baec75638acda6c6f7b08dde8a615c841a19d0e38df88729`.

## GitHub customer preview

The publishing workflow `.github/workflows/pages.yml` uploads only the generated `_site/` folder to GitHub Pages. It runs `scripts/prepare_pages.py` against GitHub's reported site URL and verifies every local image, link, gallery and video URL after adding the project path. The original `website/` remains suitable for a root-domain host.

```sh
python3 scripts/check_site.py
python3 scripts/prepare_pages.py --url https://chenpeiteng0423-spec.github.io/kws-hygiene-website/
```

Customer previews keep `noindex,nofollow` and do not change the original domain. On GitHub, enable Settings → Pages → Source → GitHub Actions, then push `main` or run “Publish customer preview”. The workflow publishes the checked static snapshot; content changes must first be rebuilt locally with `scripts/build.py`. Legacy extensionless redirects are served as HTML directory pages on Pages; GitHub Pages does not apply `_headers` or HTTP 301 `_redirects` rules.

The repository excludes duplicate original image/video archives in `research/media/` and `research/video/`; all public website images and video segments remain in `website/assets/`. Original HTML and structured content are retained for future edits. Repository upload and a live customer URL are not considered completed until the remote repository and deployment have been verified.

## Customer preview hosting

- GitHub repository: https://github.com/chenpeiteng0423-spec/kws-hygiene-website
- Primary customer URL: https://kws-hygiene-preview.pages.dev/
- Cloudflare project: `kws-hygiene-preview`, production branch `main`, direct static upload.
- GitHub Pages remains a separately configured automatic preview. Cloudflare does not automatically follow GitHub pushes; use the command below after rebuilding and committing website changes.

```sh
# Use the computer's existing network proxy if the network requires it.
HTTPS_PROXY=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897 ./scripts/publish_preview.sh
```

This command verifies the site, prepares root-hosted URLs and uploads only `_cloudflare_site/` to this project's existing Cloudflare Pages deployment. It retains security headers and the original URL's HTTP 301 mappings. Authentication stays in the local Wrangler credential store; no hosting credentials are included in the repository. The original scentairmachines.com domain is unchanged.
