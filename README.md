# AI Changelog Generator

An AI-powered tool to automatically generate and manage well-structured changelogs from Git repository commits.

## Overview

This application solves two key challenges in writing changelogs:

1. Automates the process of analyzing commit histories to identify meaningful changes
2. Uses AI to generate concise, user-friendly changelog entries that focus on what matters to end-users

The solution consists of two main components:
- A developer-facing tool for easily generating AI-powered changelogs
- A public-facing website to display the changelogs to users

## Features

### For Developers
- Select a Git repository and generate a changelog with a single click
- Specify version numbers and commit ranges
- Edit and customize the AI-generated changelogs
- Copy as Markdown or HTML for easy integration with other tools

### For End-Users
- Clean, modern UI for viewing changelogs
- Fully responsive design that works on all devices
- Syntax highlighting for code snippets

## Installation and Setup

### Prerequisites
- Python 3.8+
- Git

### Installation Steps

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/aichangelog.git
   cd aichangelog
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment:
   - Copy the `.env.example` file to `.env`
   - Add your OpenAI API key in the `.env` file

5. Run the application:
   ```bash
   python app.py
   ```

6. Access the application:
   - Developer interface: http://localhost:5000/developer
   - Public changelog website: http://localhost:5000/

## Usage

### Creating a New Changelog

1. Navigate to the Developer Portal (http://localhost:5000/developer)
2. Enter the path to your Git repository
3. Specify the version number for this changelog (e.g., "v1.0.0")
4. Optionally specify commit ranges:
   - Since commit (e.g., "v0.9.0" or a commit hash)
   - Until commit (e.g., "HEAD" or a commit hash)
5. Click "Generate Changelog"
6. Review the AI-generated changelog
7. Edit if necessary and save

### Viewing Changelogs

Users can view all published changelogs by visiting the public-facing website at http://localhost:5000/.

## Design Choices

### Technical Stack
- **Flask**: A lightweight web framework that allows for rapid development
- **GitPython**: For interacting with Git repositories
- **OpenAI API**: Leverages GPT-4 to generate human-like, contextually relevant changelog entries
- **SQLAlchemy**: Provides a robust ORM for database operations
- **Bootstrap 5**: Ensures a responsive, modern UI
- **EasyMDE**: For an enhanced Markdown editing experience
- **Marked.js**: For client-side Markdown rendering

### Product Decisions
1. **Two-Interface Approach**: Separating the developer tool from the public site ensures each audience gets exactly what they need
2. **Customizable Output**: AI generates the initial content, but developers can review and customize to maintain full control
3. **Context Preservation**: The system stores the Git commit data along with each changelog, allowing for coherent incremental updates
4. **Copy Options**: Supporting both Markdown and HTML output formats provides flexibility for different publishing workflows
5. **Markdown Format**: Using Markdown enables rich formatting while maintaining simplicity and portability

## Future Improvements

- Add user authentication for the developer interface
- Support for multiple projects in a single instance
- Integration with GitHub/GitLab webhooks for automatic changelog generation
- Email notifications for new changelog entries
- Themes and customization options for the public site

## Tools Used to Build This Project

- Python with Flask framework
- OpenAI GPT-4 API for changelog generation
- Bootstrap 5 for UI components
- GitPython for repository analysis

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
