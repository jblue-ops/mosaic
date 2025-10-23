# Environment Variables Setup

**Status**: ✅ `.env` files created | 🔴 API keys needed

## What's Been Done

All three `.env` files have been created with auto-generated secrets:

```
/Users/jblue/mosaic/.env                    ✅ Created
/Users/jblue/mosaic/honeybee/.env           ✅ Created
/Users/jblue/mosaic/python-ai-service/.env  ✅ Created
```

### Auto-Generated Secrets ✅

These have been set and synchronized across all services:

- **SECRET_KEY_BASE**: `3d0c02407e9c78daf3b52df03b0e424a9d35180e8941fd95fde3436a09beb1a389f578ef21028e7957aa828d59b9476d6d373f327313b996fc1bc3a3b31a5e94`
- **AI_SERVICE_API_KEY**: `e75f31c4cf06ec92190fe9e217df53617593d853ba99575ca5d1f6a8adcfcc94`

These keys are used for Rails ↔ Python authentication and are already configured in all three `.env` files.

## What You Need to Add

### 🔴 REQUIRED: OpenAI API Key

You need to obtain an OpenAI API key to enable the AI agents:

1. **Get your API key**: https://platform.openai.com/api-keys
2. **Add to all three `.env` files**, replacing this line:
   ```bash
   OPENAI_API_KEY=sk-YOUR_OPENAI_API_KEY_HERE
   ```
   With:
   ```bash
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```

**Files to update** (search for `sk-YOUR_OPENAI_API_KEY_HERE`):
- `/Users/jblue/mosaic/.env`
- `/Users/jblue/mosaic/honeybee/.env`
- `/Users/jblue/mosaic/python-ai-service/.env`

### 🟡 OPTIONAL: ATS Integration Keys

When you're ready to integrate with Applicant Tracking Systems, add these:

**Ashby**:
```bash
ASHBY_API_KEY=your-ashby-api-key-here
```

**Greenhouse**:
```bash
GREENHOUSE_API_KEY=your-greenhouse-api-key-here
```

### 🟡 OPTIONAL: Error Tracking

When ready to use Sentry for error tracking:

```bash
SENTRY_DSN=https://your-sentry-dsn-here
```

## Quick Setup Commands

### Update OpenAI Key in All Files

```bash
# Method 1: Using sed (macOS)
cd /Users/jblue/mosaic
sed -i '' 's/sk-YOUR_OPENAI_API_KEY_HERE/sk-proj-YOUR-ACTUAL-KEY/' .env
sed -i '' 's/sk-YOUR_OPENAI_API_KEY_HERE/sk-proj-YOUR-ACTUAL-KEY/' honeybee/.env
sed -i '' 's/sk-YOUR_OPENAI_API_KEY_HERE/sk-proj-YOUR-ACTUAL-KEY/' python-ai-service/.env

# Method 2: Manual edit
nano .env
nano honeybee/.env
nano python-ai-service/.env
```

## Verification

After adding your OpenAI key, verify the setup:

```bash
# Check all .env files exist
ls -la /Users/jblue/mosaic/.env
ls -la /Users/jblue/mosaic/honeybee/.env
ls -la /Users/jblue/mosaic/python-ai-service/.env

# Verify OpenAI key is set (should NOT show "YOUR_OPENAI_API_KEY_HERE")
grep OPENAI_API_KEY /Users/jblue/mosaic/.env
grep OPENAI_API_KEY /Users/jblue/mosaic/honeybee/.env
grep OPENAI_API_KEY /Users/jblue/mosaic/python-ai-service/.env
```

## Security Notes

⚠️ **IMPORTANT**: These `.env` files contain secrets and should NEVER be committed to git.

Verify they're in `.gitignore`:
```bash
grep ".env" /Users/jblue/mosaic/.gitignore
grep ".env" /Users/jblue/mosaic/honeybee/.gitignore
grep ".env" /Users/jblue/mosaic/python-ai-service/.gitignore
```

## Next Steps

Once you've added your OpenAI API key:

1. **Install dependencies**:
   ```bash
   cd honeybee && bundle install
   cd ../python-ai-service && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
   ```

2. **Start services**:
   ```bash
   # Terminal 1: Rails
   cd honeybee && rails server

   # Terminal 2: Python AI Service
   cd python-ai-service && source venv/bin/activate && fastapi dev app/main.py
   ```

3. **Test the connection**:
   ```bash
   # In Rails console
   cd honeybee
   rails console
   > AiService.healthy?  # Should return true
   ```

---

**Last Updated**: October 22, 2025
**Status**: Environment files created, awaiting OpenAI API key
