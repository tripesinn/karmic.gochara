# DESIGN_SPEC.md

## Overview
The 'karmic-master' agent will understand the purpose of the application, which is likely related to astrological calculations and karmic insights, given the project context. It will act as a core intelligent component of the application.

## Example Use Cases
- Providing astrological insights based on user input.
- Interacting with Google Sheets for data management.
- Processing payments via Stripe API.
- Utilizing local Python astrological calculation functions.

## Tools Required
- **Google Sheets API:** For reading and writing data to Google Sheets. Authentication will likely involve OAuth 2.0 or a service account.
- **Stripe API:** For handling payment processing. Requires API key authentication.
- **Local Python Astro Functions:** Integration with existing Python functions within the 'karmic.gochara' project for astrological calculations.

## Constraints & Safety Rules
- **No medical advice:** The agent must never provide medical advice or diagnoses.
- **No guaranteed outcomes:** The agent must not guarantee any specific outcomes for astrological predictions or life events.
- **No unauthorized data access:** The agent must not access user data without explicit permission.
- **No payment circumvention:** The agent must not provide ways to bypass or circumvent payment processes.
- **Astrological disclaimer:** All astrological interpretations must include a clear disclaimer stating that they are for entertainment or informational purposes only and not definitive.

## Success Criteria
- Successfully understand and respond to user queries related to the application's purpose.
- Accurately integrate and utilize Google Sheets, Stripe API, and local Python astro functions.
- Adhere to all specified safety constraints and disclaimers.

## Reference Samples
(No specific ADK samples directly match, but patterns from data-science (code execution) or adk-ae-oauth (OAuth) might be relevant for future enhancements.)