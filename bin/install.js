#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const os = require('os');

console.log('🚀 Installing 12-Pillars Agent Ecosystem...');

const homeDir = os.homedir();
const configDir = path.join(homeDir, '.gemini', 'config');
const skillsDir = path.join(configDir, 'skills');
const repoUrl = 'https://github.com/UsmanAzizz/snowline-agent-tools.git';

// Ensure config dir exists
if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
}

// Check if skills dir exists
if (fs.existsSync(skillsDir)) {
    console.log(`📁 Found existing skills directory at ${skillsDir}`);
    // Check if it's a git repo
    if (fs.existsSync(path.join(skillsDir, '.git'))) {
        console.log('🔄 Pulling latest updates...');
        try {
            execSync('git pull origin main', { cwd: skillsDir, stdio: 'inherit' });
        } catch (e) {
            console.error('❌ Failed to update repository.');
        }
    } else {
        console.log('⚠️ Existing skills directory is not a git repository. Skipping git pull.');
    }
} else {
    console.log(`📥 Cloning 12-Pillars repository to ${skillsDir}...`);
    try {
        execSync(`git clone ${repoUrl} "${skillsDir}"`, { stdio: 'inherit' });
    } catch (e) {
        console.error('❌ Failed to clone repository.');
        process.exit(1);
    }
}

// Copy AGENTS_TEMPLATE.md to AGENTS.md globally if AGENTS.md doesn't exist
const templatePath = path.join(skillsDir, 'AGENTS_TEMPLATE.md');
const globalAgentsPath = path.join(configDir, 'AGENTS.md');

if (fs.existsSync(templatePath)) {
    if (!fs.existsSync(globalAgentsPath)) {
        console.log('📝 Creating Global AGENTS.md from template...');
        fs.copyFileSync(templatePath, globalAgentsPath);
        console.log('✅ Global AGENTS.md created successfully.');
    } else {
        console.log('⚠️ Global AGENTS.md already exists. Skipping overwrite to preserve your personal rules.');
    }
}

console.log('\n🎉 Installation Complete!');
console.log('Your IDE is now powered by the 12-Pillars Ecosystem.');
console.log('Open any new project, and the agent will automatically scaffold the architecture for you!');
