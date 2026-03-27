const { chromium } = require('playwright');

async function quickTest() {
  console.log('🔍 Testando console errors...');
  
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  const consoleErrors = [];
  const notFoundUrls = [];
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });
  
  page.on('response', response => {
    if (response.status() === 404) {
      notFoundUrls.push(response.url());
    }
  });
  
  try {
    // Ir direto para o dashboard (com token mock)
    await page.goto('http://localhost:8080/dashboard/');
    await page.waitForTimeout(2000);
    
    console.log('\n=== CONSOLE ERRORS ===');
    if (consoleErrors.length > 0) {
      console.log(`❌ ${consoleErrors.length} erros:`);
      consoleErrors.forEach((error, i) => console.log(`${i+1}. ${error}`));
    } else {
      console.log('✅ Nenhum erro de console!');
    }
    
    console.log('\n=== 404 URLs ===');
    if (notFoundUrls.length > 0) {
      console.log(`❌ ${notFoundUrls.length} URLs 404:`);
      notFoundUrls.forEach((url, i) => console.log(`${i+1}. ${url}`));
    } else {
      console.log('✅ Nenhum 404 encontrado!');
    }
    
  } catch (error) {
    console.error('❌ Erro no teste:', error.message);
  }
  
  await browser.close();
}

quickTest().catch(console.error);
