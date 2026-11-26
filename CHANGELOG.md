# Changelog

All notable technical changes to Iris will be documented in this file.
Note: Formal version logging began after the v1.0.0 release; earlier iterative updates between initial deployment (Oct 10, 2026) and v1.0.0 are summarized together below.

## 2026-11-26 - v1.1.1
### Added
- Added current version status on news page. 
- Added `<hr>` lines between articles on news page. 

### Fixed
- Adjusted text sizing of `send message` button in the contact form and set `width` to `100%`. 

### Changed
- Changed title of contact page from `Contact Us & Support | Iris` to `Contact Us & Frequently Asked Questions | Iris`.
- Rephrased answer to "Are my uploaded PDFs secure?" to include the link to `CHANGELOG.md`. 

## 2026-11-24 - v1.1.0 
### Added
- Created `CHANGELOG.md` to track technical updates across versions.
- Created `/news` route for the user-facing updates feed. 
- Added "Source Code" link to the footer pointing to the public GitHub repository.
- Added "News" link to the footer pointing to the user-facing updates feed (`/news`). 

### Fixed
- Switched footer navigation to CSS Grid (3x2 desktop, 2x3 mobile) with `justify-content: space-evenly` on mobile.
- Added a try statement to the `extract_acroform_fields` function in case Gemini doesn't work to generate field names.
- Cleaned up media queries for smaller screens. 

### Changed
- Changed header tagline size to better accommodate different sized screens. 
- Changed links to stand out clearly against plain text. 

---

## 2026-10-10 - v1.0.0 
### Added
- Initial public release of Iris (`irisforms.org`) for the Congressional App Challenge.
- User authentication system (sign up, log in, password reset) with 13+ age verification.
- PDF upload and AI-powered field extraction using `PyMuPDF` and the Google Gemini API.
- One-question-at-a-time accessible form interface with built-in text-to-speech (`Listen`) and voice-to-text support.
- Read-only answer review screen and completed PDF generation/download.
- Encrypted database storage for user profiles and uploaded files.
- High-contrast, low-glare UI using `Atkinson Hyperlegible` and responsive `clamp()` typography.
- Terms of Service, Privacy Policy, Our Story, and Contact & FAQs pages.