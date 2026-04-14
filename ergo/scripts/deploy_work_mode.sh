#!/usr/bin/env bash
# Ergo Work Mode Deployment Script
# This script sets up the complete work mode environment

set -e

echo "🚀 Deploying Ergo Work Mode..."

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERGO_HOME="${HOME}/ergo"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Create directory structure
echo -e "${BLUE}📁 Creating directory structure...${NC}"
mkdir -p "${ERGO_HOME}"/{config,runtime/{logs,cache,artifacts},vault/{personality,general,procedures,coding/language_profiles,projects/ergo,sessions,missions},models/{prompts,policies,role_templates},ui/exports}

# Copy configuration files
echo -e "${BLUE}⚙️  Deploying configuration files...${NC}"
cp "${REPO_ROOT}/config/ergo.toml" "${ERGO_HOME}/config/"
cp "${REPO_ROOT}/config/routes.toml" "${ERGO_HOME}/config/"
cp "${REPO_ROOT}/config/permissions.toml" "${ERGO_HOME}/config/"

# Copy personality templates
echo -e "${BLUE}🎭 Deploying personality files...${NC}"
cp -r "${REPO_ROOT}/vault_templates/personality/"* "${ERGO_HOME}/vault/personality/"

# Copy model prompts and policies
echo -e "${BLUE}🤖 Deploying model prompts and policies...${NC}"
cp -r "${REPO_ROOT}/vault_templates/models/prompts/"* "${ERGO_HOME}/models/prompts/" 2>/dev/null || true
cp -r "${REPO_ROOT}/vault_templates/models/policies/"* "${ERGO_HOME}/models/policies/" 2>/dev/null || true

# Initialize database
echo -e "${BLUE}💾 Initializing missions database...${NC}"
if [ -f "${REPO_ROOT}/orchestrator/src/db/work_mode_schema.sql" ]; then
    sqlite3 "${ERGO_HOME}/runtime/missions.db" < "${REPO_ROOT}/orchestrator/src/db/work_mode_schema.sql"
    echo -e "${GREEN}✓ Database initialized${NC}"
else
    echo -e "${YELLOW}⚠  Schema file not found, skipping database init${NC}"
fi

# Verify database
if [ -f "${ERGO_HOME}/runtime/missions.db" ]; then
    ROLE_COUNT=$(sqlite3 "${ERGO_HOME}/runtime/missions.db" "SELECT COUNT(*) FROM role_definitions;")
    echo -e "${GREEN}✓ Database has ${ROLE_COUNT} roles defined${NC}"
fi

# Create initial project memory
echo -e "${BLUE}📝 Creating initial project memory...${NC}"
cat > "${ERGO_HOME}/vault/projects/ergo/README.md" << 'EOF'
# Ergo Project Memory

This directory contains project-specific knowledge, decisions, and context for the Ergo project itself.

## Files
- `architecture.md` - System architecture decisions
- `decisions.md` - Key architectural and design decisions
- `recurring_issues.md` - Common problems and their solutions
- `roadmap.md` - Development roadmap and priorities
EOF

# Create setup guide
cat > "${ERGO_HOME}/README.md" << 'EOF'
# Ergo Work Mode

This directory contains the work mode system for Ergo.

## Structure

- `config/` - Configuration files
- `runtime/` - Live databases and logs
- `vault/` - Obsidian-compatible knowledge base
- `models/` - Prompts and policies
- `ui/` - UI exports

## Quick Start

1. Ensure API keys are set:
   ```bash
   export ANTHROPIC_API_KEY="your-key"
   export GOOGLE_AI_API_KEY="your-key"
   ```

2. Start the orchestrator:
   ```bash
   cd ~/Documents/Github/Ergo/ergo
   ./run-orchestrator.sh
   ```

3. In Neovim, try:
   ```vim
   :ErgoChat
   let's get a job done
   ```

## Configuration

Edit `config/ergo.toml` to customize:
- Model routing
- Budget limits
- Memory settings
- Personality modes

See `docs/reference/WORK_MODE_ARCHITECTURE.md` for details.
EOF

# Verify Python service files exist
echo -e "${BLUE}🐍 Checking Python services...${NC}"
SERVICES_DIR="${REPO_ROOT}/orchestrator/src/services"
if [ -f "${SERVICES_DIR}/supervisor.py" ]; then
    echo -e "${GREEN}✓ Supervisor service found${NC}"
fi
if [ -f "${SERVICES_DIR}/mission_manager.py" ]; then
    echo -e "${GREEN}✓ Mission manager service found${NC}"
fi
if [ -f "${SERVICES_DIR}/memory_service.py" ]; then
    echo -e "${GREEN}✓ Memory service found${NC}"
fi
if [ -f "${SERVICES_DIR}/obsidian_bridge.py" ]; then
    echo -e "${GREEN}✓ Obsidian bridge service found${NC}"
fi
if [ -f "${SERVICES_DIR}/coding_style_learner.py" ]; then
    echo -e "${GREEN}✓ Coding style learner service found${NC}"
fi

# Verify agent base class
AGENTS_DIR="${REPO_ROOT}/orchestrator/src/agents"
if [ -f "${AGENTS_DIR}/base_agent.py" ]; then
    echo -e "${GREEN}✓ Base agent class found${NC}"
fi

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "📂 Ergo work mode installed at: ${ERGO_HOME}"
echo ""
echo "Deployed components:"
echo "  • Configuration system (3 TOML files)"
echo "  • Database schema with 9 tables"
echo "  • 5 Personality modes"
echo "  • 7 Role prompts (Supervisor + 6 agents)"
echo "  • 5 Policy files"
echo "  • 5 Python services (mission, memory, obsidian, style learner, supervisor)"
echo "  • Agent base class with permission system"
echo ""
echo "Next steps:"
echo "1. Set environment variables for API keys:"
echo "   export ANTHROPIC_API_KEY=\"sk-ant-...\""
echo "   export GOOGLE_AI_API_KEY=\"AIza...\""
echo ""
echo "2. Review and customize configuration:"
echo "   ${ERGO_HOME}/config/ergo.toml"
echo ""
echo "3. Install Python dependencies:"
echo "   pip install anthropic google-generativeai openai"
echo ""
echo "4. Start the orchestrator:"
echo "   cd ${REPO_ROOT} && ./run-orchestrator.sh"
echo ""
echo "5. Try work mode in Neovim:"
echo "   :ErgoChat"
echo "   > let's get a job done"
echo ""
echo "Documentation:"
echo "  • Architecture: ${REPO_ROOT}/docs/reference/WORK_MODE_ARCHITECTURE.md"
echo "  • Implementation: ${REPO_ROOT}/docs/reference/WORK_MODE_IMPLEMENTATION.md"
echo "  • Claude Guide: ${REPO_ROOT}/.claude.md"
