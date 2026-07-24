#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('Installing 12-Pillars Agent Ecosystem (Project-Level)...');

const projectRoot = process.cwd();
const agentsDir = path.join(projectRoot, '.agents');
const skillsDir = path.join(agentsDir, 'skills');
const knowledgeDir = path.join(agentsDir, 'knowledge');
const repoUrl = 'https://github.com/UsmanAzizz/snowline-agent-tools.git';
let isNewInstall = false;

// Ensure .agents and .agents/knowledge exist
if (!fs.existsSync(agentsDir)) {
    fs.mkdirSync(agentsDir, { recursive: true });
}
if (!fs.existsSync(knowledgeDir)) {
    fs.mkdirSync(knowledgeDir, { recursive: true });
}

// Scaffold skills
if (fs.existsSync(skillsDir)) {
    console.log(`Found existing skills directory at ${skillsDir}`);
    if (fs.existsSync(path.join(skillsDir, '.git'))) {
        console.log('Pulling latest updates...');
        try {
            execSync('git pull origin main', { cwd: skillsDir, stdio: 'inherit' });
        } catch (e) {
            console.error('Failed to update repository.');
        }
    } else {
        console.log('Existing skills directory is not a git repository. Skipping git pull.');
    }
} else {
    isNewInstall = true;
    console.log(`Downloading 12-Pillars skills...`);
    try {
        execSync(`git clone ${repoUrl} "${skillsDir}"`, { stdio: 'inherit' });
    } catch (e) {
        console.error('Failed to clone repository. Make sure git is installed.');
        process.exit(1);
    }
}

// Copy AGENTS_TEMPLATE.md to AGENTS.md in the project root
const templatePath = path.join(skillsDir, 'AGENTS_TEMPLATE.md');
const localAgentsPath = path.join(agentsDir, 'AGENTS.md');

if (fs.existsSync(templatePath)) {
    if (!fs.existsSync(localAgentsPath)) {
        console.log('Creating Project AGENTS.md...');
        fs.copyFileSync(templatePath, localAgentsPath);
        console.log('Project AGENTS.md created successfully.');
    } else {
        console.log('Project AGENTS.md already exists. Skipping overwrite.');
    }
}

// Scaffold PLAN.md in project root
const planPath = path.join(projectRoot, 'PLAN.md');
if (!fs.existsSync(planPath)) {
    console.log('Creating PLAN.md...');
    fs.writeFileSync(planPath, '# Project Plan / Task Tracker\n\n- [ ] Initial task\n', 'utf8');
}

if (isNewInstall) {
    console.log('\nInstallation Complete!');
    console.log('This project is now powered by the 12-Pillars Ecosystem.');
}
