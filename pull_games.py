#### Run this script to rebuild the games pages from the folders in games/
#### Each game folder needs an .swf file and an icon (icon.png, icon.jpg, ...)
#### - Writes games/<game>/index.html for each game, using games/index.html as the page template
#### - Rebuilds the game grid in games/index.html (between the BEGIN GENERATED / END GENERATED comments)
#### Ignores folders beginning with '&'

import os

from generated import replace_generated

games_dir = "games"
games_page = "games/index.html"

with open(games_page) as f:
    template = f.read()

grid = '''
        <div class="game-grid">'''
left_side = True

for game in sorted(os.listdir(games_dir)):
    game_dir = os.path.join(games_dir, game)
    if not os.path.isdir(game_dir) or game.startswith('&'):
        continue

    files = sorted(os.listdir(game_dir))
    swf_filename = next(f for f in files if f.endswith('.swf'))
    icon_filename = next(f for f in files if f.startswith('icon.'))
    game_name = game.replace('-', ' ').title()
    print(f"{game_name}: {swf_filename}, {icon_filename}")

    grid += '''
            <div class="{}">
                <a href="/games/{}/"><img class="game-icon" src="/games/{}/{}" alt="{}"></a>
                <div><a href="/games/{}/">{}</a></div>
            </div>'''.format("left" if left_side else "right", game, game, icon_filename, game_name, game, game_name)
    left_side = not left_side

    player = '''
        <script src="https://unpkg.com/@ruffle-rs/ruffle"></script>
        <object class="game">
            <param name="movie" value="{}">
            <embed src="{}">
        </object>
'''.format(swf_filename, swf_filename)

    with open(os.path.join(game_dir, "index.html"), "w") as f:
        f.write(replace_generated(template, player))

grid += '''
        </div>
'''

with open(games_page, "w") as f:
    f.write(replace_generated(template, grid))

print(f"Games have been written to {games_page}")
