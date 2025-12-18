# Contributing to E-Commerce Sales Performance & Customer Behavior Analysis

First off, thank you for considering contributing to this project! 🎉

This document provides guidelines for contributing to this data analysis project. Following these guidelines helps maintain quality and makes the contribution process smooth for everyone.

---

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How Can I Contribute?](#how-can-i-contribute)
3. [Development Setup](#development-setup)
4. [Contribution Workflow](#contribution-workflow)
5. [Style Guidelines](#style-guidelines)
6. [Commit Message Convention](#commit-message-convention)
7. [Pull Request Process](#pull-request-process)
8. [Testing Guidelines](#testing-guidelines)

---

## 🤝 Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code:

- **Be respectful** and inclusive
- **Be collaborative** and constructive
- **Focus on what is best** for the community
- **Show empathy** towards other community members

---

## 💡 How Can I Contribute?

### Reporting Bugs

**Before submitting a bug report:**
- Check the [Issues](https://github.com/hamzakhan0712/E-Commerce-Sales-Performance-Customer-Behavior-Analysis/issues) to see if the problem has already been reported
- Collect information about the bug (error messages, screenshots, steps to reproduce)

**When submitting a bug report, include:**
- **Clear title** and description
- **Steps to reproduce** the issue
- **Expected vs. actual behavior**
- **Environment details** (Python version, OS, library versions)
- **Error logs** or screenshots if applicable

**Example bug report:**
```markdown
**Bug:** Data cleaning function fails on missing CustomerID

**Steps to Reproduce:**
1. Load raw_data.csv
2. Run `clean_ecommerce_data(df)`
3. Observe KeyError

**Expected:** Function should handle missing CustomerIDs gracefully
**Actual:** Function crashes with KeyError: 'CustomerID'

**Environment:**
- Python 3.10.8
- pandas 2.0.3
- OS: Windows 11
```

### Suggesting Enhancements

**Enhancement suggestions are welcome!** Examples include:
- New analysis techniques
- Additional visualizations
- Performance improvements
- Better documentation

**When suggesting an enhancement:**
- Use a **clear, descriptive title**
- Provide a **detailed description** of the proposed feature
- Explain **why this enhancement would be useful**
- Include **mockups or examples** if applicable

### Improving Documentation

Documentation improvements are highly valued:
- Fix typos or clarify confusing sections
- Add examples or tutorials
- Improve README or docstrings
- Translate documentation (if applicable)

### Adding New Features

**Before starting work on a new feature:**
1. **Open an issue** to discuss the feature
2. Wait for **maintainer feedback**
3. Get **approval** before implementing

**Feature contribution checklist:**
- [ ] Feature is discussed and approved
- [ ] Code follows style guidelines
- [ ] Tests are added (if applicable)
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.8+
- Git
- Jupyter Notebook

### Setup Instructions

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/E-Commerce-Sales-Performance-Customer-Behavior-Analysis.git
   cd E-Commerce-Sales-Performance-Customer-Behavior-Analysis
   ```

2. **Create a virtual environment**
   ```bash
   # Using venv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # OR using conda
   conda env create -f environment.yml
   conda activate ecommerce-analysis
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a branch for your work**
   ```bash
   git checkout -b feature/your-feature-name
   ```

5. **Verify setup**
   ```bash
   # Run tests
   pytest tests/
   
   # Check code style
   flake8 src/
   black --check src/
   ```

---

## 🔄 Contribution Workflow

1. **Create an issue** (for features/bugs)
2. **Fork** the repository
3. **Create a branch** (`git checkout -b feature/amazing-feature`)
4. **Make changes** (follow style guidelines)
5. **Test your changes** (`pytest tests/`)
6. **Commit** (`git commit -m 'Add amazing feature'`)
7. **Push** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request**

---

## 📝 Style Guidelines

### Python Code Style

Follow **PEP 8** with these conventions:

```python
# Good
def calculate_customer_lifetime_value(df, customer_id):
    """
    Calculate CLV for a specific customer.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Transaction dataframe
    customer_id : int
        Customer identifier
    
    Returns:
    --------
    float : Customer lifetime value
    """
    customer_transactions = df[df['CustomerID'] == customer_id]
    clv = customer_transactions['TotalPrice'].sum()
    return clv

# Bad
def calc_clv(d, c):  # Unclear function and variable names
    return d[d['CustomerID']==c]['TotalPrice'].sum()  # No docstring, poor spacing
```

**Code formatting tools:**
```bash
# Auto-format code
black src/

# Check style
flake8 src/

# Sort imports
isort src/
```

### Notebook Guidelines

- **Clear markdown explanations** before each code cell
- **Meaningful cell outputs** (no empty cell executions)
- **Restart kernel and run all** before committing
- **Remove large outputs** (images, dataframes with >100 rows)
- **Use section headings** (## for main sections, ### for subsections)

Example notebook structure:
```markdown
## 1. Introduction
Brief description of the analysis...

### 1.1 Load Data
```python
# Load dataset with error handling
df = pd.read_csv('data/raw_data.csv', encoding='latin1')
```

### Documentation Style

- Use **clear, concise language**
- Include **code examples** for functions
- Provide **context** for business decisions
- Use **consistent formatting** (Markdown)

---

## ✉️ Commit Message Convention

Follow **Conventional Commits** specification:

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code formatting (no logic change)
- **refactor**: Code restructuring (no behavior change)
- **test**: Adding/updating tests
- **chore**: Maintenance tasks

### Examples

```bash
# Feature
feat(feature-engineering): add RFM segmentation function

Implemented create_rfm_scores() to classify customers into 5 segments
based on Recency, Frequency, and Monetary values.

Closes #42

# Bug fix
fix(data-cleaning): handle missing CustomerID gracefully

Added conditional check to prevent KeyError when CustomerID is missing.
Function now skips rows with null CustomerID instead of crashing.

Fixes #38

# Documentation
docs(README): update installation instructions

Added conda environment setup steps and troubleshooting section
for common installation issues on Windows.
```

---

## 🔀 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines (run `black` and `flake8`)
- [ ] Tests pass (`pytest tests/`)
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Commit messages follow convention
- [ ] Branch is up-to-date with `main`

### PR Title Format

```
[Type] Brief description

Examples:
[Feature] Add customer churn prediction model
[Fix] Resolve data cleaning function crash
[Docs] Update README with SQL setup instructions
```

### PR Description Template

```markdown
## Description
Brief description of changes...

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Related Issues
Closes #42

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing performed
- [ ] All tests pass

## Screenshots (if applicable)
[Add screenshots here]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review performed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

### Review Process

1. **Automated checks** run (tests, linting)
2. **Maintainer review** (1-3 business days)
3. **Address feedback** (if any)
4. **Approval** and merge

---

## 🧪 Testing Guidelines

### Writing Tests

```python
# tests/test_data_cleaning.py
import pytest
import pandas as pd
from src.data_cleaning import remove_cancelled_orders

def test_remove_cancelled_orders():
    """Test that cancelled orders are removed correctly"""
    # Arrange
    df = pd.DataFrame({
        'InvoiceNo': ['536365', 'C536366', '536367'],
        'Quantity': [6, -6, 12]
    })
    
    # Act
    result = remove_cancelled_orders(df)
    
    # Assert
    assert len(result) == 2
    assert 'C536366' not in result['InvoiceNo'].values
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_data_cleaning.py

# Run with coverage
pytest --cov=src tests/

# Run verbose
pytest -v tests/
```

---

## 🎓 Learning Resources

**Python for Data Analysis:**
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Python Data Science Handbook](https://jakevdp.github.io/PythonDataScienceHandbook/)

**Git & GitHub:**
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

**Testing:**
- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://realpython.com/pytest-python-testing/)

---

## 📧 Questions?

- **Open an issue** for technical questions
- **Email maintainer:** hamzakhan@example.com
- **GitHub Discussions:** For general questions

---

## 🙏 Recognition

Contributors will be recognized in:
- README.md (Contributors section)
- CHANGELOG.md (for significant contributions)

**Thank you for contributing!** Your work helps improve this project for everyone. 🚀

---

**Last Updated:** December 18, 2024  
**Maintainer:** Hamza Khan
