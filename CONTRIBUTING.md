# Contributing to Snowsports Program Manager

Thank you for your interest in contributing to the Snowsports Program Manager! We welcome contributions from the community to help improve this project.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
   ```bash
   git clone https://github.com/your-username/snowsports-program-manager.git
   cd snowsports-program-manager
   ```
3. **Set up the development environment** (see [README.md](README.md) for detailed instructions)
4. **Create a new branch** for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🔧 Development Workflow

### Code Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use 4 spaces for indentation (no tabs)
- Keep lines under 88 characters (PEP 8 recommendation)
- Use docstrings for all public modules, functions, classes, and methods

### Git Commit Messages
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally
- Consider starting the commit message with an applicable emoji:
  - ✨ `:sparkles:` When adding a new feature
  - 🐛 `:bug:` When fixing a bug
  - ♻️ `:recycle:` When refactoring code
  - 📚 `:books:` When writing docs
  - 🚧 `:construction:` WIP (Work In Progress)
  - ⬆️ `:arrow_up:` When upgrading dependencies
  - ⬇️ `:arrow_down:` When downgrading dependencies

### Testing
- Write tests for new features and bug fixes
- Run all tests before submitting a pull request
   ```bash
   pytest
   ```
- Ensure all tests pass before pushing changes

## 🛠 Making Changes

1. **Start with an issue** - If you're working on a new feature or bug fix, please create an issue first to discuss the changes.

2. **Keep your changes focused** - Each pull request should address a single issue or add a single feature.

3. **Update documentation** - If your changes affect how users interact with the application, please update the relevant documentation.

4. **Add tests** - New features and bug fixes should include tests.

## 📝 Submitting a Pull Request

1. **Update your fork**
   ```bash
   git fetch upstream
   git merge upstream/main
   ```

2. **Run tests** to ensure everything works as expected
   ```bash
   pytest
   ```

3. **Commit your changes** with a clear commit message
   ```bash
   git commit -am "Add some feature"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request** from your fork to the main repository

## 🏷 Issue and Pull Request Labels

- `bug` - Something isn't working
- `documentation` - Improvements or additions to documentation
- `duplicate` - This issue or pull request already exists
- `enhancement` - New feature or request
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `invalid` - This doesn't seem right
- `question` - Further information is requested
- `wontfix` - This will not be worked on

## 📜 Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🙏 Thank You!

Your contributions to open source, large or small, make great projects like this possible. Thank you for taking the time to contribute.
