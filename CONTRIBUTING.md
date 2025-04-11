---
# 🤝 Contributing to B-Vista

Thank you for considering a contribution to **B-Vista**

We welcome contributions of all kinds: ✨ new features, 🐛 bug fixes, 📝 documentation, 🧪 tests, 🧠 ideas — and even 💬 feedback!

---

## 📌 Before You Start

- 🔍 **Explore the codebase**: Check [README.md](./README.md) for features and dev setup.
- 📚 **Read the docs**: Full architecture is in [DOCUMENTATION.md](./DOCUMENTATION.md).
- 🧭 **Follow the Code of Conduct**: Be kind, inclusive, and respectful ([CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)).

---

## 🛠️ Setup Guide

### Clone the project

```bash
git clone https://github.com/Baci-Ak/b-vista.git
cd b-vista
```

### Python Backend (API Server)

```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows

pip install -r requirements.txt
pip install -e ".[dev]"
python bvista/backend/app.py
```

### Frontend (React UI)

```bash
cd bvista/frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) to view the frontend (optional).

---

## 🧪 Running Tests

From the root of the project:

```bash
pytest
```

To test in watch mode (when editing):

```bash
pip install pytest-watch
ptw
```

---

## 📋 Style Guide

We use:

- **Black** for Python formatting
- **Prettier** for JS/React formatting
- **isort** for imports
- **flake8** for linting

You can format all Python code automatically with:

```bash
black .
isort .
```

---

## 🧩 Ways to Contribute

You don’t have to write code to contribute! Here’s how you can help:

| Type                        | Examples |
|-----------------------------|----------|
| 🐛 Bug Reports              | File issues with steps to reproduce |
| 💡 Feature Suggestions      | Ideas that improve B-Vista or fill a gap |
| ✍️ Docs Improvements         | Fix typos, explain a feature better |
| 🧪 Add Tests                | Coverage for untested logic |
| 🎨 UI/UX Enhancements        | Improve layout, styling, usability |
| 🔍 Triaging                 | Review open issues and verify bugs |
| 📦 Package Improvements     | Help with conda, pip, or Docker builds |

---

## ✅ Pull Request Checklist

Before submitting a PR:

- [ ] The code works locally (`pytest` passes)
- [ ] The feature has a clear purpose and benefit
- [ ] Added docs or usage examples if needed
- [ ] Linting and formatting are clean
- [ ] Commits are descriptive (use present tense)

Once ready:

```bash
git checkout -b feat/your-feature-name
# make changes
git add .
git commit -m "✨ Add feature: short description"
git push origin feat/your-feature-name
```

Then open a **Pull Request** on GitHub.

---

## 📣 First-Time Contributors Welcome!

Never contributed before? You’re in the right place.

- Look for [good first issue](https://github.com/Baci-Ak/b-vista/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
- Ask questions in [Discussions](https://github.com/Baci-Ak/b-vista/discussions)
- Don’t worry about perfection — we’re here to help you!

---

## 💬 Community

Feel free to engage:

- GitHub Discussions (for ideas or help)
- GitHub Issues (for bugs or feature requests)
- Twitter/X: `#bvista` or tag us on data science platforms

---

## 🔐 Code of Conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/).  
Be respectful. Be inclusive. Help others succeed.

---

Thanks again for making B-Vista better 🙏

— *The B-Vista Maintainers*
```

---
