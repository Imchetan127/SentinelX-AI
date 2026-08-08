# Contributing to SentinelX AI

Thank you for your interest in contributing to **SentinelX AI**! This guide outlines the development process, code standards, and contribution workflow.

---

## 1. Code of Conduct

We are committed to maintaining a welcoming, inclusive, and professional open-source community. Please treat all contributors and maintainers with respect and constructive feedback.

---

## 2. Development Workflow

### 2.1 Repository Setup
1. Fork and clone the repository:
   ```bash
   git clone https://github.com/<your-username>/Red-team-vs-Blue-team.git
   cd Red-team-vs-Blue-team
   ```
2. Set up the Python backend environment:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Set up the Next.js frontend environment:
   ```bash
   cd ../frontend
   npm install
   ```

---

## 3. Git Branching Strategy

We follow a structured branching model:

- `main`: Production-ready releases (tagged `vX.Y.Z`).
- `feature/<feature-name>`: New feature implementations.
- `bugfix/<bug-description>`: Bug fixes and patches.
- `docs/<doc-topic>`: Documentation enhancements.

---

## 4. Conventional Commit Messages

Commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` A new feature implementation (e.g. `feat(xai): add XGBoost SHAP support`)
- `fix:` A bug fix (e.g. `fix(reports): resolve route shadow ordering for /history`)
- `docs:` Documentation updates (e.g. `docs(api): update REST specification`)
- `test:` Adding or updating tests (e.g. `test(reporting): add SHA256 tamper verification test`)
- `refactor:` Code refactoring without changing logic (e.g. `refactor(inference): optimize scaler cache`)
- `infra:` Docker or deployment changes (e.g. `infra(docker): add healthcheck probe to compose`)

---

## 5. Pull Request Checklist

Before submitting a Pull Request:
1. Ensure all 78 tests pass:
   ```bash
   cd backend
   JWT_SECRET="testsecretkey12345678901234567890" DATABASE_URL="sqlite:///:memory:" ./.venv/bin/pytest tests/ -v
   ```
2. Verify code adheres to PEP 8 (backend) and ESLint/Prettier (frontend).
3. Ensure no hardcoded secrets or environment credentials are included.
4. Include an updated test case if adding a new service or API endpoint.
5. Provide a clear description of changes in the PR template.
