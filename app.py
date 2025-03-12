import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import git
import openai
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///changelogs.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Database models
class Changelog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    raw_git_data = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Changelog {self.version}>'

# Create database tables
with app.app_context():
    db.create_all()

# Git operations
def get_commit_logs(repo_path, since_commit=None, until_commit=None):
    """Get commit logs from a git repository"""
    try:
        repo = git.Repo(repo_path)
        
        # If since_commit is not provided, use the latest version's commit or HEAD~20
        if not since_commit:
            try:
                latest_changelog = Changelog.query.order_by(Changelog.date.desc()).first()
                if latest_changelog and latest_changelog.raw_git_data:
                    data = json.loads(latest_changelog.raw_git_data)
                    since_commit = data.get('until_commit', 'HEAD~20')
                else:
                    since_commit = 'HEAD~20'
            except Exception as e:
                print(f"Error getting latest changelog: {e}")
                since_commit = 'HEAD~20'
        
        # If until_commit is not provided, use HEAD
        if not until_commit:
            until_commit = 'HEAD'
        
        # Get commits between since_commit and until_commit
        commits = list(repo.iter_commits(f"{since_commit}..{until_commit}"))
        
        # Get commit details
        commit_details = []
        for commit in commits:
            commit_details.append({
                'hash': commit.hexsha,
                'author': f"{commit.author.name} <{commit.author.email}>",
                'date': commit.committed_datetime.isoformat(),
                'message': commit.message,
                'files': [item.a_path for item in commit.diff(commit.parents[0])] if commit.parents else []
            })
        
        return {
            'since_commit': since_commit,
            'until_commit': until_commit,
            'commits': commit_details
        }
    except Exception as e:
        print(f"Error getting commit logs: {e}")
        return None

# AI changelog generation
def generate_changelog(git_data):
    """Generate a changelog using OpenAI"""
    try:
        # Prepare commit data for the prompt
        commit_text = ""
        for commit in git_data['commits']:
            commit_text += f"Commit: {commit['hash'][:8]}\n"
            commit_text += f"Author: {commit['author']}\n"
            commit_text += f"Date: {commit['date']}\n"
            commit_text += f"Message: {commit['message']}\n"
            commit_text += f"Files: {', '.join(commit['files'])}\n\n"
        
        # Create the prompt for OpenAI
        prompt = f"""
        You are an expert at creating changelogs for developer tools. Your task is to analyze the following git commits and create a well-organized changelog with the following sections:
        
        1. New Features
        2. Improvements
        3. Bug Fixes
        4. Breaking Changes (if any)
        
        For each item, write a concise, user-facing description that explains what changed and why it matters to users.
        Focus only on changes that would be relevant to end-users (developers using this tool).
        Ignore internal refactoring, test changes, or other updates that don't affect the user experience unless they improve performance significantly.
        
        Here are the git commits to analyze:
        
        {commit_text}
        
        Format the changelog in Markdown.
        """
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in creating developer changelogs."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract and return the generated changelog
        changelog_content = response.choices[0].message.content
        return changelog_content
    
    except Exception as e:
        print(f"Error generating changelog: {e}")
        return f"Error generating changelog: {str(e)}"

# Routes for developer interface
@app.route('/developer', methods=['GET'])
def developer_interface():
    changelogs = Changelog.query.order_by(Changelog.date.desc()).all()
    return render_template('developer.html', changelogs=changelogs)

@app.route('/developer/generate', methods=['POST'])
def generate():
    repo_path = request.form.get('repo_path')
    version = request.form.get('version')
    since_commit = request.form.get('since_commit')
    until_commit = request.form.get('until_commit')
    
    if not repo_path:
        flash('Repository path is required', 'error')
        return redirect(url_for('developer_interface'))
    
    if not version:
        flash('Version number is required', 'error')
        return redirect(url_for('developer_interface'))
    
    # Get commit logs
    git_data = get_commit_logs(repo_path, since_commit, until_commit)
    if not git_data:
        flash('Failed to get commit logs. Check the repository path and commits.', 'error')
        return redirect(url_for('developer_interface'))
    
    # Generate changelog
    changelog_content = generate_changelog(git_data)
    
    # Save to database
    new_changelog = Changelog(
        version=version,
        content=changelog_content,
        raw_git_data=json.dumps(git_data)
    )
    db.session.add(new_changelog)
    db.session.commit()
    
    flash('Changelog generated successfully', 'success')
    return redirect(url_for('view_changelog', id=new_changelog.id))

@app.route('/developer/changelog/<int:id>', methods=['GET'])
def view_changelog(id):
    changelog = Changelog.query.get_or_404(id)
    return render_template('view_changelog.html', changelog=changelog)

@app.route('/developer/changelog/<int:id>/edit', methods=['GET', 'POST'])
def edit_changelog(id):
    changelog = Changelog.query.get_or_404(id)
    
    if request.method == 'POST':
        changelog.version = request.form.get('version')
        changelog.content = request.form.get('content')
        db.session.commit()
        flash('Changelog updated successfully', 'success')
        return redirect(url_for('view_changelog', id=changelog.id))
    
    return render_template('edit_changelog.html', changelog=changelog)

@app.route('/developer/changelog/<int:id>/delete', methods=['POST'])
def delete_changelog(id):
    changelog = Changelog.query.get_or_404(id)
    db.session.delete(changelog)
    db.session.commit()
    flash('Changelog deleted successfully', 'success')
    return redirect(url_for('developer_interface'))

# Routes for public-facing website
@app.route('/')
def index():
    changelogs = Changelog.query.order_by(Changelog.date.desc()).all()
    return render_template('index.html', changelogs=changelogs)

@app.route('/changelog/<int:id>')
def public_changelog(id):
    changelog = Changelog.query.get_or_404(id)
    return render_template('public_changelog.html', changelog=changelog)

# API endpoints
@app.route('/api/changelogs', methods=['GET'])
def api_changelogs():
    changelogs = Changelog.query.order_by(Changelog.date.desc()).all()
    result = []
    for changelog in changelogs:
        result.append({
            'id': changelog.id,
            'version': changelog.version,
            'date': changelog.date.isoformat(),
            'content': changelog.content
        })
    return jsonify(result)

@app.route('/api/changelog/<int:id>', methods=['GET'])
def api_changelog(id):
    changelog = Changelog.query.get_or_404(id)
    return jsonify({
        'id': changelog.id,
        'version': changelog.version,
        'date': changelog.date.isoformat(),
        'content': changelog.content
    })

if __name__ == '__main__':
    app.run(debug=True)
