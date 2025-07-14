# Contributing to LinkAce Classifier

We welcome contributions to the LinkAce Classifier project! This document provides guidelines for contributing to make the process smooth and effective for everyone.

## 🤝 How to Contribute

### Reporting Issues

Before creating an issue, please:
1. Check the existing issues to avoid duplicates
2. Use the issue templates when available
3. Provide clear, detailed information about the problem
4. Include steps to reproduce the issue
5. Specify your environment (Python version, OS, LinkAce version, Ollama model)

### Suggesting Features

We appreciate feature suggestions! Please:
1. Check existing feature requests first
2. Explain the use case and problem you're trying to solve
3. Provide examples of how the feature would work
4. Consider the impact on existing functionality

### Code Contributions

1. **Fork the repository** and create a feature branch
2. **Set up your development environment**:
   ```bash
   git clone https://github.com/yourusername/linkace-classifier.git
   cd linkace-classifier
   pip install -r requirements.txt
   ```
3. **Make your changes** following our coding standards
4. **Test your changes** thoroughly
5. **Submit a pull request** with a clear description

## 🔧 Development Setup

### Prerequisites

- Python 3.7+
- Ollama server for testing
- LinkAce instance for integration tests (optional)

### Local Development

1. **Clone and setup**:
   ```bash
   git clone https://github.com/yourusername/linkace-classifier.git
   cd linkace-classifier
   pip install -r requirements.txt
   ```

2. **Run tests**:
   ```bash
   python test_classifier.py
   ```

3. **Run demo**:
   ```bash
   python demo_classifier.py
   ```

### Testing

Before submitting a pull request:
1. Run the test suite: `python test_classifier.py`
2. Test with different Ollama models if possible
3. Ensure your changes don't break existing functionality
4. Add tests for new features

## 📝 Coding Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings for all public functions and classes
- Keep functions focused and concise
- Use type hints where appropriate

### Documentation

- Update docstrings for any modified functions
- Add comments for complex logic
- Update README.md if adding new features
- Include examples in docstrings when helpful

### Commit Messages

Use clear, descriptive commit messages:
- Use imperative mood ("Add feature" not "Added feature")
- Keep first line under 50 characters
- Include more details in the body if necessary
- Reference issues when applicable

Examples:
```
Add confidence threshold validation

- Validate threshold is between 0.0 and 1.0
- Add helpful error messages for invalid values
- Update tests to cover validation cases

Fixes #123
```

## 🚀 Pull Request Process

1. **Create a feature branch** from main:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit them:
   ```bash
   git add .
   git commit -m "Add your feature description"
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a pull request** with:
   - Clear title and description
   - Reference to related issues
   - Screenshots or examples if applicable
   - Notes about testing performed

### Pull Request Checklist

- [ ] Code follows the project's coding standards
- [ ] Tests pass locally
- [ ] New features include tests
- [ ] Documentation updated if necessary
- [ ] No merge conflicts with main branch
- [ ] Pull request description is clear and complete

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
python test_classifier.py

# Run demo with sample data
python demo_classifier.py

# Test specific functionality
python -c "from linkace_api import LinkAceClient; print('API module OK')"
```

### Adding Tests

When adding new features:
1. Add unit tests for new functions
2. Test error conditions and edge cases
3. Ensure tests are independent and can run in any order
4. Use descriptive test names

### Test Coverage

- Aim for good test coverage of new code
- Test both success and failure scenarios
- Include tests for configuration validation
- Test API integration points

## 📚 Documentation

### README Updates

If your changes affect:
- Installation process
- Configuration options
- Usage examples
- API endpoints
- Troubleshooting

Please update the README.md file accordingly.

### Code Documentation

- Add docstrings for new functions and classes
- Update existing docstrings if behavior changes
- Include parameter types and return values
- Add usage examples for complex functions

## 🐛 Bug Reports

When reporting bugs, include:
- Python version and OS
- LinkAce version and configuration
- Ollama model and version
- Complete error messages and stack traces
- Steps to reproduce the issue
- Expected vs actual behavior

### Security Issues

For security-related issues:
1. Do not create public issues
2. Contact maintainers privately
3. Allow time for fix before public disclosure

## 💡 Feature Requests

Good feature requests include:
- Clear description of the problem
- Proposed solution with examples
- Use cases and benefits
- Consideration of implementation complexity
- Backward compatibility impact

## 📋 Code Review Process

### For Contributors

- Be open to feedback and suggestions
- Respond to review comments promptly
- Make requested changes or discuss alternatives
- Keep pull requests focused and atomic

### For Reviewers

- Be constructive and helpful
- Focus on code quality and project consistency
- Test changes locally when possible
- Provide clear feedback on requested changes

## 🔄 Release Process

Releases follow semantic versioning:
- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes, backward compatible

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: For implementation guidance
- **Documentation**: Check README.md and inline documentation

## 🎯 Project Goals

Keep these goals in mind when contributing:
- **Reliability**: Robust error handling and edge case coverage
- **Usability**: Clear configuration and helpful error messages
- **Performance**: Efficient processing of large link collections
- **Maintainability**: Clean, well-documented code
- **Compatibility**: Support for different LinkAce and Ollama versions

## 📜 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Maintain a positive, collaborative environment

## 🙏 Recognition

Contributors will be recognized in:
- Git commit history
- Release notes for significant contributions
- README acknowledgments section

Thank you for contributing to LinkAce Classifier! 🚀