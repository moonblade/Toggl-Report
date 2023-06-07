from toggl import Toggl
import settings
import subprocess
import os

def convertToPdf(html_file):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, 'htmlToPdf.js')
    command = ['node', script_path, html_file]
    subprocess.run(command, check=True)

def main():
    t = Toggl(settings.apiKey)
    convertToPdf("report.html")

if __name__ == "__main__":
    main()
