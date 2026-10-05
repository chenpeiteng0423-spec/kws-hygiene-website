# KWS website design and content contract

2026-10-05. Owner: 东莞市凯卫莎实业有限公司. Public source: https://www.scentairmachines.com/.

Visual thesis: a calm, contemporary manufacturer website in deep forest green, warm ivory and honest product photography, combining fragrance atmosphere with readable procurement information.
Content plan: image-led brand introduction → fragrance / hygiene collections → selected products → manufacturing and quality → product demonstrations → direct inquiry.
Interaction thesis: restrained hero entrance, a sticky editorial navigation, and subtle image/arrow hover motion. Reduced motion disables animated movement. No extra animation dependencies.

## Architecture

There is no previous framework or package manifest. Generate static HTML with Python, BeautifulSoup and Pillow already available in the environment. Plain JavaScript handles client-side catalog search, sorting, pagination, mobile navigation, image galleries and inquiry drafts. All products have independent HTML URLs; content remains readable without JavaScript.

Content lives in content/ with original page IDs. Preserve research/ as an archival source. Actual product specifications are never filled by inference. All retained pictures and videos are downloaded locally. Source HTML is sanitized before rendering; no source scripts, forms, tracking or inline handlers are carried across.

## Pages

Home; product catalog and 14 category routes; individual product routes; applications; company; manufacturing; quality/certificates; resources/videos; news; contact; privacy; 404. Old English product and public page URLs receive local redirect documents and a URL mapping CSV. English is the source-grounded public site language; no nonfunctional language switcher.

## Content corrections

Archive conflicting workforce/revenue claims and mixed company names. Rewrite general company narrative using the consistent Dongguan entity, while retaining historical Shenzhen references only in the sourced history timeline. Don't display unconfirmed metrics. Deduplicate certificates by standard+number+date. Do not claim certificates cover all products or remain valid today. Normalize only mechanically provable duplicate parameter values; audit changes. Never merge different page records solely based on model similarity.

## Contact boundary

No email service credentials or authorized form delivery backend exist in this checkout. Offer existing WhatsApp and email links. Form creates a reviewable mail draft and a WhatsApp draft; it never reports that a message was sent. No external messages are sent in testing. CMS evaluated according to site-cms-stack; a database/admin deployment is not required for current website scope and has not been installed. JSON content is not represented as a working CMS.

## Acceptance

Check content records and source/asset URLs, safe markup, local links, images, model fields, certificate duplicate removal and build reproducibility. Browser: 1440 desktop and 390/320 mobile, search/filter/pagination, direct product URL, keyboard menu and gallery, inquiry draft validation, media and no page-level overflow. Show a local browser preview. No DNS or production domain changes are authorized by this build request.

## 2026-10-06 interface revision

Preserve the vanilla static stack and forest / ivory visual identity. Homepage uses three real catalog collections with six-second rotation, previous/next, dots and pause controls; hover, focus, background tabs and reduced motion suspend rotation. Three homepage HLS previews load on entering the viewport, play muted and inline, and pause on leaving; full resource pages retain manual playback.

About service content uses alternating text and generated concept illustrations. Actual team photographs remain unchanged, converted losslessly from archived originals; three-column desktop presentation avoids excessive enlargement and provides original-detail zoom. The original photographs are approximately 680 pixels wide and do not become high-resolution originals through this change.

Manufacturing adds six production discussion stages, original factory photography, OEM / ODM briefing and model-specific quality documentation guidance. News uses nine responsive cards: the original company archive story plus eight clearly labeled editorial guides. New articles make no invented claims about company events, certification, customers or measured results.

Generated visual provenance and accepted prompts are recorded in content/visual-assets.json and content/image-prompts.json. Only three concept illustrations are accepted; experimental portrait/document restoration is excluded because it changed fine details. Image generation used the built-in image tool.

## Premium spatial direction — 2026-10-06

Visual thesis: a quiet hospitality showroom, with warm architectural photography, ivory editorial typography and deep forest chapters. Preserve KWS branding and all real product/catalog content. Primary audience: overseas buyers comparing fragrance and hygiene equipment; primary action: explore products and prepare an inquiry.

Content plan: cinematic three-slide collection hero; two product-family compositions; an interactive spatial showroom; real selected products; manufacturing story; demonstrations; inquiry. Applications repeats the complete spatial showroom before the existing category guidance. Other pages share refined section titles, spacing, image treatment and conversion sections, without changing product data.

Interaction thesis: restrained hero image transitions; photographic scene switches with selectable equipment points; a pausable illustrative operation pulse. Three scene modes use clearly labeled concept imagery. The demonstration visualizes a discussion, not physical diffusion, coverage, concentration, efficacy or engineering sizing. Scheduling preference changes the briefing advice and is carried to the contact form, which continues to generate drafts only.

Acceptance: real product links per point, scene selection and keyboard operation, pause/reduced motion, selected scene/schedule reflected in contact drafts, no failed visible images, no horizontal overflow at 1440/768/390/320, and previously delivered carousel/video features preserved. Implement with existing Python generator and plain CSS/JS; no CMS or React migration.
