# Nimoli Bhandari Events (Python / Django)

This Django application provides an installable, responsive Progressive Web App (PWA) for Windows desktop and mobile browsers, with multiple event workspaces, event-scoped guests, expense tracking, crew management, Excel/CSV guest import and export, per-guest private RSVP links, RSVP data storage, custom guest details, bride/groom guest lists, and queued WhatsApp Business campaigns. It starts with an empty guest list and does not collect identity-document details.

## Windows desktop app

To build a portable Windows desktop app on Windows, run this from PowerShell:

```powershell
.\build_windows.ps1
```

The build creates `windows-dist\Nimoli-Bhandari-Events-Windows.zip`. Extract it and open `Nimoli Bhandari Events.exe`; a small launcher window lets you open the dashboard or exit cleanly. Windows may show a console window while the app is running. Guest data remains locally at `%LOCALAPPDATA%\Gather RSVP\gather.sqlite3` to preserve data created by previous Gather RSVP versions. Keep the Windows account and local data folder private, and arrange backups for real event data.

## macOS app

Build the Mac app on a Mac (PyInstaller cannot create macOS executables from Windows):

```bash
chmod +x build_macos.sh
./build_macos.sh
```

Install Python 3 with Tk support first (the python.org macOS installer includes Tk). The script creates a Mac-specific virtual environment, installs the build requirements, packages `dist/Nimoli Bhandari Events.app`, and creates `dist/Nimoli-Bhandari-Events-macOS.zip`. Open the `.app` from Finder. Guest data remains in `~/Library/Application Support/Gather RSVP/gather.sqlite3` so existing records are preserved. The first version is unsigned; Gatekeeper may require Control-click → Open on your own Mac. Distributing the app to other users requires Apple Developer ID signing/notarization. Build separately on Apple silicon and Intel Macs if both CPU architectures are needed.

The dashboard offers **Download Excel template**, **Import Excel/CSV**, and **Export Excel**. The generated `.xlsx` template includes an Instructions sheet and one `Guest List` sheet; users do not have to create separate Bride Side and Groom Side sheets. The guest table, template, and export use the EventIQ columns, in order: `Group ID`, `First Name`, `Last Name`, `Country Code`, `Phone Number`, `Invited Dates`, `Category`, `Pax`, `Guest Type`, `Tag`, `Sub Category`, `Invite Name`, and `Salutation`. All columns and values are optional: rows with any data are imported, and missing Group IDs are assigned automatically. Pick Bride Side or Groom Side from the Tag dropdown when known, or choose a default side in the import dialog; otherwise guests remain unassigned. Import accepts columns in any order, skips informational `Read Me` sheets, and accepts older side-specific sheet names. The guest-type and Tag dropdowns provide valid values, and Country Code has a country calling-code dropdown. Reuse a Group ID for members of the same family or travel group, with one person per row. Country code and phone are separate (for example, `+91` and `9876543210`). A phone number is optional; sending messages still requires valid international contact details and the guest’s consent. Extra event-specific columns may follow the listed headings. Guest sheets have frozen headers and Excel filter controls; imports and exports are ordered by side, group ID, and guest name. Legacy `.xls` is not supported. Import is all-or-nothing, limited to 2,000 people and a 2 MB file; imported contacts default to no WhatsApp consent.

The guest list has Bride Side and Groom Side tabs and groups rows by side and group number; Excel export contains separate sheets for both sides, plus an Unassigned sheet when older untagged records remain. Guests submit attendance, party size, hotel dates, room preference, and extra RSVP details; those answers are saved in the event database and appear in `.xlsx` and CSV exports. The dashboard's right-hand **Event media** panel accepts JPG, PNG, and WebP photos up to 20 MB, plus MP4 and WebM videos up to 100 MB, with at most 40 items and 500 MB per event. Media is served only to authenticated organizers for the currently selected event; it is not shown on guest RSVP pages. Desktop media is stored locally under `%LOCALAPPDATA%\Gather RSVP\media`. On a hosted deployment, configure `GATHER_MEDIA_ROOT` to persistent private storage and include it in backups. This is not live editing of an Excel Online/OneDrive workbook. Guests have private RSVP links. Local desktop links work only on that computer; a public HTTPS URL must be configured before exporting usable guest links. Do not post a private RSVP link publicly.

## Run on Windows

From this folder, open PowerShell and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The desktop app starts with a blank guest list. The dashboard offers a one-time **Create organizer account** page on the local computer; create your account before entering real event data. Once created, sign-up closes. Create an event first, then download and fill the Excel template or import an `.xlsx`/CSV guest list. Use **Add extra detail** to add up to 10 custom text fields shared across event workspaces; removing a column deletes its saved values. Guest RSVP forms include these fields.

The development server opens without sign-in only for requests from this computer while `DEBUG` is enabled. A visible “Local demo” badge indicates this mode. Requests from other machines still require organizer authentication. For a hosted deployment, public self-signup is disabled; create organizer accounts with `python manage.py create_organizer` on the server. Guest records are saved locally in SQLite during development and remain on the same computer.

Create an event from **Add event** in the left navigation, then select its workspace to manage guests. Each event has its own guest list, expense records, and crew members; the same phone number may be invited to separate events. The Expenses page currently records amounts in INR. Custom guest-column definitions are shared across workspaces, while entered guest values remain with their guest records.

