# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in ThoughtBase, please report it responsibly:

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. Email security concerns to: james@think.dev
3. Include a detailed description of the vulnerability
4. If possible, include steps to reproduce

We will acknowledge receipt within 48 hours and aim to provide a fix within 7 days for critical issues.

## Security Considerations

ThoughtBase sends Python code to a cloud backend for execution. Users should:

- **Never commit API keys** to version control
- Use environment variables or secret management for credentials
- Be aware that deployed code runs in a shared serverless environment
- Review code before deploying to ensure it does not contain sensitive data
- Use `set_api_key()` or the `THB_API_KEY` environment variable rather than hardcoding keys
