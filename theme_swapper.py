import glob
import re

replacements = {
    r'bg-slate-950': 'bg-slate-50',
    r'bg-slate-900': 'bg-white',
    r'bg-slate-800': 'bg-slate-50',
    r'border-slate-800': 'border-slate-200',
    r'border-slate-700': 'border-slate-300',
    r'text-slate-200': 'text-slate-900',
    r'text-slate-300': 'text-slate-800',
    r'text-slate-400': 'text-slate-600',
    r'text-slate-500': 'text-slate-500', # leave as is
    r'bg-black/50': 'bg-slate-900/50',
}

# Special case for text-white used in headings but not in buttons
# It's tricky to regex safely. Instead of changing text-white to text-slate-900, 
# I will just manually look for common patterns like class="font-bold text-white" 
# or I can replace 'text-white' -> 'text-slate-900' and then revert it on buttons.

for filepath in glob.glob("app/templates/*.html"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = re.sub(old, new, content)
    
    # We replace text-white with text-slate-900 everywhere EXCEPT where it's part of a button or similar solid background.
    # Actually, a simpler way is to replace `text-white` with `text-slate-900`
    # and then replace `bg-brand-600 hover:bg-brand-500 text-slate-900` back to `text-white`.
    # Let's just do:
    content = re.sub(r'text-white', 'text-slate-900', content)
    
    # Revert for buttons and badges that need white text
    content = re.sub(r'bg-brand-600(.*?)text-slate-900', r'bg-brand-600\1text-white', content)
    content = re.sub(r'bg-gradient-to-tr(.*?)text-slate-900', r'bg-gradient-to-tr\1text-white', content)
    content = re.sub(r'bg-brand-500(.*?)text-slate-900', r'bg-brand-500\1text-white', content)
    content = re.sub(r'btn-close-white', 'btn-close', content) # if any legacy bootstrap
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {filepath}")