If you used an older app demo build, start the updated app once. It removes only the exact seven fictional records bundled by the old `seed_demo` command; any other guest rows are preserved. The app no longer adds sample guests at startup.

## Install on desktop or phone

Open the site over HTTPS when deployed (or `http://127.0.0.1:8000/` locally), then use the **Install app** button for device-specific instructions. Chromium browsers may offer a direct install prompt. On iPhone/iPad, use Safari’s Share menu and choose **Add to Home Screen**. Service workers and home-screen installation require a secure context; localhost is treated as secure for development. The offline page is cached, but guest data and dashboard pages are deliberately never cached.

The local `127.0.0.1` address is reachable only on the computer running Django, not on a phone. To install on phones or use the app across devices, deploy it to a domain with HTTPS, set a strong `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=false` and the allowed host/CSRF origin values, then create an organizer account. Do not expose Django’s development server to the public internet.

## Deploy on Render

The included `render.yaml` is a Render Blueprint for a hosted version of the app. It configures a private PostgreSQL database, production static files, HTTPS-aware Django settings, and a persistent disk for organizer-only event media. The selected Render web and database plans and the 5 GB media disk are paid resources; check Render's current prices before deploying. Keep one web instance while using the attached media disk.

1. Put this project in a private GitHub repository and push the files.
2. Sign in to Render, choose **New → Blueprint**, and connect that repository. Review the resources and charges before approving creation.
3. Wait for the first deploy to finish. Render supplies the site's HTTPS address; Django uses Render's hostname automatically for allowed hosts, CSRF protection, and RSVP links.
4. In the Render service's **Shell**, run `python manage.py create_organizer` and follow the prompts. Then sign in, create an event, and import the guest list. Do not use public self-signup for the hosted organizer account.
5. Set up backups and confirm that both the PostgreSQL database and the `/var/data` media disk are included. Do not store Aadhaar/passport numbers or identity-document images in this app.

Blueprint deployment does not connect WhatsApp. Add Meta's `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN`, and `WHATSAPP_API_VERSION` as private Render environment variables only after the hosted site is working and the official Cloud API is configured. Queued campaigns are not sent automatically; review and run the documented campaign command manually in the Render Shell.

## WhatsApp Business campaigns

On a public HTTPS deployment, the **WhatsApp Business** dialog queues a private one-to-one template message for each eligible opted-in guest; it does not create a group. The local desktop executable is not connected to an account just because WhatsApp Business is installed. Set up the official WhatsApp Business Platform/Cloud API for the sender's number and check Meta's current onboarding options if the number is already active in the WhatsApp Business app. Configure Meta Cloud API secrets `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_API_VERSION` (for example `vXX.X`), and `GATHER_PUBLIC_BASE_URL` in the deployment environment. Never put the access token in source control or in a shared desktop package. Create an approved template whose body parameters are, in order, guest name (`{{1}}`) and private RSVP link (`{{2}}`), then enter its exact name and language in Nimoli Bhandari Events. Imported guests default to no consent. Collect and document opt-in first, then use the guest row's **WhatsApp consent** control and save; the app records the time of the consent change. Queueing does not send automatically. On the hosted server, first run `python manage.py send_whatsapp_campaigns --dry-run`, review the campaign IDs and eligible/skipped counts, then send only the intended queue with `python manage.py send_whatsapp_campaigns --campaign-id ID --confirm`. Without `--confirm`, the command will not send. Messages are sent individually only to opted-in, non-opted-out guests with valid international phone numbers and are subject to Meta's policies, limits, approvals, and charges. A local desktop install has no public guest URL and cannot run a useful public campaign; share a hosted HTTPS website with the organizer instead. RSVP responses save in the app database and downloads; live Excel Online/OneDrive synchronization would require a separate Microsoft Graph integration.

## Before an internet deployment

- Set `DJANGO_DEBUG=false`, `DJANGO_SECRET_KEY` to a randomly generated secret, `DJANGO_ALLOWED_HOSTS` to your domain(s), `DJANGO_CSRF_TRUSTED_ORIGINS` to your HTTPS origin(s), and `GATHER_PUBLIC_BASE_URL` to the public HTTPS base URL. Production startup refuses to run without these values.
- Set `DATABASE_URL` to the hosting provider's PostgreSQL connection URL for shared use; PostgreSQL URLs default to required SSL. Keep this secret in the hosting provider's environment-variable store. SQLite remains the desktop/local default. Configure HTTPS, persistent private media storage through `GATHER_MEDIA_ROOT`, managed database/media backups, access monitoring, and retention/deletion procedures. Run `python manage.py migrate` and `python manage.py check --deploy` with production environment settings before opening the site.
- For Meta Cloud API campaigns, set `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_API_VERSION`, and optionally `WHATSAPP_SEND_INTERVAL` (seconds between recipients; default 0.25, maximum 60). Use approved templates, documented opt-in, and an opt-out/suppression workflow. Check current Meta messaging rules, limits, and charges.
- The app stores only name, phone number, RSVP status, hotel status, and consent metadata. Do not enter Aadhaar or passport numbers or upload identity document images. Confirm hotel and legal requirements for each applicable country before collecting any ID data.
- The application supports multiple event workspaces but currently gives authenticated staff organizers access to all workspaces. Add role-based access, a configurable event currency, and a reviewed data-protection plan before inviting additional team members or using sensitive real-world records.
