const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('Running pre-build tasks...');

// Ensure build directories exist
const dirs = ['build', 'dist'];
dirs.forEach(dir => {
    const dirPath = path.join(process.cwd(), dir);
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
});

// Build server
console.log('Building server...');
try {
    process.chdir(path.join(process.cwd(), 'server'));
    execSync('npm run build', { stdio: 'inherit' });
    process.chdir(process.cwd());
} catch (error) {
    console.error('Failed to build server:', error);
    process.exit(1);
}

// Build client
console.log('Building client...');
try {
    execSync('npm run build', { stdio: 'inherit' });
} catch (error) {
    console.error('Failed to build client:', error);
    process.exit(1);
}

// Copy necessary files
console.log('Copying resources...');
try {
    // Copy icon
    fs.copyFileSync(
        path.join(process.cwd(), 'assets', 'icon.ico'),
        path.join(process.cwd(), 'build', 'icon.ico')
    );

    // Copy config files
    const configDir = path.join(process.cwd(), 'config');
    const buildConfigDir = path.join(process.cwd(), 'build', 'config');
    if (!fs.existsSync(buildConfigDir)) {
        fs.mkdirSync(buildConfigDir, { recursive: true });
    }
    fs.readdirSync(configDir).forEach(file => {
        fs.copyFileSync(
            path.join(configDir, file),
            path.join(buildConfigDir, file)
        );
    });
} catch (error) {
    console.error('Failed to copy resources:', error);
    process.exit(1);
}

console.log('Pre-build tasks completed successfully.');