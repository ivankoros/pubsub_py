# PubSub Py: AI-Powered, One-Sentence Deli Sub Ordering and Deal Searching Platform for Publix

**Note: This project is a work in progress.**

PubSub Py streamlines the Publix deli sub ordering process by leveraging natural language processing and web scraping 
to empower users to discover local deals and place orders with a single text.

Utilizing the **Publix API**, PubSub Py queries daily deals from your local Publix in less than a second and sends updates
via text through **Twilio**. A **scikit-learn vectorization** model and the **Open AI API** work together to accurately parse user
responses, enabling **Selenium** 4 browser automation to order a custom sub in less than 10 seconds.

Beforehand, the Google Maps API is used to find stores near your location, and Python's GeoPy is used to rank them by shortest distance to you, allowing
you to easily pick your favorite store. Your geo information is securely stored, and will be remembered after your first input.

Supported by an AWS-hosted MySQL cloud database and Docker runtimes for efficient containerized deployment, 
PubSub Py makes grabbing a quick lunch easy on your wallet and mind.

## Flow diagram
![Flow](pubsubpy_flow.svg)

## Getting Started

These instructions will guide you through setting up Pubsub Py on your local machine.

### Prerequisites

- Python 3.8 or newer
- Docker installed
- A Twilio account

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ivankoros/pubsub_py
cd pubsub_py
```

2. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate
```


3. Install the required packages:
```python
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
export TWILIO_ACCOUNT_SID=your_account_sid
export TWILIO_AUTH_TOKEN=your_auth_token
export TWILIO_PHONE_NUMBER=your_twilio_phone_number
export YOUR_PHONE_NUMBER=your_phone_number
```

## Usage

The bot can be used to order a custom sub from Publix, with options for selecting the store location, sub customization, pickup date and time, and customer details. The bot is also capable of collecting information on current sub deals and updating the database with new deals as they appear.

By using this bot, customers can easily and quickly order their favorite subs from Publix without having to navigate through the website manually.

## Running Tests

To ensure the functionality of both Twilio and Selenium components app components, I've implemented unit tetsts through Python's Pytest with Magic Mock and Patch (found in tests/). Currently, I have complete tests for the Twilio Flask app portion of the project, including tests for: user initialization, and start, get_name, get_store_location, get_sale, and default state transitions.

Follow these steps to run the tests:

1. Ensure you are in the root directory of the project and have requirements installed

2. Run the tests
 - Twilio/Twilm Flask app tests:
 
   ```python
   pytest tests/twilio_tests.py
   
   ```
- Selenium tests:
   ```python
   pytest tests/selenium_tests.py
   ```

The tests will be executed, and you will see the results in your terminal. The tests cover ever function in the Flask app, such as login, registration, file upload, and file validation.


## Contributing

We welcome contributions to this project. Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for more information on how to contribute.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

