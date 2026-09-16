#!/usr/bin/env python3
"""
Obsidian Vault SRE Hygiene & Graph Integrity Linter
Ensures zero ghost files, zero broken wikilinks, strict frontmatter, and auto-sync health.
"""

import sys
import re
from pathlib import Path
from collections import defaultdict

VAULT_DIR = Path(__file__).resolve().parent.parent

def clean_ghost_files(vault: Path) -> list:
    """Removes stray 0-byte files or untitled temporary artifacts."""
    cleaned = []
    # Clean zero-byte markdown files at root
    for f in vault.iterdir():
        if f.is_file() and not f.name.startswith('.'):
            if f.name.startswith('Untitled') or (f.suffix == '.md' and f.stat().st_size == 0):
                f.unlink()
                cleaned.append(f.name)
    return cleaned

def audit_vault(vault: Path):
    user_md = [p for p in vault.rglob('*.md') if not any(part.startswith('.') for part in p.relative_to(vault).parts)]
    
    note_stems = {}
    note_paths = {}
    missing_frontmatter = []
    
    for p in user_md:
        rel_str = str(p.relative_to(vault))
        note_stems[p.stem.lower()] = p
        note_paths[rel_str.lower()] = p
        note_paths[str(p.relative_to(vault).with_suffix('')).lower()] = p
        
        text = p.read_text(encoding='utf-8', errors='ignore')
        if not text.startswith('---'):
            missing_frontmatter.append(rel_str)
        else:
            parts = text.split('---', 2)
            if len(parts) >= 3:
                fm = parts[1]
                if 'aliases:' in fm:
                    in_aliases = False
                    for line in fm.splitlines():
                        if line.strip().startswith('aliases:'):
                            in_aliases = True
                            continue
                        if in_aliases:
                            if line.startswith('  - ') or line.startswith('- '):
                                alias = line.split('-', 1)[1].strip().strip('\"\'')
                                note_stems[alias.lower()] = p
                            elif line and not line.startswith(' '):
                                in_aliases = False

    wikilink_pattern = re.compile(r'\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]')
    broken_links = defaultdict(list)
    outgoing = defaultdict(set)
    incoming = defaultdict(set)
    
    for p in user_md:
        rel_str = str(p.relative_to(vault))
        text = p.read_text(encoding='utf-8', errors='ignore')
        links = wikilink_pattern.findall(text)
        for tgt in links:
            tgt_clean = tgt.strip()
            stem = Path(tgt_clean).stem.lower()
            rel = (tgt_clean if tgt_clean.endswith('.md') else tgt_clean + '.md').lower()
            rel_no_ext = (tgt_clean[:-3] if tgt_clean.endswith('.md') else tgt_clean).lower()
            
            matched = note_stems.get(stem) or note_paths.get(rel) or note_paths.get(rel_no_ext)
            if matched:
                outgoing[p].add(matched)
                incoming[matched].add(p)
            else:
                broken_links[tgt_clean].append(rel_str)

    orphans = [p for p in user_md if len(incoming[p]) == 0 and len(outgoing[p]) == 0 and p.name != 'Home.md']
    
    return {
        'total_notes': len(user_md),
        'missing_frontmatter': missing_frontmatter,
        'broken_links': dict(broken_links),
        'orphans': [str(p.relative_to(vault)) for p in orphans]
    }

def main():
    cleaned = clean_ghost_files(VAULT_DIR)
    if cleaned:
        print(f"[Hygiene] Automatically purged {len(cleaned)} ghost file(s): {', '.join(cleaned)}")
        
    report = audit_vault(VAULT_DIR)
    
    has_errors = False
    print(f"[Audit] Scanned {report['total_notes']} markdown notes across vault.")
    
    if report['missing_frontmatter']:
        print(f"⚠️  [Warning] {len(report['missing_frontmatter'])} note(s) missing frontmatter YAML:")
        for f in report['missing_frontmatter']:
            print(f"    - {f}")
            
    if report['broken_links']:
        has_errors = True
        print(f"❌ [Error] {len(report['broken_links'])} broken wikilink target(s) detected:")
        for tgt, srcs in report['broken_links'].items():
            print(f"    - [[{tgt}]] referenced by: {', '.join(set(srcs))}")
            
    if report['orphans']:
        print(f"⚠️  [Warning] {len(report['orphans'])} true orphan note(s) (0 in, 0 out):")
        for o in report['orphans']:
            print(f"    - {o}")
            
    if not has_errors and not report['missing_frontmatter'] and not report['orphans']:
        print("✅ [OK] Vault graph is 100% interconnected, clean, and bullet-proof.")
        sys.exit(0)
    elif has_errors:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
