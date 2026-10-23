#### Run this script to sync photos/index.html with the photos in images/photos/
#### Photos that aren't on the page yet are added to the top; existing photos keep their order and captions
#### Photos whose file has been deleted from images/photos/ are removed from the page
#### (so to take a photo down, delete its file; deleting only its HTML would get it added back)
#### A photo's caption is read from images/photos/captions/<photo filename>.txt (shows "..." if there isn't one)
#### New photos larger than MAX_SIZE pixels are shrunk (needs Pillow: pip install pillow; skipped if it isn't installed)

import html
import os
import re

from generated import generated_section, replace_generated

try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None

photos_dir = "images/photos"
captions_dir = "images/photos/captions"
page = "photos/index.html"
image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
MAX_SIZE = 1600


def read_caption(filename):
    caption_file = os.path.join(captions_dir, filename + ".txt")
    if not os.path.isfile(caption_file):
        return None
    with open(caption_file, encoding="utf-8") as f:
        return f.read().strip() or None


def shrink(path):
    """Shrink the photo so its longest side is at most MAX_SIZE, rotating it upright and dropping its metadata (e.g. GPS location)."""
    with Image.open(path) as img:
        if max(img.size) <= MAX_SIZE or getattr(img, "is_animated", False):
            return
        img = ImageOps.exif_transpose(img)
        img.thumbnail((MAX_SIZE, MAX_SIZE))
    if path.lower().endswith(('.jpg', '.jpeg')):
        img.convert("RGB").save(path, quality=85)
    else:
        img.save(path)
    print(f"Shrunk {path} to {img.size[0]}x{img.size[1]}")


with open(page, encoding="utf-8") as f:
    page_html = f.read()

start, end = generated_section(page_html)
existing = page_html[start:end]

# Remove photos whose file is gone. Each photo is a <table class="content-table"> block followed by <br>.
removed_photos = []
def remove_if_deleted(match):
    filename = html.unescape(re.search(r'src="/images/photos/([^"]*)"', match.group(0)).group(1))
    if os.path.isfile(os.path.join(photos_dir, filename)):
        return match.group(0)
    removed_photos.append(filename)
    caption_file = os.path.join(captions_dir, filename + ".txt")
    if os.path.isfile(caption_file):
        os.remove(caption_file)
    return ''
existing = re.sub(r'[ \t]*<table class="content-table">.*?</table>\s*<br>\n(?:[ \t]*\n)?', remove_if_deleted, existing, flags=re.DOTALL)

new_photos = [
    filename for filename in sorted(os.listdir(photos_dir))
    if filename.lower().endswith(image_extensions)
    and f'src="/images/photos/{filename}"' not in existing
]

if new_photos and Image is None:
    print("Pillow isn't installed, so new photos won't be shrunk (pip install pillow)")

content = '\n'
for filename in new_photos:
    if Image is not None:
        shrink(os.path.join(photos_dir, filename))
    caption = read_caption(filename)
    content += '''        <table class="content-table">
            <tr>
                <td>
                    <img class="content-img" src="/images/photos/{}" alt="{}">
                    <div>{}</div>
                </td>
            </tr>
        </table>
        <br>

'''.format(html.escape(filename), html.escape(caption or ''), html.escape(caption or '...'))

with open(page, "w", encoding="utf-8") as f:
    f.write(replace_generated(page_html, content + existing.lstrip('\n').removesuffix('        ')))

print(f"Added {len(new_photos)} new photo(s) to {page}: {new_photos}")
print(f"Removed {len(removed_photos)} deleted photo(s) from {page}: {removed_photos}")
