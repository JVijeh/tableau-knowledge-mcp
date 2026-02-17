# Virtual Environment Quick Reference

## Why Do We Need Virtual Environments?

Think of a virtual environment like a **separate workspace** for each Python project:

- **Isolation:** Each project gets its own copies of packages
- **No conflicts:** Project A can use pandas v1.5, Project B can use pandas v2.0
- **Reproducible:** Others can recreate your exact setup
- **Clean:** Doesn't mess with your system Python

**Analogy:** Like having separate toolboxes for different jobs - your carpentry tools don't mix with your electronics tools.

---

## Visual Guide: Are You in a Virtual Environment?

### ✅ **Virtual Environment ACTIVATED**
```
(venv) C:\Users\jvije\tableau-knowledge-mcp_prod\support_files>
  ↑
  This (venv) prefix means you're IN the virtual environment
```

### ❌ **Virtual Environment NOT ACTIVATED**
```
C:\Users\jvije\tableau-knowledge-mcp_prod\support_files>
↑
No prefix = NOT in virtual environment
```

**Rule:** If you don't see `(venv)` at the start of your prompt, you need to activate!

---

## The Three Essential Commands (Windows)

### 1. **First Time Setup** (Only Once)
```batch
py -m venv venv
```
**What it does:** Creates the `venv` folder with Python environment  
**When:** First time setting up the project, or if you deleted `venv` folder  
**Takes:** 30-60 seconds

### 2. **Activate** (Every Session)
```batch
.\venv\Scripts\activate.bat
```
**What it does:** "Turns on" the virtual environment  
**When:** Every time you open a new PowerShell/CMD window  
**You'll see:** `(venv)` prefix appears in your prompt

### 3. **Install Packages** (After Activation)
```batch
pip install -r requirements.txt
```
**What it does:** Installs all project dependencies  
**When:** First setup, or when requirements.txt changes  
**Takes:** 2-5 minutes

---

## Quick Start Scripts (Even Easier!)

### **First Time Setup:**
Just run:
```batch
setup.bat
```
Does all three steps automatically!

### **Daily Use:**
Just run:
```batch
activate.bat
```
Activates environment and keeps window open!

---

## Common Scenarios

### **Scenario 1: Starting Fresh (First Time)**
```batch
# Navigate to project
cd C:\Users\jvije\tableau-knowledge-mcp_prod\support_files

# Run setup script (does everything)
setup.bat
```

### **Scenario 2: Coming Back to Project (Daily)**
```batch
# Navigate to project
cd C:\Users\jvije\tableau-knowledge-mcp_prod\support_files

# Activate environment
activate.bat

# Now you can work
python scripts\index_books.py --pdf-dir "path"
```

### **Scenario 3: Forgot to Activate**
**Symptom:** Error like "No module named 'chromadb'"

**Fix:**
```batch
# Activate the environment
.\venv\Scripts\activate.bat

# Now try again
python scripts\index_books.py --pdf-dir "path"
```

### **Scenario 4: Virtual Environment Broken**
**Symptom:** Can't activate, or weird errors

**Fix:**
```batch
# Delete the venv folder
rmdir /s venv

# Run setup again
setup.bat
```

---

## Memory Tricks

### **Remember: Open New Window = Need to Activate**

Every time you:
- Close and reopen PowerShell/CMD
- Open a new terminal tab
- Restart your computer
- Open VS Code terminal

You need to activate again!

### **Visual Check: Look for (venv)**

Before running ANY Python command:
1. Look at your prompt
2. Do you see `(venv)`?
   - **YES** → You're good, proceed
   - **NO** → Run `activate.bat` first

### **The Setup vs Activate Rule**

```
setup.bat    → Run ONCE (first time or after deleting venv)
activate.bat → Run EVERY TIME (each new session)
```

---

## Troubleshooting

### "Python not found"
**Use `py` instead of `python`:**
```batch
py -m venv venv
```

### "Cannot activate"
**Try the .bat file:**
```batch
.\venv\Scripts\activate.bat
```

### "Module not found" errors
**You forgot to activate!**
```batch
.\venv\Scripts\activate.bat
# Then try again
```

### "Permission denied"
**Run as Administrator OR use .bat file**

---

## File Organization Reference

```
tableau-knowledge-mcp/
├── venv/                    ← Virtual environment (created by setup)
│   ├── Scripts/
│   │   ├── activate.bat    ← Activation script
│   │   └── python.exe      ← Project's Python
│   └── Lib/                ← Installed packages go here
├── setup.bat               ← First-time setup script
├── activate.bat            ← Daily activation script
├── requirements.txt        ← Package list
└── ...
```

---

## When Do I Need Virtual Environment?

### **Need Virtual Environment:**
✅ Running Python scripts from this project  
✅ Installing packages with pip  
✅ Running tests  
✅ Indexing PDFs  
✅ Testing the MCP server  

### **Don't Need Virtual Environment:**
❌ Using Git commands (git add, git commit, etc.)  
❌ Editing files in text editor  
❌ Browsing files with `dir` or `ls`  
❌ Configuring Claude Desktop (it uses venv path)  

---

## Quick Reference Card

**Print or bookmark this:**

```
┌─────────────────────────────────────────────────┐
│  Virtual Environment Quick Commands             │
├─────────────────────────────────────────────────┤
│                                                 │
│  FIRST TIME:                                    │
│    setup.bat                                    │
│                                                 │
│  EVERY SESSION:                                 │
│    activate.bat                                 │
│    OR: .\venv\Scripts\activate.bat              │
│                                                 │
│  CHECK IF ACTIVATED:                            │
│    Look for (venv) in prompt                    │
│                                                 │
│  DEACTIVATE:                                    │
│    deactivate                                   │
│                                                 │
│  START OVER:                                    │
│    rmdir /s venv                                │
│    setup.bat                                    │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Advanced: Why These Specific Commands?

### **Why `py` instead of `python`?**
Windows 10+ has a Python launcher (`py`) that's more reliable than the `python` command, which can be hijacked by Windows Store.

### **Why `venv\Scripts\activate.bat` and not `activate`?**
Windows requires the full path and `.bat` extension to find the script.

### **Why create `venv` folder in project directory?**
Keeps environment isolated and makes it easy to delete/recreate without affecting other projects.

---

## Pro Tips

1. **Pin setup.bat to taskbar** for quick access
2. **Create desktop shortcut** to activate.bat
3. **Use VS Code?** It can auto-activate venv when you open the folder
4. **Name your PowerShell windows** so you remember which is activated

---

## Still Confused?

**Simple rule:** 
- See `(venv)` in prompt = ✅ Good to go
- Don't see `(venv)` = ❌ Run `activate.bat`

**When in doubt:**
```batch
activate.bat
```

---

**Need help?** See TROUBLESHOOTING.md or open a GitHub issue.
