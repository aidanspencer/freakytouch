#### Run this script to generate the index.html file for each folder in games/ containing an .swf file and icon.png
#### Also creates games_index_main.html which should be inserted in the <main> tag in games/index.html
#### Ignores folders beginning with '&'

import os

# 1. Define the directory path to scan
directory_path = "games"  # Use "." for the current directory, or specify an absolute path 
output_filename = "gen_html/games_index_main.html"

# 2. Get the list of files in the directory
# os.listdir() returns all entries (files and subdirectories)
entries = os.listdir(directory_path)
files_list = [entry for entry in entries if os.path.isfile(os.path.join(directory_path, entry))]

output_text = ''
left_side = True

output_text += '''      <div style="width: 100%; max-width: 625px; margin-left: auto; margin-right: auto;">'''

for subdir, dirs, files in os.walk(directory_path):
    dirs.sort()
    if subdir == 'games':
        continue

    subdir_text = subdir.replace("\\", "/")
    print(subdir_text)

    game_name = subdir_text.replace('games/','')
    game_name = game_name.replace('-',' ')
    print(game_name.title())
    
    if game_name.startswith('&'):
        continue

    game_html = subdir_text + '/index.html'
    print(game_html)

    output_text += '''          <div class="{}">'''.format("left" if left_side else "right")

    output_text += '''              <a href="/{}/"><img style='width: 100%; max-height: 200px;' src="/{}/icon.png"/></a>
                <div style="text-align: center;"><a href="/{}/">{}</a></div>
            </div>'''.format(subdir_text,subdir_text,subdir_text,game_name.title())

    left_side = not left_side

    files = []
    for file in os.listdir(subdir):
        if file.endswith('.swf') and os.path.isfile(os.path.join(subdir_text, file)):
            files.append(file)
    print(files[0])

    swf_filename = files[0]
    
    index_html = '''<!DOCTYPE html>
<html>
<style>
table, th, td {
  border:1px solid black;
  text-align: center;
}
</style>
'''
    index_html += '''<body>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Freaky Touch - Games</title>
    <link rel="stylesheet" href="/style.css"> 
    <link rel="icon" type="image/png" href="/images/favicon.ico"/>
    <script type="text/javascript" src="/js/randomator.js"></script>
</head>
<body class="mainview">
    <header>
        <table class="title-table">
            <tr>
                <td>
                    <h1 class="title-text">
                        <img style='height: 50px;' src="/images/rasta_banana.gif"/>
                        Games
                        <img style='height: 50px;' src="/images/rasta_banana.gif"/>
                    </h1>
                </td>
            </tr>
        </table>
        <div style="width: 100%; max-width: 710px; margin-left: auto; margin-right: auto;">
            <ul class="nav-bar">
                <li class="nav-item"><a class="nav-link" href="/"> Home </a></li>
                <li class="nav-item"><a class="nav-link" href="/photos/">Photos</a></li>
                <li class="nav-item"><a class="nav-link" href="/videos/">Videos</a></li>
                <li class="nav-item"><a class="nav-link" href="/team/"> Team </a></li>
                <li class="nav-item"><a class="nav-link" href="/games/">Games</a></li>
                <li class="nav-item"><a class="nav-link" href="/">Store</a></li>
            </ul>
        </div>
    </header>
    <main>
        <script src="https://unpkg.com/@ruffle-rs/ruffle"></script>
        <object style="width: 100%; max-width: 625px;">
            <param name="movie" value="{}">
            <embed src="{}"></embed>
        </object>
    </main>
    <footer>
        <p>&copy; 2026 Freaky Touch</p>
    </footer>
</body>
<script type="text/javascript">
    randomator();
</script>
</html>
'''.format(swf_filename, swf_filename)

    with open(game_html, "w") as f:
        f.write(index_html)

output_text += '''        </div>

        '''

with open(output_filename, "w") as f:
    f.write(output_text)

print(f"Games have been written to {output_filename}, insert between <main> tags")