import os

# 1. Define the directory path to scan
directory_path = "images/photos"  # Use "." for the current directory, or specify an absolute path 
output_filename = "file_list.txt"

# 2. Get the list of files in the directory
# os.listdir() returns all entries (files and subdirectories)
entries = os.listdir(directory_path)
files_list = [entry for entry in entries if os.path.isfile(os.path.join(directory_path, entry))]

# 3. Write the file names to a text file
with open(output_filename, "w") as f:
    for filename in files_list:
        text = ''
        text += '''
        <table class="content-table">
            <tr>
                <td>
                    <img style='height: 100%; width: 100%; object-fit: contain; max-width:625px;' src="/images/photos/{}"/>
                    <div style="text-align: center;">...</div>
                </td>
            </tr>
        </table>
        <br>
'''.format(filename)
        f.write(text) # os.linesep adds a newline character appropriate for the OS

print(f"File names have been written to {output_filename}")