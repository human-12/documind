# Contributing to DocuMind

Thank you for your interest in contributing to DocuMind! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect different viewpoints and experiences

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Git
- OpenAI API key

### Development Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/yourusername/documind.git
cd documind
```

2. **Set up the backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set up the frontend**

```bash
cd frontend
npm install
```

4. **Configure environment**

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

5. **Start development services**

```bash
# Terminal 1: Start database and Redis
docker-compose up postgres redis

# Terminal 2: Start backend
cd backend
python main.py

# Terminal 3: Start frontend
cd frontend
npm start
```

## Development Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical production fixes

### Making Changes

1. **Create a feature branch**

```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**

- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Update documentation as needed

3. **Test your changes**

```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
npm test

# Run API tests
python test_api.py
```

4. **Commit your changes**

```bash
git add .
git commit -m "feat: add new feature description"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

5. **Push and create a Pull Request**

```bash
git push origin feature/your-feature-name
```

## Code Style Guidelines

### Python (Backend)

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to functions and classes

Example:
```python
def process_document(file_path: str, file_type: str) -> tuple[str, dict]:
    """
    Process a document and extract its content.
    
    Args:
        file_path: Path to the document file
        file_type: Type of the document (pdf, docx, etc.)
        
    Returns:
        Tuple of (extracted_text, metadata_dict)
    """
    # Implementation
    pass
```

### JavaScript/React (Frontend)

- Use ES6+ features
- Functional components with hooks
- Use meaningful component and variable names
- Add PropTypes or TypeScript for type checking
- Keep components small and focused

Example:
```javascript
function DocumentCard({ document, onDelete }) {
  const [isDeleting, setIsDeleting] = useState(false);
  
  const handleDelete = async () => {
    setIsDeleting(true);
    await onDelete(document.id);
    setIsDeleting(false);
  };
  
  return (
    // JSX
  );
}
```

### CSS

- Use CSS variables for consistency
- Follow BEM naming convention when applicable
- Mobile-first responsive design
- Organize styles by component

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Integration Tests

```bash
python test_api.py
```

## Documentation

- Update README.md for user-facing changes
- Update API documentation for endpoint changes
- Add JSDoc comments for complex functions
- Update CHANGELOG.md with your changes

## Pull Request Process

1. **Ensure all tests pass**
2. **Update documentation**
3. **Add a clear PR description**:
   - What changes were made
   - Why these changes were needed
   - How to test the changes
4. **Link related issues**
5. **Request review from maintainers**
6. **Address review feedback**

### PR Title Format

Use conventional commits format:
```
feat(backend): add document versioning support
fix(frontend): resolve upload progress bar issue
docs: update API documentation
```

## Reporting Bugs

### Before Submitting

- Check existing issues to avoid duplicates
- Verify the bug in the latest version
- Collect relevant information

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Ubuntu 22.04]
 - Browser: [e.g. Chrome 120]
 - Version: [e.g. 1.0.0]

**Additional context**
Any other context about the problem.
```

## Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Any alternative solutions or features you've considered.

**Additional context**
Any other context or screenshots.
```

## Architecture Guidelines

### Backend Architecture

- Keep routes thin, move logic to service layer
- Use dependency injection
- Follow SOLID principles
- Keep database queries in repository layer
- Use async/await for I/O operations

### Frontend Architecture

- Component-based architecture
- Separate presentation and container components
- Use custom hooks for shared logic
- Keep state as local as possible
- Use context for global state when needed

## Performance Considerations

- Optimize database queries (use indexes)
- Implement proper caching strategies
- Minimize API calls
- Lazy load components when appropriate
- Optimize images and assets

## Security Guidelines

- Never commit API keys or secrets
- Validate all user inputs
- Sanitize data before database operations
- Use parameterized queries
- Implement rate limiting
- Follow OWASP guidelines

## Questions?

- Open a discussion on GitHub
- Join our community chat
- Email the maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to DocuMind! 🚀
