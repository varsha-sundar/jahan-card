# Jahan · Product Wrapped

Static “Spotify Wrapped”–style farewell page for Jahan (Product → Delivery Ops at Via). No build step: open via a local HTTP server or any static host.

## Preview locally

From this directory:

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080/` in a browser.

**Why:** The page loads `team-source.txt` with `fetch()` for **photos**. Browsers block that from `file://` for the text file; teammate **notes** always load from `embedded-notes.js`, so notes still show without a server.

## Customize

- **Copy & stats:** Edit the `PAGE` object in `index.html`.
- **Photos:** Edit `team-source.txt` — uncomment up to **three** `=== PHOTOS ===` lines when image files exist under `photos/`.
- **Teammate notes:** Edit **`embedded-notes.js`** (`window.__FAREWELL_NOTES_BLOCK__`). That is the only source for messages; keep the `## Name` / body format.
- **Look:** Adjust colors in `css/styles.css` (`:root` and panel themes).

## Git

```bash
git init
git add .
git commit -m "Add Jahan Product Wrapped farewell page"
git remote add origin <your-remote-url>
git push -u origin main
```

For **GitHub Pages**, enable Pages on the branch containing these files (root or `/docs` if you move the site). For **GitLab Pages**, add a `pages` job that publishes this folder as the artifact.
