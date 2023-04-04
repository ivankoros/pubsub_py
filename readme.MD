# Pubsub Py: Allowing automated, simple ordering for Publix deli subs through text with natural language processing

Pubsub Py simplifies your Publix deli sub ordering process using natural language processing. This project allows you to place an order with a single text message and sends you timely reminders, making it perfect for your busy schedule and tight wallet.

**Note: This project is a work in progress.**

## How it works

Powered by Selenium 4, Pubsub Py scrapes your local deli's website daily and keeps you informed through text messages, courtesy of Twilio. The text responses are parsed using spaCy's natural language processing to enable one-text, one-line online order placement. The project is dockerized and scheduled with cron to ensure a seamless experience.

### Major Technologies Used

- **Selenium**: A Python library for web automation that enables autonomous browser control for automated web page interaction.
- **Twilio**: A cloud communications platform that automates incoming and outgoing SMS using its Python library.
- **SpaCy**: A Python library for natural language processing, used to extract meaning from text, such as customer preferences, to help create the perfect sandwich.
- **Docker**: A containerization platform that packages applications and their dependencies in lightweight, portable containers for easy deployment.

## Getting Started

These instructions will guide you through setting up Pubsub Py on your local machine.

### Prerequisites

- Python 3.8 or newer
- Docker installed
- A Twilio account

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pubsub_py.git
cd pubsub_py
```
