# These are the text responses that I'm using in a class
import random

class TextResponses:
    def __init__(self):
        self.text_responses = {
            "help": ["Ask me 'any deals today?' to see what subs are on sale today.",
                     "Ask 'what's on sale' to see what on sale today.",
                     "Ask me what's on sale right now to get today's sub deals"],
            "no_sale": "There are no subs on sale today.",
            "error": "Sorry, I don't understand.",
            "sale_prompt": ["deal",
                            "sale",
                            "on sale",
                            "on sale today",
                            "on sale right now",
                            "today's deals",
                            "today's deal"]
        }

    def get_response(self, response):
        if response == "help":
            return random.choice(self.text_responses[response])
        else:
            return self.text_responses[response]