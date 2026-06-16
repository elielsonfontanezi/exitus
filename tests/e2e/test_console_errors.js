const { chromium } = require('playwright');

async function checkConsoleErrors() {
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
  
  // Fazer login primeiro
  await page.goto('http://localhost:8080/auth/login');
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'senha123');
  await page.click('button[type="submit"]');
  await page.waitForURL('http://localhost:8080/dashboard/');
  
  // Navegar para o dashboard
  await page.goto('http://localhost:8080/dashboard/');
  await page.waitForTimeout(3000);
  
  console.log('\n=== CONSOLE ERRORS ===');
  if (consoleErrors.length > 0) {
    console.log(`Encontrados ${consoleErrors.length} erros:`);
    consoleErrors.forEach((error, i) => console.log(`${i+1}. ${error}`));
  } else {
    console.log('✅ Nenhum erro de console encontrado!');
  }
  
  console.log('\n=== 404 URLs ===');
  if (notFoundUrls.length > 0) {
    console.log(`Encontrados ${notFoundUrls.length} URLs 404:`);
    notFoundUrls.forEach((url, i) => console.log(`${i+1}. ${url}`));
  } else {
    console.log('✅ Nenhum 404 encontrado!');
  }
  
  await browser.close();
}

checkConsoleErrors().catch(console.error);
