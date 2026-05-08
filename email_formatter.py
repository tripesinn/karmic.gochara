"""
email_formatter.py - Formats astrological alerts into HTML emails.
"""

def format_alert_email(
    alert_narrative: str,
    premium_teaser: str,
    cta_text: str,
    upgrade_link: str,
    user_name: str,
    urgency: str
) -> dict:
    """
    Creates a compelling HTML email for a transit alert.
    """
    # 1. Craft Subject Line
    urgency_map = {
        "low": "Une douce énergie se présente",
        "medium": "Un transit important se profile",
        "high": "Alerte Karmique : Un transit majeur est actif",
        "critical": "ACTION REQUISE : Activation karmique critique",
    }
    subject_line = f"✦ {urgency_map.get(urgency, 'Alerte de transit')} pour {user_name}"

    # 2. Select Hero Image
    # In a real scenario, you might select an image based on the planets involved.
    # For now, we'll use a generic one.
    hero_image_url = "https://img.freepik.com/photos-gratuite/fond-texture-nuit-etoilee_1122-873.jpg"

    # 3. Build HTML Structure
    html_email = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Georgia, serif; background: #0a0a1a; color: #e8e0d0; margin: 0; padding: 20px; }}
  .container {{ max-width: 620px; margin: 0 auto; background: #0f0f2a;
                border: 1px solid #4b0082; border-radius: 4px; padding: 30px; }}
  .header img {{ width: 100%; height: auto; border-radius: 3px; }}
  h1 {{ color: #d4a017; font-size: 22px; margin-top: 20px; }}
  .narrative {{ white-space: pre-wrap; line-height: 1.7; font-size: 14px; color: #e0d8f0; }}
  .teaser {{ margin: 20px 0; padding: 16px; border: 1px dashed #d4a017; border-radius: 3px;
             background: rgba(212, 160, 23, 0.05); text-align: center; font-style: italic; color: #d4a017;}}
  .cta-button {{ display: inline-block; background: #d4a017; color: #0a0a1a; text-decoration: none;
                 padding: 12px 28px; border-radius: 3px; font-weight: bold; font-size: 14px; letter-spacing: 0.08em; }}
  .footer {{ margin-top: 28px; padding-top: 14px; border-top: 1px solid #4b0082;
             font-size: 11px; color: #606080; text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <img src="{hero_image_url}" alt="Karmic Gochara">
  </div>
  <h1>Bonjour {user_name},</h1>
  <div class="narrative">
    {alert_narrative}
  </div>
  <div class="teaser">
    "{premium_teaser}"
  </div>
  <div style="text-align: center; margin: 30px 0;">
    <a href="{upgrade_link}" class="cta-button">{cta_text}</a>
  </div>
  <div class="footer">
    <p>Ceci est une alerte de transit générée pour vous. Vous pouvez gérer vos préférences ci-dessous.</p>
    <a href="https://karmicgochara.app/preferences" style="color:#4b4b70;">Se désinscrire</a> |
    <a href="https://karmicgochara.app/preferences" style="color:#4b4b70;">Gérer mes alertes</a>
  </div>
</div>
</body>
</html>
"""
    return {
        "html_email": html_email,
        "subject_line": subject_line,
    }
