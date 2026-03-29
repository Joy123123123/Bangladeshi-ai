# 🤝 Contributing to Bangladeshi-ai

Thank you for your interest in contributing to **Bangladeshi-ai**! 🇧🇩
Every contribution — big or small — helps us build a better platform for Bengali students worldwide.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Ways to Contribute](#ways-to-contribute)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Submitting a Pull Request](#submitting-a-pull-request)
6. [Community Roles](#community-roles)

---

## Code of Conduct

We are committed to creating a welcoming and inclusive community.

- **Be respectful** — treat everyone with kindness and patience
- **Be constructive** — give helpful feedback, not harsh criticism
- **Be inclusive** — we welcome contributors of all backgrounds and skill levels
- **Be honest** — be transparent about your intentions and capabilities

Violations of these principles may result in removal from the project.

---

## Ways to Contribute

| Type | Examples |
|------|---------|
| 🐛 **Bug Reports** | Find and document issues |
| 💡 **Feature Requests** | Suggest new features via GitHub Issues |
| 🛠️ **Code** | Fix bugs, build features, improve performance |
| 📝 **Documentation** | Improve guides, fix typos, add examples |
| 🌐 **Bengali NLP** | Improve Bengali language understanding |
| 🎨 **Design** | UI/UX improvements, logos, graphics |
| 🧪 **Testing** | Write or improve tests |
| 🌍 **Translation** | Translate content to Bengali or other languages |

---

## Development Workflow

### 1. Fork & Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/Bangladeshi-ai.git
cd Bangladeshi-ai
```

### 2. Set Up the Development Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
```

### 3. Create a Feature Branch

Always create a new branch for your work:

```bash
git checkout -b feature/my-new-feature
# or
git checkout -b fix/bug-description
# or
git checkout -b docs/update-setup-guide
```

### 4. Make Your Changes

- Write clean, readable code
- Add comments for complex logic
- Update documentation if needed
- Add or update tests if applicable

### 5. Test Your Changes

```bash
# Run the test suite
pytest backend/

# Start the dev server and manually test
uvicorn app.main:app --reload
```

### 6. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git commit -m "feat: add Bengali spell checker to grammar route"
git commit -m "fix: handle empty response from Grok API"
git commit -m "docs: update setup guide with Railway deployment"
```

Commit message prefixes:
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation change
- `style:` — code style/formatting
- `refactor:` — code restructuring
- `test:` — adding/updating tests
- `chore:` — maintenance tasks

### 7. Push and Open a Pull Request

```bash
git push origin feature/my-new-feature
```

Then open a Pull Request on GitHub with:
- Clear title describing what you changed
- Description of *why* you made this change
- Screenshots if you changed the UI
- References to related issues (`Closes #123`)

---

## Coding Standards

### Python (Backend)

- Follow **PEP 8** style guidelines
- Use **type hints** on all function signatures
- Use **docstrings** for modules, classes, and public functions
- Max line length: 100 characters
- Use `async/await` for all I/O operations

### General

- No secrets or API keys in code — use environment variables
- Write self-explanatory variable and function names
- Keep functions small and focused
- Handle errors gracefully and return helpful error messages

---

## Submitting a Pull Request

When you open a PR, our team will:

1. Review your code within 2–3 days
2. Leave comments or suggestions
3. Request changes if needed
4. Approve and merge when ready

**Tips for a smooth review:**
- Keep PRs focused — one feature or fix per PR
- Ensure all tests pass before submitting
- Respond to review comments promptly
- Be patient and open to feedback

---

## Community Roles

| Role | How to Earn | Responsibilities |
|------|------------|-----------------|
| 👑 **Founder** | Project creator | Vision, final decisions |
| ⚔️ **Commander** | Appointed by Founder | Lead specific areas |
| 🥇 **Core Contributor** | 5+ merged PRs | Maintain codebase, review PRs |
| 🥈 **Contributor** | 1+ merged PR | Build features, fix bugs |
| 🌱 **Community Member** | First engagement | File issues, suggest features |

All contributors are celebrated in **[CONTRIBUTORS.md](../CONTRIBUTORS.md)** 🏆

---

## Questions?

- Open a [GitHub Issue](https://github.com/Joy123123123/Bangladeshi-ai/issues)
- Start a [GitHub Discussion](https://github.com/Joy123123123/Bangladeshi-ai/discussions)

**Thank you for helping make AI accessible to Bengali students! 🇧🇩**
