from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import mysql.connector
from rasa_sdk.events import SlotSet
class ActionListSectors(Action):
    def name(self) -> Text:
        return "action_list_sectors"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Connect to database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chatbot"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Sector")
        sectors = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        dispatcher.utter_message(text=f"The available sectors are: {', '.join(sectors)}")
        return []
class ActionListSemesters(Action):
    def name(self) -> Text:
        return "action_list_semesters"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sector = tracker.get_slot("sector")
        
        if not sector:
            dispatcher.utter_message(text="Please specify the sector.")
            return []
        
        # Connect to database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chatbot"
        )
        cursor = conn.cursor()
        query = """
        SELECT Semester.name 
        FROM Semester
        JOIN Sector ON Semester.sector_id = Sector.id
        WHERE Sector.name = %s
        """
        cursor.execute(query, (sector,))
        semesters = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        if semesters:
            dispatcher.utter_message(text=f"The semesters in {sector} are: {', '.join(semesters)}.")
        else:
            dispatcher.utter_message(text=f"No semesters found for the sector {sector}.")
        
        # Ensure sector is correctly set in the slot
        return [SlotSet("sector", sector), SlotSet("semester", None)]

class ActionListModules(Action):
    def name(self) -> Text:
        return "action_list_modules"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        semester = tracker.get_slot("semester")
        sector = tracker.get_slot("sector")
        
        if not semester:
            dispatcher.utter_message(text="Please specify the semester.")
            return []
        
        if not sector:
            dispatcher.utter_message(text="Please specify the sector first.")
            return []
        
        # Connect to database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chatbot"
        )
        cursor = conn.cursor()
        query = """
        SELECT Module.name 
        FROM Module
        JOIN Semester ON Module.semester_id = Semester.id
        JOIN Sector ON Semester.sector_id = Sector.id
        WHERE Semester.name = %s AND Sector.name = %s
        """
        cursor.execute(query, (semester, sector))
        modules = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        if modules:
            dispatcher.utter_message(text=f"The modules in {semester} for {sector} are: {', '.join(modules)}.")
        else:
            dispatcher.utter_message(text=f"No modules found for {semester} in {sector}.")
        return []


class ActionListElements(Action):
    def name(self) -> Text:
        return "action_list_elements"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        module = tracker.get_slot("module")
        
        if not module:
            dispatcher.utter_message(text="Please specify the module.")
            return []

        # Connect to the database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chatbot"
        )
        cursor = conn.cursor()
        query = """
        SELECT Element.name 
        FROM Element
        JOIN Module ON Element.module_id = Module.id
        WHERE Module.name = %s
        """
        cursor.execute(query, (module,))
        elements = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        if elements:
            dispatcher.utter_message(text=f"The elements in {module} are: {', '.join(elements)}.")
        else:
            dispatcher.utter_message(text=f"No elements found for the module {module}.")
        
        return [SlotSet("module", module)]


class ActionListElementTeacher(Action):
    def name(self) -> Text:
        return "action_list_element_teacher"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        element = tracker.get_slot("element")
        
        if not element:
            dispatcher.utter_message(text="Please specify the element.")
            return []

        # Connect to the database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chatbot"
        )
        cursor = conn.cursor()

        query = """
        SELECT Teacher.fname, Teacher.lname
        FROM Teacher
        JOIN Element ON Teacher.id = Element.prof_id
        WHERE Element.name LIKE %s
        """
        cursor.execute(query, (f"%{element}%",))
        teacher = cursor.fetchone()
        cursor.close()
        conn.close()

        if teacher:
            fname, lname = teacher
            dispatcher.utter_message(text=f"The teacher for {element} is {fname} {lname}.")
        else:
            dispatcher.utter_message(text=f"I couldn't find a teacher for the element {element}.")
        
        return [SlotSet("element", element)]
