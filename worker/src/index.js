// Receives photo uploads from the form on /photos/ and opens a pull request adding the photo to images/photos/.
// Merging the PR publishes the photo (the "Update photos page" GitHub Action adds it to photos/index.html).
// Setup and deploy steps are in worker/README.md.

const MAX_BYTES = 5 * 1024 * 1024; // the form shrinks photos to well under this before sending
const MAX_CAPTION = 200;

export default {
    async fetch(request, env) {
        const allowedOrigins = env.ALLOWED_ORIGINS.split(",").map((origin) => origin.trim());
        const origin = request.headers.get("Origin") || "";
        const headers = {
            "Access-Control-Allow-Origin": allowedOrigins.includes(origin) ? origin : allowedOrigins[0],
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Vary": "Origin",
        };
        const reply = (status, message) => Response.json({ message }, { status, headers });

        if (request.method === "OPTIONS") return new Response(null, { headers });
        if (request.method !== "POST") return reply(405, "Method not allowed.");
        if (!allowedOrigins.includes(origin)) return reply(403, "Uploads are only accepted from the Freaky Touch website.");

        let form;
        try {
            form = await request.formData();
        } catch {
            return reply(400, "That upload couldn't be read.");
        }
        const photo = form.get("photo");
        const caption = String(form.get("caption") || "").replace(/[\u0000-\u001f\u007f]/g, " ").trim();

        if (!(await verifyTurnstile(form.get("cf-turnstile-response"), request, env))) {
            return reply(403, "The CAPTCHA check failed. Refresh the page and try again.");
        }
        if (!(photo instanceof File)) return reply(400, "No photo was attached.");
        if (photo.size > MAX_BYTES) return reply(413, "That photo is too big.");
        if (caption.length > MAX_CAPTION) return reply(400, `Captions can be at most ${MAX_CAPTION} characters.`);

        const bytes = new Uint8Array(await photo.arrayBuffer());
        if (!isJpeg(bytes)) return reply(400, "Photos must be JPEGs.");

        const id = `${new Date().toISOString().slice(0, 10).replaceAll("-", "")}-${crypto.randomUUID().slice(0, 8)}`;
        let pullRequest;
        try {
            pullRequest = await openPullRequest(env, { id, filename: `upload-${id}.jpg`, bytes, caption });
        } catch (error) {
            console.error(error);
            return reply(502, "Something went wrong saving your photo. Try again later.");
        }
        await notify(env, pullRequest, caption);
        return reply(200, "Thanks! Your photo will show up here after it's approved by Toom.");
    },
};

async function verifyTurnstile(token, request, env) {
    if (!token) return false;
    const response = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
        method: "POST",
        body: new URLSearchParams({
            secret: env.TURNSTILE_SECRET,
            response: token,
            remoteip: request.headers.get("CF-Connecting-IP") || "",
        }),
    });
    const result = await response.json();
    return result.success === true;
}

function isJpeg(bytes) {
    return bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff;
}

// Creates branch upload/<id> off main, commits the photo (and its caption, if any) to it, and opens a PR.
async function openPullRequest(env, { id, filename, bytes, caption }) {
    const branch = `upload/${id}`;
    const main = await github(env, "GET", "/git/ref/heads/main");
    await github(env, "POST", "/git/refs", { ref: `refs/heads/${branch}`, sha: main.object.sha });

    await github(env, "PUT", `/contents/images/photos/${filename}`, {
        message: `Add uploaded photo ${filename}`,
        content: toBase64(bytes),
        branch,
    });
    if (caption) {
        await github(env, "PUT", `/contents/images/photos/captions/${filename}.txt`, {
            message: `Add caption for ${filename}`,
            content: toBase64(new TextEncoder().encode(caption + "\n")),
            branch,
        });
    }

    return github(env, "POST", "/pulls", {
        title: `Photo upload: ${caption || filename}`,
        head: branch,
        base: "main",
        body: [
            "A visitor uploaded a photo from the Photos page.",
            "",
            `**Caption:** ${caption || "(none)"}`,
            "",
            "Check the photo under **Files changed**. Merge to publish it, or close this PR to reject it (then delete the branch).",
        ].join("\n"),
    });
}

// Sends a push notification through ntfy.sh (subscribe to the NTFY_TOPIC topic in the ntfy app); tapping it opens the PR.
// GitHub itself doesn't notify you, because the PR is opened with your own token. Skipped if NTFY_TOPIC isn't set.
async function notify(env, pullRequest, caption) {
    if (!env.NTFY_TOPIC) return;
    try {
        const response = await fetch(`https://ntfy.sh/${env.NTFY_TOPIC}`, {
            method: "POST",
            headers: { "Title": "New photo upload", "Click": pullRequest.html_url, "Tags": "camera" },
            body: caption || "(no caption)", // in the body, not a header, because headers can't hold emoji
        });
        if (!response.ok) console.error(`ntfy failed: ${response.status} ${await response.text()}`);
    } catch (error) {
        console.error(error); // the upload already worked, so don't fail it over a missed notification
    }
}

function toBase64(bytes) {
    let binary = "";
    for (let i = 0; i < bytes.length; i += 0x8000) {
        binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
    }
    return btoa(binary);
}

async function github(env, method, path, body) {
    const response = await fetch(`https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}${path}`, {
        method,
        headers: {
            "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "freakytouch-uploads",
        },
        body: body && JSON.stringify(body),
    });
    if (!response.ok) throw new Error(`GitHub ${method} ${path} failed: ${response.status} ${await response.text()}`);
    return response.json();
}
