import glob
import re

files_to_fix = glob.glob("app/templates/*.html")

replacements = {
    # Fix light text colors on light backgrounds
    r'text-brand-400': 'text-brand-600',
    r'text-purple-400': 'text-purple-600',
    r'text-emerald-400': 'text-emerald-600',
    r'text-amber-400': 'text-amber-600',
    r'text-cyan-400': 'text-cyan-600',
    r'text-red-400': 'text-red-600',
    
    # Fix backgrounds for icons and active states to be slightly darker or softer if needed
    r'bg-brand-500/10': 'bg-brand-100',
    r'bg-purple-500/10': 'bg-purple-100',
    r'bg-emerald-500/10': 'bg-emerald-100',
    r'bg-amber-500/10': 'bg-amber-100',
    r'bg-cyan-500/10': 'bg-cyan-100',
    r'bg-red-500/10': 'bg-red-100',
    
    # Fix specific sidebar badge that wraps
    r'<span class="text-slate-900 font-bold text-lg tracking-wide">MockExam <span class="text-brand-500">Pro</span></span>': r'<span class="text-slate-900 font-bold text-base tracking-tight whitespace-nowrap">MockExam <span class="text-brand-600">Pro</span></span>',
    r'text-\[10px\] font-bold px-2 py-0\.5': r'text-[9px] font-bold px-1.5 py-0.5 ml-1 whitespace-nowrap',
}

for filepath in files_to_fix:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    for old, new in replacements.items():
        content = re.sub(old, new, content)
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Fixed colors in {filepath}")
