from toggl import Toggl
import settings
import subprocess

def convertToPdf(inputHtmlFile):
    # Execute the Node.js script using subprocess
    try:
        subprocess.run(['node', 'htmlToPdf.js', inputHtmlFile], check=True)
        print("PDF conversion completed!")
    except subprocess.CalledProcessError as e:
        print("PDF conversion failed:", e)

inputHtmlFile = 'report.html'
def main():
    t = Toggl(settings.apiKey)
    convertToPdf("report.html")

if __name__ == "__main__":
    main()
