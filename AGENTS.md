# NorviTech website

This public repository owns the source for norvitech.com, served by GitHub Pages from main:/docs.

Keep demonstration data fictional. Never commit credentials, personal data, private infrastructure addresses, logs or session journals. The privacy workflow scans history and new content.

Navigation is defined in scripts/nav.py: the product list, every menu, each page's header and footer, and the row of products on each product's page. Edit it there, never in a page. After adding a product or page, register it in the product menu, run python3 scripts/nav.py and update the canonical sitemap. Validate with python3 scripts/check.py and node --check docs/site.js. Every product page must be reachable from its own menu.

Use responsive, accessible HTML with reviewed product demonstrations. Document requirements, setup, configuration, security, backups, upgrades and recovery without exposing deployment-specific values.
