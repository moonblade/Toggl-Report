from toggl import Toggl
import settings
import subprocess
import os

def convertToPdf(html_file, index):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, 'htmlToPdf.js')
    nodePath = "/Users/moonblade/.nvm/versions/node/v19.9.0/bin/node"
    # nodePath = "node"
    command = [nodePath, script_path, html_file, str(index)]
    subprocess.run(command, check=True)

def main():
    t = Toggl(settings.apiKey)
    for x in range(len(t.timeEntries)):
        convertToPdf("report.html", x)

if __name__ == "__main__":
    main()
