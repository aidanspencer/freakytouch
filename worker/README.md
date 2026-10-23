# Photo uploads

Lets visitors add photos to the Photos page without access to this repo.

```
"Add a photo" form on /photos/   (js/upload.js: shrinks the photo, adds the Turnstile CAPTCHA token)
        ↓
Cloudflare Worker                (worker/src/index.js: checks the CAPTCHA and file, opens a pull request)
        ↓
Pull request "Photo upload: ..." → you merge it to publish, or close it to reject
        ↓
GitHub Action                    (.github/workflows/photos.yml: shrinks new photos, runs pull_photos.py, commits)
        ↓
GitHub Pages redeploys the site
```

Captions are saved as `images/photos/captions/<photo filename>.txt`. `pull_photos.py` puts them under the photo.

## One-time setup

### 1. Turnstile (CAPTCHA)
1. In the Cloudflare dashboard, open **Turnstile** → **Add widget**.
2. Hostnames: `freakytouch.com`, `www.freakytouch.com`, `localhost`. Widget mode: **Managed**.
3. Put the **site key** in `photos/index.html` (`data-sitekey="..."`, replacing the test key).
4. Keep the **secret key** for step 3.

### 2. GitHub token
1. GitHub → **Settings** → **Developer settings** → **Fine-grained personal access tokens** → **Generate new token**.
2. Repository access: **Only select repositories** → `freakytouch`.
3. Permissions: **Contents** → Read and write, **Pull requests** → Read and write.
4. Note the expiry date. Uploads stop working when the token expires, so set a reminder to replace it.

### 3. The Worker
1. Cloudflare dashboard → **Workers & Pages** → **Create application** → **Start with Hello World!**
   (not "Upload your static files", which is for static sites and rejects JavaScript).
   Name it `freakytouch-uploads`, **Deploy**.
2. **Edit code**, replace everything in the editor with the contents of `worker/src/index.js`, **Deploy**.
3. **Settings** → **Variables and Secrets**, add:

   | Name | Type | Value |
   |---|---|---|
   | `GITHUB_OWNER` | Text | `aidanspencer` |
   | `GITHUB_REPO` | Text | `freakytouch` |
   | `ALLOWED_ORIGINS` | Text | `https://www.freakytouch.com,https://freakytouch.com,http://localhost:8000` |
   | `GITHUB_TOKEN` | Secret | the token from step 2 |
   | `TURNSTILE_SECRET` | Secret | the Turnstile secret key from step 1 |

4. Copy the Worker's URL (`https://freakytouch-uploads.<something>.workers.dev`) into `UPLOAD_URL` in `js/upload.js`.

(If you install Node.js, you can instead deploy from this folder with `npx wrangler deploy` and set the secrets with `npx wrangler secret put GITHUB_TOKEN`. The settings in `wrangler.toml` match the table above.)

### 4. GitHub repo settings (auto-delete upload branches)
Every upload creates a new branch in the repo (named like `upload/20261022-1a2b3c4d`). This setting makes GitHub
delete that branch automatically once you merge its pull request, so they don't pile up.

1. Go to https://github.com/aidanspencer/freakytouch.
2. Click the **Settings** tab (gear icon) in the row of tabs at the top of the repo, the same row as **Code**, **Issues** and **Pull requests**.
   If the row is cut off on a narrow window, it's under the **...** menu at the end of the row.
3. You land on the **General** page (first item in the left sidebar). Scroll about halfway down to the section headed **Pull Requests**.
4. Tick **Automatically delete head branches**. It saves straight away; there's no Save button.

That's the only repo setting needed. The Action already has permission to commit, because `.github/workflows/photos.yml` asks for it.

### 5. Publish and test
1. Commit and push all the changes (`photos/index.html`, `js/upload.js`, `pull_photos.py`, `style.css`, `.github/`, `worker/`).
2. Wait a minute or two for GitHub Pages to redeploy. You can watch it under the repo's **Actions** tab.
3. Open https://www.freakytouch.com/photos/, choose a photo, type a caption, wait for the CAPTCHA box to show a tick, and click **Upload**.
   You should see "Thanks! Your photo will show up here once it's approved."
4. On GitHub, open the **Pull requests** tab. There should be a new PR titled "Photo upload: <your caption>". Merge it (see below).
5. Open the **Actions** tab: an "Update photos page" run starts, then a "pages build and deployment" run.
   When both have a green tick, reload the Photos page and your photo should be at the top with its caption.

If the upload shows an error instead, see **Troubleshooting** below.

## Reviewing uploads
Each upload arrives as a pull request. You get a GitHub notification (and an email, depending on your notification settings).

1. Open the PR and click the **Files changed** tab to see the photo. The caption is in the PR description and in the `.txt` file.
2. To **publish** it: go back to the **Conversation** tab, click **Merge pull request**, then **Confirm merge**.
   The Action adds it to the Photos page a minute or two later.
3. To **reject** it: click **Close pull request** at the bottom of the **Conversation** tab, then click **Delete branch** in the
   message that appears. A rejected photo never reaches `main`, so it never appears on the site.

This works in the GitHub mobile app too: **Pull requests** → open the PR → **Merge** or **Close**.

## Removing a photo
Delete the photo's **file** from `images/photos/`. Don't just delete its HTML from `photos/index.html`: the Action adds every
photo in the folder that isn't on the page, so the photo would come back the next time it runs.

On github.com: open `images/photos/`, click the photo, click the **...** menu (top right of the file view) → **Delete file** →
**Commit changes**. The Action then removes it from the Photos page, along with its caption file.
Locally: delete the file, run `python pull_photos.py`, then commit and push.

## Troubleshooting
- **"The CAPTCHA check failed"**: the site key in `photos/index.html` and the `TURNSTILE_SECRET` on the Worker come from different
  widgets, or the site's hostname isn't in the widget's hostname list (step 1.2).
- **"Uploads are only accepted from the Freaky Touch website"**: the address in your browser's address bar isn't in `ALLOWED_ORIGINS` (step 3.3).
  It must match exactly, including `https://` or `www.`.
- **"Something went wrong saving your photo"**: the Worker reached GitHub, but GitHub refused. Usually the token has expired or is missing a permission (step 2).
  For the exact error, open the Worker in the Cloudflare dashboard → **Logs** (or **Observability**), and try the upload again.
- **"Couldn't upload that photo"**: the browser couldn't read the image (e.g. a HEIC photo in a desktop browser) or couldn't reach the Worker.
  Check that `UPLOAD_URL` in `js/upload.js` is the Worker's URL.

## Updating the Worker
Edit `worker/src/index.js`, then paste it into the dashboard editor again (or run `npx wrangler deploy`).
The code in this repo is not deployed automatically.
