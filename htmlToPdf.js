const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function convertHtmlToPdf(inputHtmlFile, outputPdfFile, index) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Read the report.json file
  const jsonFile = path.join(__dirname, 'report.json');
  const inputFile = path.join(__dirname, inputHtmlFile);
  const reportData = fs.readFileSync(jsonFile, 'utf-8');
  const jsonData = JSON.parse(reportData);

  // Read the HTML template file
  const htmlContent = fs.readFileSync(inputFile, 'utf-8');

  // Inject the report data into the HTML template
  const injectedHtmlContent = htmlContent.replace(
    'var reportData = {};',
    `var reportData = ${JSON.stringify(jsonData)};
     index=${index}`
  );

  await page.setContent(injectedHtmlContent, { waitUntil: 'networkidle0' });

  // Extract the output filename from window.fileName variable or fallback to "report.pdf"
  const outputFilename = await page.evaluate(() => {
    return window.fileName || 'report';
  });

  // Generate the PDF using the output filename
  const outputPath = path.join(outputPdfFile, `${outputFilename}.pdf`);
  await page.pdf({ path: outputPath, format: 'A4' });

  await browser.close();

  console.log(`PDF generation completed! Saved as: ${outputPath}`);
}

// Extract input file path from command-line argument
const inputHtmlFile = process.argv[2];
const index = parseInt(process.argv[3]);

// Check if input file path is provided
if (!inputHtmlFile) {
  console.error('Please provide the input file path.');
  console.log('Usage: node html_to_pdf.js [input.html]');
  process.exit(1);
}

const outputDirectory = path.join(process.env.HOME, 'Downloads');

convertHtmlToPdf(inputHtmlFile, outputDirectory, index);

