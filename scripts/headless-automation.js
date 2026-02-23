const puppeteer = require('puppeteer-core');
const fs = require('fs');

class HeadlessAutomation {
  constructor() {
    this.browser = null;
    this.page = null;
    this.executablePath = '/usr/bin/chromium-browser';
  }
  
  async launch() {
    if (!fs.existsSync(this.executablePath)) {
      throw new Error(`Browser not found at ${this.executablePath}`);
    }
    
    this.browser = await puppeteer.launch({
      executablePath: this.executablePath,
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });
    
    this.page = await this.browser.newPage();
    await this.page.setViewport({ width: 1280, height: 800 });
    
    console.log('Headless browser launched');
    return this;
  }
  
  async goto(url) {
    if (!this.page) throw new Error('Browser not launched');
    console.log(`Navigating to ${url}`);
    await this.page.goto(url, { waitUntil: 'networkidle2' });
    return this;
  }
  
  async screenshot(path = '/tmp/browser-screenshot.png') {
    await this.page.screenshot({ path });
    console.log(`Screenshot saved to ${path}`);
    return this;
  }
  
  async fillForm(selector, value) {
    await this.page.waitForSelector(selector, { timeout: 5000 });
    await this.page.type(selector, value);
    console.log(`Filled ${selector} with ${value.substring(0, 10)}...`);
    return this;
  }
  
  async click(selector) {
    await this.page.waitForSelector(selector, { timeout: 5000 });
    await this.page.click(selector);
    console.log(`Clicked ${selector}`);
    return this;
  }
  
  async getText(selector) {
    await this.page.waitForSelector(selector, { timeout: 5000 });
    const text = await this.page.$eval(selector, el => el.textContent);
    return text.trim();
  }
  
  async close() {
    if (this.browser) {
      await this.browser.close();
      console.log('Browser closed');
    }
  }
  
  // Specific task: Mendel wallet submission
  async submitMendelWallet(walletAddress) {
    try {
      await this.goto('https://mendel.network');
      await this.screenshot('/tmp/mendel-before.png');
      
      // Check page state
      const pageText = await this.page.content();
      if (pageText.includes('Mendel Points are now locked')) {
        console.log('⚠️ Mendel Points are locked - snapshot may have happened');
      }
      
      // Look for wallet input (simplified - would need actual selectors)
      // This is a placeholder - need to inspect actual Mendel form
      console.log('Page loaded. Manual inspection needed for form selectors.');
      console.log('Current page title:', await this.page.title());
      
      // For now, just verify we can access the site
      return { success: true, message: 'Mendel site accessible, form selectors need inspection' };
      
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
  
  // Generic form submission
  async submitGenericForm(url, formData) {
    // formData: { inputSelectors: { selector: value }, submitSelector }
    await this.goto(url);
    
    for (const [selector, value] of Object.entries(formData.inputSelectors)) {
      await this.fillForm(selector, value);
    }
    
    await this.click(formData.submitSelector);
    await this.page.waitForTimeout(3000);
    
    return await this.screenshot('/tmp/form-submission.png');
  }
}

// Export for use in other scripts
module.exports = HeadlessAutomation;

// If run directly, test Mendel
if (require.main === module) {
  (async () => {
    const auto = new HeadlessAutomation();
    try {
      await auto.launch();
      const result = await auto.submitMendelWallet('0x889d72eeaa4a9e0f18803d01a1a7a797d5e26ac4');
      console.log('Result:', result);
      await auto.screenshot('/tmp/mendel-final.png');
    } catch (error) {
      console.error('Error:', error);
    } finally {
      await auto.close();
    }
  })();
}