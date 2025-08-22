import fs from 'fs';
import path from 'path';

function fixImports(dir) {
  const files = fs.readdirSync(dir);
  
  for (const file of files) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      fixImports(filePath);
    } else if (file.endsWith('.js')) {
      let content = fs.readFileSync(filePath, 'utf8');
      
      // Fix relative imports to include .js extension
      content = content.replace(/from ['"](\.[^'"]*)['"]/g, (match, importPath) => {
        if (!importPath.endsWith('.js') && !importPath.includes('*')) {
          return `from '${importPath}.js'`;
        }
        return match;
      });
      
      fs.writeFileSync(filePath, content);
      console.log(`Fixed imports in: ${filePath}`);
    }
  }
}

console.log('Fixing imports in compiled files...');
fixImports('kashif-standalone/dist/server');
console.log('Import fixes completed!'); 