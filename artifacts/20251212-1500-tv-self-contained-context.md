# TV Repository Self-Contained Context Update

> Reference: @claude.md for project context and development guidelines

## Summary

Made the tanque-verde-swim repository fully self-contained so that:
1. A new chat with only `@claude.md` has complete context
2. On a new computer with the repo checked out, you can rebuild everything
3. No implicit dependency on swim-data-tool for website generation

## Files Created/Updated

### Created: `requirements.txt`
Python dependencies for harvesting and analysis scripts:
- pandas
- beautifulsoup4
- requests
- pdfplumber
- playwright

**Note:** Core generation (`generate_website.py`) only needs stdlib.

### Replaced: `claude.md`
Comprehensive documentation including:
- Quick start commands
- Python environment setup
- Directory structure
- Script categories (Core, Enrichment, Analysis, Harvesting, Archive)
- Data file formats with examples
- Common workflows
- Styling reference
- Relationship to swim-data-tool
- Troubleshooting guide

### Updated: `WORKFLOW.md`
Simplified to quick-reference commands, points to `claude.md` for details.

## Key Decisions

### Relationship to swim-data-tool
- **Website generation:** No dependency on swim-data-tool
- **Data harvesting:** Optional - can use SDT or standalone harvest scripts
- **Documentation:** Clear separation of what needs SDT vs what doesn't

### Script Categories
Organized 67 scripts into 5 categories:
1. 🟢 **Core Generation** (3 scripts) - Always needed
2. 🟡 **Data Enrichment** (2 scripts) - As needed
3. 🔵 **Analysis Tools** (4+ scripts) - For insights
4. 🟠 **Harvesting** (10+ scripts) - External data import
5. ⚪ **One-Time/Archive** (50+ scripts) - Already run, keep for reference

## Next Steps

Consider:
1. Archiving one-time scripts to `archive/` directory
2. Adding `.python-version` file if specific Python version needed
3. Testing on fresh clone to verify self-contained setup works

---

**Date:** December 12, 2025


