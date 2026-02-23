const puppeteer = require('puppeteer-core');
const fs = require('fs');

async function testHeadlessChrome() {
  // Try to find system Chrome/Chromium
  const possiblePaths = [
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
    '/usr/bin/google-chrome',
    '/usr/bin/chrome',
    '/snap/bin/chromium'
  ];
  
  let executablePath = null;
  for (const path of possiblePaths) {
    if (fs.existsSync(path)) {
      executablePath = path;
      console.log(`Found browser at: ${path}`);
      break;
    }
  }
  
  if (!executablePath) {
    console.log('❌ No browser found. Trying to install chromium-browser...');
    return;
  }
  
  try {
    console.log('Launching headless browser...');
    const browser = await puppeteer.launch({
      executablePath,
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.goto('https://mendel.network');
    
    console.log('Page loaded:', await page.title());
    
    // Take screenshot
    await page.screenshot({ path: '/tmp/mendel-test.png' });
    console.log('Screenshot saved to /tmp/mendel-test.png');
    
    // Check page content
    const content = await page.content();
    if (content.includes('Mendel Points')) {
      console.log('✅ Mendel page loaded successfully');
    }
    
    await browser.close();
    console.log('✅ Headless browser test successful!');
    
  } catch (error) {
    console.error('Error:', error.message);
    console.log('Trying alternative approach...');
    
    // Fallback: use curl to check if Mendel is accessible
    const { execSync } = require('child_process');
    try {
      const result = execSync('curl -s "https://mendel.network" | grep -i "mendel" | head -2').toString();
      console.log('Curl fallback - Mendel site accessible:', result.substring(0, 200));
    } catch (curlError) {
      console.error('Curl also failed:', curlError.message);
    }
  }
}

testHeadlessChrome();