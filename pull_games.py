import os

# 1. Define the directory path to scan
directory_path = "games"  # Use "." for the current directory, or specify an absolute path 
output_filename = "gen_html/games_index_main_html.html"

# 2. Get the list of files in the directory
# os.listdir() returns all entries (files and subdirectories)
entries = os.listdir(directory_path)
files_list = [entry for entry in entries if os.path.isfile(os.path.join(directory_path, entry))]

# # 3. Write the file names to a text file
# with open(output_filename, "w") as f:
#     for filename in files_list:
#         text = ''
#         text += '''
#         <table class="content-table">
#             <tr>
#                 <td>
#                     <img style='width: 100%; max-width:625px;' src="/images/photos/{}"/>
#                     <div style="text-align: center;">...</div>
#                 </td>
#             </tr>
#         </table>
#         <br>
# '''.format(filename)
#         f.write(text) # os.linesep adds a newline character appropriate for the OS

# print(f"File names have been written to {output_filename}, insert between <main> tags")

output_text = ''
left_side = True

output_text += '''      <div style="width: 100%; max-width: 625px; margin-left: auto; margin-right: auto;">'''

for subdir, dirs, files in os.walk(directory_path):
    if subdir == 'games':
        continue

    subdir_text = subdir.replace("\\", "/")
    print(subdir_text)
    
    output_text += '''          <div class="{}">'''.format("left" if left_side else "right")

    output_text += '''              <a href="/{}/"><img style='width: 100%; object-fit: contain;' src="/{}/icon.png"/></a>
                <div style="text-align: center;"><a href="/{}/">/{}</a></div>
            </div>'''.format(subdir_text,subdir_text,subdir_text,subdir_text.replace('games/',''))

    left_side = not left_side

output_text += '''        </div>

        '''

with open(output_filename, "w") as f:
    f.write(output_text)

print(f"Games have been written to {output_filename}, insert between <main> tags")