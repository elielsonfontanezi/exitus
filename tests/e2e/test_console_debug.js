const { chromium } = require('playwright');

async function debugError() {
  console.log('🔍 Debugando erro 500...');
  
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  const responses = [];
  
  page.on('response', response => {
    if (response.status() >= 400) {
      responses.push({
        url: response.url(),
        status: response.status(),
        statusText: response.statusText()
      });
    }
  });
  
  try {
    await page.goto('http://localhost:8080/dashboard/');
    await page.waitForTimeout(2000);
    
    console.log('\n=== RESPOSTAS COM ERRO ===');
    if (responses.length > 0) {
      responses.forEach((resp, i) => {
        console.log(`${i+1}. ${resp.status} ${resp.statusText}: ${resp.url}`);
      });
    } else {
      console.log('✅ Nenhuma resposta com erro!');
    }
    
  } catch (error) {
    console.error('❌ Erro no teste:', error.message);
  }
  
  await browser.close();
}

debugError().catch(console.error);
