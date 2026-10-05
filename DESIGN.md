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
