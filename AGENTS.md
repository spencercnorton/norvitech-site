# NorviTech website

This public repository owns the source for norvitech.com, served by GitHub Pages from main:/docs.

Keep demonstration data fictional. Never commit credentials, personal data, private infrastructure addresses, logs or session journals. The privacy workflow scans history and new content.

Navigation is defined in scripts/nav.py: the product list, every menu, each page's header and footer, and the row of products on each product's page. Edit it there, never in a page. After adding a product or page, register it in the product menu and run python3 scripts/nav.py, which also rewrites the sitemap. Validate with python3 scripts/check.py and node --check docs/site.js. Every product page must be reachable from its own menu.

Indigo's pages under docs/indigo/ are generated from each stable Indigo release by scripts/build_indigo.py (its docstring has the command); never edit them by hand. A release that adds a guide page fails check.py until the page is added to Indigo's menus in scripts/nav.py.

Use responsive, accessible HTML with reviewed product demonstrations. Document requirements, setup, configuration, security, backups, upgrades and recovery without exposing deployment-specific values.
