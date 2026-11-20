/**
 * test_syntax.js — Validates that all inline scripts in templates/index.html
 * parse with zero JavaScript syntax errors using Node's V8 engine.
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const htmlPath = path.join(__dirname, 'templates', 'index.html');
const htmlContent = fs.readFileSync(htmlPath, 'utf8');

const scriptRegex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match;
let scriptIndex = 0;
let errors = 0;

console.log('='.repeat(55));
console.log('  RakshaAI — JavaScript Syntax Validation');
console.log('='.repeat(55));

while ((match = scriptRegex.exec(htmlContent)) !== null) {
  scriptIndex++;
  const code = match[1].trim();
  if (!code) continue; // External script tag (e.g. Leaflet)

  try {
    new vm.Script(code, { filename: `inline-script-${scriptIndex}.js` });
    console.log(`✅ Script #${scriptIndex} (${code.length} bytes): Syntax is 100% clean.`);
  } catch (err) {
    console.error(`❌ Script #${scriptIndex} Syntax Error:`, err.message);
    errors++;
  }
}

if (errors === 0) {
  console.log('\n✅ All frontend JavaScript scripts passed syntax validation without errors!');
  process.exit(0);
} else {
  console.error(`\n❌ Found ${errors} syntax error(s).`);
  process.exit(1);
}

