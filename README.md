# School Lost & Found

An unofficial, responsive prototype for Samarkand Presidential School, built with React, TypeScript, and Vite. The existing `ML_GUIDE.html` is preserved separately.

## Run locally

Use Node.js 20.19+ or 22.12+ and npm:

```sh
npm ci
npm run dev
```

Open the address printed by Vite. For a production build:

```sh
npm run build
npm run preview
```

## Prototype behavior

- Add lost/found listings; search titles and descriptions; filter by category/status; sort by date.
- View details, edit/delete listings, and mark items returned.
- Local storage persists listings and theme only in the current browser and origin. Nothing is shared between students. Clearing browser data removes listings.
- Six clearly marked examples appear only when no saved board exists. Clear samples removes only sample entries and does not seed them again.
- Optional JPG/PNG/WebP photos (15 MB input limit) are resized to a maximum 1,000 pixels and encoded as JPEG before saving. Failed storage writes preserve existing listings and keep the form open.
- Optional Telegram usernames create contact links. Avoid sensitive descriptions, exact home addresses, or phone numbers.
- Google Fonts are optional; local fallback fonts work offline.

## Validation

`npm run build` performs TypeScript checking and a production build. Browser flow checks are in `tests/smoke.py` and require Python Playwright and Chromium:

```sh
python tests/smoke.py
```

By default, checks use the running server on port 5173 and `/usr/bin/chromium`. Set `APP_URL` and `CHROMIUM_PATH` to override these. The runner uses a fresh browser profile and does not affect your normal browser's listings.

## Making it a shared school service

Add a hosted API and database for shared listings, protected image storage with upload limits, and school-approved identity/access controls. Add ownership permissions for editing/deletion, moderation and reporting, privacy/retention rules, backups, and abuse protection. Obtain school approval before describing it as an official service, deploy with HTTPS, and test accessibility and security. No backend or authentication is included in this prototype.
