# 🤝 Contribution Guidelines

Thank you for your interest in contributing. This repository aims to be the **Gold Standard** for AI Engineering. As such, we have strict quality controls.

## 🚫 What We Do Not Accept
- **Toy Examples:** No `print("hello world")`. Real systems rely on logging.
- **Academic Code:** Variable names like `x`, `y`, `df` are forbidden. Use `user_input`, `prediction_scores`, `customer_dataframe`.
- **Unformatted Code:** Everything must pass `ruff` and `black`.
- **No Context:** Every PR must explain *why* this change is valuable in a production setting.

## ✅ The Gold Standard Checklist
Before submitting, ensure your contribution:
1. **Is Type Hinted:** Fully strict Python typing (`mypy` compliant).
2. **Has Error Handling:** No bare `try/except`. handle specific exceptions.
3. **Is Documented:** Docstrings for every function using Google or NumPy style.
4. **Includes Tests:** Unit tests (pytest) are mandatory.

## 📂 Structure
- Place new concepts in the appropriate Block folder.
- If adding a new tool, include a `README.md` explaining "When to use" and "When NOT to use".

## 🧠 Mental Model Checks
Ask yourself:
- "Would I let a junior engineer push this to prod?"
- "Does this explain the *tradeoffs*?"

Let's build the best resource on the internet, together.
