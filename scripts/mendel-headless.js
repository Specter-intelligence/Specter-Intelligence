const { chromium } = require('playwright');

async function submitMendelWallet(walletAddress) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    console.log('Navigating to Mendel...');
    await page.goto('https://mendel.network');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check if Mendel Points are locked
    const pointsText = await page.textContent('body');
    if (pointsText.includes('Mendel Points are now locked')) {
      console.log('Mendel Points are locked - snapshot may have happened');
    }
    
    // Look for wallet submission form
    const walletInput = await page.$('input[type="text"], input[placeholder*="Ethereum"], input[placeholder*="0x"]');
    
    if (walletInput) {
      console.log('Found wallet input field');
      await walletInput.fill(walletAddress);
      
      // Look for submit button
      const submitButton = await page.$('button[type="submit"], button:has-text("Submit"), input[type="submit"]');
      if (submitButton) {
        await submitButton.click();
        console.log('Submitted wallet address');
        
        // Wait for response
        await page.waitForTimeout(3000);
        
        // Check for success message
        const responseText = await page.textContent('body');
        if (responseText.includes('thank') || responseText.includes('success') || responseText.includes('registered')) {
          console.log('✅ Wallet submission appears successful');
        } else {
          console.log('⚠️ Submission completed but no confirmation message found');
        }
      } else {
        console.log('❌ No submit button found');
      }
    } else {
      console.log('❌ No wallet input field found on page');
      console.log('Page content preview:', (await page.textContent('body')).substring(0, 500));
    }
    
    // Take screenshot for debugging
    await page.screenshot({ path: '/tmp/mendel-screenshot.png' });
    console.log('Screenshot saved to /tmp/mendel-screenshot.png');
    
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await browser.close();
  }
}

// Get wallet address from command line or use default
const walletAddress = process.argv[2] || '0x889d72eeaa4a9e0f18803d01a1a7a797d5e26ac4';
submitMendelWallet(walletAddress);