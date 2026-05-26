with open('/Users/jero87/karmic.gochara/app.py', 'r') as f:
    content = f.read()

import re

# Fix index()
old_index = """    return render_template(
        "index.html",
        user=user,"""
new_index = """    # Injecte 'illimite' si le pseudo est dans la liste VIP
    display_user = dict(user) if user else {}
    if display_user.get("pseudo", "").lower() in UNLIMITED_PSEUDOS:
        display_user["plan"] = "illimite"

    return render_template(
        "index.html",
        user=display_user,"""
if old_index in content:
    content = content.replace(old_index, new_index)

with open('/Users/jero87/karmic.gochara/app.py', 'w') as f:
    f.write(content)
