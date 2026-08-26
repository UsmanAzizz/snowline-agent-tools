import os
import glob
import re

def test_skills_folder_rules():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_dir = os.path.join(repo_root, 'src', 'snowline', 'templates', 'skills')
    
    # Aturan 1 & 2
    folders = [f for f in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, f))]
    shared_modules = ['tree_gen']
    
    skill_count = 0
    for folder in folders:
        if folder == 'rules' or folder == '__pycache__':
            continue
            
        folder_path = os.path.join(skills_dir, folder)
        has_skill_md = os.path.isfile(os.path.join(folder_path, 'SKILL.md'))
        
        if not has_skill_md:
            if folder not in shared_modules:
                raise AssertionError(f"Folder '{folder}' does not have SKILL.md and is not a shared module.")
        else:
            skill_count += 1
            # Aturan 2: tiap folder yang punya SKILL.md punya minimal satu .py
            py_files = glob.glob(os.path.join(folder_path, '*.py')) + glob.glob(os.path.join(folder_path, '**', '*.py'), recursive=True)
            if not py_files:
                raise AssertionError(f"Folder '{folder}' has SKILL.md but no .py file.")
                
    # Aturan 3: jumlah alat di README dan STATE.md sama dengan hitungan sebenarnya
    with open(os.path.join(repo_root, 'README.md'), 'r', encoding='utf-8') as f:
        readme = f.read()
    
    readme_match = re.search(r'## Tools \((\d+)\)', readme)
    if not readme_match:
        raise AssertionError("Could not find tool count in README.md")
    if int(readme_match.group(1)) != skill_count:
        raise AssertionError(f"README.md count ({readme_match.group(1)}) does not match actual count ({skill_count})")
        
    with open(os.path.join(repo_root, '.here_we_are', 'STATE.md'), 'r', encoding='utf-8') as f:
        state = f.read()
        
    state_match = re.search(r'tools\s+beruji\s+\d+ / (\d+)', state)
    if not state_match:
        raise AssertionError("Could not find tool count in STATE.md")
    if int(state_match.group(1)) != skill_count:
        raise AssertionError(f"STATE.md count ({state_match.group(1)}) does not match actual count ({skill_count})")
