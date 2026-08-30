# Spec: Registration

## Overview
This step implements user account creation for Spendly. The `/register` page and template already exist as a static form (`templates/register.html`, posting to `/register`), but `app.py` currently only renders it on GET with no POST handler. This feature wires that form up to the real `users` table from Step 1 — validating input, hashing the password, creating the account, and starting a logged-in session — so a visitor can actually sign up and land in the app instead of hitting a dead end.

## Depends on
- Step 1 — Database Setup (`database/db.py`: `get_db()`, `init_db()`, `seed_db()`, `users` table). Already complete on this branch.

## Routes
- `GET /register` — render the registration form — public (already exists, unchanged)
- `POST /register` — validate input, create the user, log them in, redirect — public

## Database changes
No database changes. The `users` table (id, name, email, password_hash, created_at) from Step 1 already covers registration's needs.

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — add `{{ old.name }}` / `{{ old.email }}` re-population on validation failure so the user doesn't retype everything after an error (the `{% if error %}` block already exists and stays as-is)

## Files to change
- `app.py` — add `POST` handling to the `/register` route: read form fields, validate, hash password, insert user, set session, redirect to `/profile` (the placeholder Step 4 route)

## Files to create
None.

## New dependencies
No new dependencies. Uses `werkzeug.security.generate_password_hash` (already used in `database/db.py`) and Flask's built-in `session`.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash`, verified later with `check_password_hash`)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate on the server even though the form has `required`/`type=email` attributes client-side: name non-empty, email looks valid and is not already registered, password is at least 8 characters (matches the placeholder text in `register.html`)
- On any validation failure, re-render `register.html` with the same `error` variable pattern already used in the template (do not redirect on error, so the message shows immediately)
- On success, store the new user's id in `session["user_id"]` and redirect (302) to `/profile`
- Do not log or echo the raw password anywhere

## Definition of done
- [ ] Visiting `/register` still shows the existing form unchanged
- [ ] Submitting valid name/email/password creates a row in `users` with a hashed (not plaintext) password
- [ ] After successful registration, the browser is redirected to `/profile` and a session cookie is set
- [ ] Submitting an email that already exists in `users` re-renders the form with an error and does not create a duplicate row
- [ ] Submitting a password under 8 characters re-renders the form with an error and does not create a row
- [ ] Submitting an empty name re-renders the form with an error and does not create a row
- [ ] Restarting the Flask app and re-submitting the same valid form again still correctly rejects the now-duplicate email
