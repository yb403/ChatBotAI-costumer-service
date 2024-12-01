from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import re
class ActionCheckOrderStatus(Action):
    def name(self) -> str:
        return "action_check_order_status"

    def run(self, dispatcher, tracker, domain):
        order_id = tracker.get_slot('order_id')
        if order_id:

            order_status = "Completed"  # Example response
            dispatcher.utter_message(text=f"The status of your order with ID {order_id} is: {order_status}.")
        else:
            dispatcher.utter_message(text=f"Sorry, I couldn't find the order ID.")


        
        return []
class ActionCheckEmail(Action):
    def name(self) -> str:
        return "action_check_email"

    def run(self, dispatcher, tracker, domain):
        email = tracker.get_slot('email')
        email_pattern = r"[^@]+@[^@]+\.[^@]+"
        

        if email and re.match(email_pattern, email):
            
            
            dispatcher.utter_message(text=f"The email {email} is valid.")
        else:
            dispatcher.utter_message(text="Sorry, the provided email seems invalid. Please provide a valid email address.")

        return []
    

class ActionCheckPhone(Action):
    def name(self) -> str:
        return "action_check_phone"

    def run(self, dispatcher, tracker, domain):
        phone = tracker.get_slot('phone')
        if phone:
            dispatcher.utter_message(text=f"The phone {phone} is valid.")
        else:
            dispatcher.utter_message(text="Sorry, the provided phone seems invalid. Please provide a valid email address.")

        return []