# Pubsub Py: Allowing automated, simple ordering for Publix deli subs through text with natural language processing

## WIP
Pubsub Py is powered by Selenium 4, scraping your local deli's website daily - dockerized and cron-scheduled - keeping users
up to date with texts powered by Twilio. Text responses are parsed with spaCy's natural language processing to allow one-text, one-line online order placement
for the perfect sandwich fitting your busy schedule and tight wallet, and a reminder to not forget to pick it up.

### Major Technologies Used

- Selenium: A Python library for web automation allowing autonomous browser control for automated web page interaction
- Twilio: A cloud communications platform allowing automation of incoming and outgoing SMS (here used through its Python library)
- SpaCy: A Python library for natural language processing used to extract meaning from text, such as customers personal preferences, powering creation of the perfect sandwich
- Docker: A containerization platform allowing the packaging of applications and their dependencies for lightweight, portable containers
