import os
import ast
from jinja2 import Environment, FileSystemLoader

# Path to the files
APP_PY_PATH = 'app.py'
TEMPLATE_PATH = 'templates'
INDEX_TEMPLATE = 'index.html'
OUTPUT_PATH = 'www/index.html'

def get_langs_from_app():
    """Extract LANGS dictionary from app.py using AST."""
    with open(APP_PY_PATH, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'LANGS':
                    # This is the line. We need to evaluate the value safely.
                    # Since it's a literal dict in app.py, ast.literal_eval works.
                    return ast.literal_eval(node.value)
    return {}

def render():
    langs = get_langs_from_app()
    if not langs:
        print("Error: Could not extract LANGS from app.py using AST")
        return

    # Choose French as default
    lang_fr = langs.get('fr', {})
    if not lang_fr:
        print("Error: 'fr' not found in LANGS")
        return

    env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
    template = env.get_template(INDEX_TEMPLATE)
    
    # Render with defaults
    rendered = template.render(
        lang=lang_fr,
        langs=langs,
        session_user='', # Not logged in by default
        session_profile={}, # Empty dict to avoid .get() UndefinedError
        user={}, # Empty dict to avoid UndefinedError
        today_iso='' 
    )
    
    # Fix asset paths: /static/ -> static/
    # Handled carefully to not break paths that are already relative if any
    rendered = rendered.replace('href="/static/', 'href="static/')
    rendered = rendered.replace('src="/static/', 'src="static/')
    rendered = rendered.replace('"/static/', '"static/')
    
    # Write output
    if not os.path.exists('www'):
        os.makedirs('www')
        
    # Copy static folder to www/static to bundle with mobile assets
    import shutil
    static_dest = os.path.join('www', 'static')
    if os.path.exists(static_dest):
        shutil.rmtree(static_dest)
    shutil.copytree('static', static_dest)
        
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(rendered)
    
    print(f"Successfully rendered static index and copied assets to {OUTPUT_PATH}")

if __name__ == "__main__":
    render()
