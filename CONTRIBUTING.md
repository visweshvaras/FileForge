# 🤝 Contributing to FileForge (OpenForge)

First of all, **welcome to the team!** 🎉

Whether you are a seasoned developer or writing your very first lines of code, we want your help. At **OpenForge**, our mission is to make open-source accessible, friendly, and rewarding for all students.

> 💡 **No prior open-source experience?**
> Don't worry! We are here to guide you through your very first Git commit and Pull Request. If you get stuck, feel free to open an issue or ask our team.

---

## 🧭 Ways You Can Contribute

You don't just have to write core Python code to contribute! Here are high-impact ways to get involved:

1. **🐍 Add New Converters**: Markdown (`.md` ➔ `.pdf`), code-to-PDF lab sheets, text converters.
2. **🎨 GUI & Frontend**: Help develop a modern `CustomTkinter` or `PyQt` window.
3. **🪟 Windows / Mac Testing**: Run the tool on your laptop and report formatting or layout issues.
4. **🌐 Language Translations**: Add multilingual menu options for regional/international languages.
5. **📝 Documentation**: Fix typos, add examples, record a GIF demo, or write a beginner's guide.
6. **🐛 Bug Hunting**: Try edge-case conversions (huge files, strange fonts, nested tables) and report bugs.

---

## 🛠️ Step-by-Step Contribution Guide

### Step 1: Fork the Repository
Click the **Fork** button at the top right of the [FileForge GitHub page](https://github.com/visweshvaras/FileForge). This creates your own personal copy of the project.

### Step 2: Clone Your Fork
Open your terminal (or Command Prompt on Windows) and clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/FileForge.git
cd FileForge
```

### Step 3: Create a New Branch
Never code directly on `main`. Create a descriptive branch for your feature:
```bash
git switch -c feature/your-feature-name
```
*(For example: `feature/markdown-to-pdf` or `fix/windows-path-bug`)*

### Step 4: Install Dependencies & Test
Set up a virtual environment and install the requirements:
```bash
pip install -r requirements.txt
python main.py
```

Run the automated test suite to ensure everything is working:
```bash
python -m unittest discover tests
```

### Step 5: Make Your Changes & Commit
Once your changes are made and tested, commit them with a friendly message:
```bash
git add .
git commit -m "Add support for markdown to PDF conversion"
```

### Step 6: Push to Your Fork
```bash
git push -u origin feature/your-feature-name
```

### Step 7: Open a Pull Request (PR)
1. Go to the [original FileForge repository](https://github.com/visweshvaras/FileForge).
2. You will see a banner: **"Compare & pull request"**. Click it!
3. Describe what you added or fixed.
4. Click **Create pull request**.

🎉 **Congratulations!** You just made an open-source contribution. Our team will review your PR, leave constructive feedback, and merge your code into the project.

---

## 📜 Code Style & Principles

* **100% Offline & Private**: Do not introduce dependencies or APIs that upload user files to third-party cloud servers.
* **Clean Code**: Keep functions modular and use clear variable names.
* **Kindness First**: Be encouraging, respectful, and helpful to fellow students in issues and discussions.
