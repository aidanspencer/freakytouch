#### Run this script to add new photos from images/photos/ to photos/index.html
#### Photos that aren't on the page yet are added to the top; existing photos keep their order and captions

import os

from generated import generated_section, replace_generated

photos_dir = "images/photos"
page = "photos/index.html"

with open(page) as f:
    html = f.read()

start, end = generated_section(html)
existing = html[start:end]

new_photos = [
    filename for filename in sorted(os.listdir(photos_dir))
    if os.path.isfile(os.path.join(photos_dir, filename))
    and f'src="/images/photos/{filename}"' not in existing
]

content = '\n'
for filename in new_photos:
    content += '''        <table class="content-table">
            <tr>
                <td>
                    <img class="content-img" src="/images/photos/{}" alt="">
                    <!-- <div>...</div> -->
                </td>
            </tr>
        </table>
        <br>

'''.format(filename)

with open(page, "w") as f:
    f.write(replace_generated(html, content + existing.lstrip('\n').removesuffix('        ')))

print(f"Added {len(new_photos)} new photo(s) to {page}: {new_photos}")
