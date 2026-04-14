# Project Epic - Setup Guide

## Quick Setup (3 steps)

### 1. Install Dependencies

```bash
cd ~/Documents/Github/Ergo/Project_Epic
pip install -r requirements.txt
```

### 2. Configure API Keys

**Option A: Create .env file (Recommended)**

```bash
# Copy example file
cp .env.example .env

# Edit with your keys
nano .env  # or vim, code, etc.
```

Add your keys:
```env
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
GOOGLE_AI_API_KEY=your-google-key-here  # Optional
```

**Option B: Export environment variables**

```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
export GOOGLE_AI_API_KEY="your-google-key-here"  # Optional
```

### 3. Run Tests

```bash
# Command-line tests (no AI calls needed)
python test_standalone.py

# Web interface
python -m epic.api.server
# Open: http://localhost:8766
```

---

## Using .env File (Recommended)

### Why .env?
- ✅ Keys stored in one place
- ✅ Not in shell history
- ✅ Easy to manage multiple environments
- ✅ Works across all scripts

### Setup .env:

1. **Copy example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env:**
   ```bash
   nano .env
   ```

3. **Add your keys:**
   ```env
   # Required for Claude agents
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

   # Optional for Gemini agents
   GOOGLE_AI_API_KEY=AIzaxxxxx

   # Optional for OpenAI
   OPENAI_API_KEY=sk-xxxxx
   ```

4. **Save and test:**
   ```bash
   python test_standalone.py
   ```

### .env is loaded automatically:
- ✅ By `epic/config.py`
- ✅ By server startup
- ✅ By tests

---

## Without API Keys (Testing Only)

You can test the system structure without API keys:

```bash
python test_standalone.py
```

This runs in **simulation mode** - no actual AI calls, just tests the flow.

⚠️ **For real AI execution, you need keys!**

---

## Getting API Keys

### Anthropic (Required)
1. Go to: https://console.anthropic.com/
2. Sign up / Log in
3. Go to: API Keys section
4. Create new key
5. Copy key (starts with `sk-ant-`)

### Google AI (Optional)
1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Create API key
4. Copy key (starts with `AIza`)

---

## Troubleshooting

### "ANTHROPIC_API_KEY not set"

**Solution:**
```bash
# Check if .env exists
ls -la .env

# If not, create it
cp .env.example .env

# Edit and add your key
nano .env
```

### ".env not loading"

**Solution:**
```bash
# Make sure you're in Project_Epic directory
pwd
# Should show: .../Project_Epic

# Check .env is in current directory
ls .env

# Test loading
python -c "from epic.config import ANTHROPIC_API_KEY; print('Key loaded!' if ANTHROPIC_API_KEY else 'Not loaded')"
```

### "quickstart.sh: read: no coprocess"

**Solution:**
```bash
# Make executable
chmod +x quickstart.sh

# Run directly
./quickstart.sh

# Or use bash explicitly
bash quickstart.sh
```

### "Module not found: dotenv"

**Solution:**
```bash
# Install python-dotenv
pip install python-dotenv

# Or reinstall all deps
pip install -r requirements.txt
```

---

## Verification

Test that everything is configured:

```bash
# 1. Check dependencies
pip list | grep -E "(anthropic|dotenv|fastapi)"

# 2. Check .env loading
python -c "from epic.config import check_api_keys; warnings = check_api_keys(); print('✓ Ready!' if not warnings else '\n'.join(warnings))"

# 3. Run quick test
python test_standalone.py

# 4. Start server
python -m epic.api.server
```

If all work without errors, you're ready! 🎉

---

## Next Steps

1. ✅ **Setup complete** (you're here)
2. ➡️  **Test the system** (run test_standalone.py)
3. ➡️  **Try web interface** (http://localhost:8766)
4. ➡️  **Create your first quest**
5. ➡️  **Integrate with Ergo** (see INTEGRATION.md)

---

## Advanced Configuration

### Custom Server Port

In `.env`:
```env
EPIC_HOST=127.0.0.1
EPIC_PORT=9000  # Change from default 8766
```

### Multiple Environments

```bash
# Development
cp .env.example .env.dev
# Add dev keys

# Production
cp .env.example .env.prod
# Add prod keys

# Load specific env
export DOTENV_PATH=.env.dev
python -m epic.api.server
```

---

**Questions?** Check TESTING_GUIDE.md or COMPLETE.md
