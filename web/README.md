# Web folder

Static page, no build step: open `index.html` or upload the whole folder to any web host.

- `index.html` - table of SARFAESI cases, timeline, applicable provision, and annexure PDF downloads
- `annexures/` - 23 blank annexure PDFs (links in the page point here)
- `SARFAESI_Recovery_Timeline_and_Document_Register.pdf` - full printable timeline

Regenerate the annexures after editing `recovery/formats.py`: `python3 web/build_annexure_pdfs.py` (needs reportlab).
