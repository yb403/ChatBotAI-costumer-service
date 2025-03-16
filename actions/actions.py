from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import mysql.connector
from rasa_sdk.events import SlotSet
class ActionListSectors(Action):
    def name(self) -> Text:return "action_list_sectors"
    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        conn = mysql.connector.connect(host="localhost",user="root",password="",database="chatbot")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Sector")
        sectors = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        dispatcher.utter_message(text=f"Les filières disponibles sont :  \n-" + "\n-".join(sectors) + ".")
        return []
    
class ActionListSemesters(Action):
    def name(self) -> Text:return "action_list_semesters"
    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sector = tracker.get_slot("sector")
        if not sector:
            dispatcher.utter_message(text="Veuillez spécifier la filière.")
            return []
        conn = mysql.connector.connect(host="localhost",user="root",password="",database="chatbot")
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
            dispatcher.utter_message(text=f"Les Semesters dans <b>{sector}</b> sont :  \n-" + "\n-".join(semesters) + ".")
        else:
            dispatcher.utter_message(text=f"Aucun Semester trouvé pour le filière <b>{sector}</b>.")
        return [SlotSet("sector", sector), SlotSet("semester", None)]

class ActionListModules(Action):
    def name(self) -> Text:return "action_list_modules"
    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        semester = tracker.get_slot("semester")
        sector = tracker.get_slot("sector")
        if not sector:
            dispatcher.utter_message(text="Veuillez spécifier la filière.")
            return [SlotSet("semester", None)]
        try:
            conn = mysql.connector.connect(host="localhost",user="root",password="",database="chatbot")
            cursor = conn.cursor()
            # If semester, return specific modules for that semester in the sector
            if semester:
                query = """
                SELECT Module.name 
                FROM Module
                JOIN Semester ON Module.semester_id = Semester.id
                JOIN Sector ON Semester.sector_id = Sector.id
                WHERE Semester.name = %s AND Sector.name = %s
                """
                cursor.execute(query, (semester, sector))
            else:
                # If not return, give all modules for the sector
                query = """
                SELECT DISTINCT Module.name 
                FROM Module
                JOIN Semester ON Module.semester_id = Semester.id
                JOIN Sector ON Semester.sector_id = Sector.id
                WHERE Sector.name LIKE %s
                """
                cursor.execute(query, (f"%{sector}%",))
            modules = [row[0] for row in cursor.fetchall()]
        except mysql.connector.Error as e:
            dispatcher.utter_message(text=f"Une erreur est survenue lors de l'accès à la base de données : {str(e)}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        if modules:
            if semester:
                dispatcher.utter_message(text=f"Les modules dans <b>{semester}</b> pour {sector} sont:  \n-" + "\n-".join(modules) + ".")
            else:
                dispatcher.utter_message(text=f"Les modules dans <b>{sector}</b> sont :  \n-" + "\n-".join(modules) + ".")
        else:
            if semester:
                dispatcher.utter_message(text=f"Aucun module trouvé pour {semester} dans {sector}.")

            else:
                dispatcher.utter_message(text=f"Aucun module trouvé dans {sector}.")
        return []


class ActionListElements(Action):
    def name(self) -> Text:return "action_list_elements"
    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        module = tracker.get_slot("module")
        sector = None
        if not module:
            module = tracker.get_slot("element")
            if not module:
                sector = tracker.get_slot("sector")
                if not sector:
                        dispatcher.utter_message(text="Veuillez spécifier le module.")
                        return []
        conn = mysql.connector.connect(host="localhost",user="root",password="",database="chatbot")
        cursor = conn.cursor()
        if sector != None:
            query = """
                SELECT Element.name
                FROM Element
                LEFT JOIN Module ON Element.module_id = Module.id AND Module.name LIKE %s
            """
            cursor.execute(query, (f"%{sector}%",))
        else:
            query = """
            SELECT Element.name 
            FROM Element
            JOIN Module ON Element.module_id = Module.id
            WHERE Module.name LIKE %s
            """
            cursor.execute(query, (f"%{module}%",))
        elements = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        if not module:
            module = sector
        if elements:
            dispatcher.utter_message(text=f"Les éléments dans <b>{module}</b> sont :  \n-" + "\n-".join(elements) + ".")
        else:
            dispatcher.utter_message(text=f"Aucun élément trouvé pour le module {module}.")
        if sector != None:
            return [SlotSet("sector", sector)]
        #return [SlotSet("module", module)]
        return [SlotSet("module", None)]


class ActionListElementTeacher(Action):
    def name(self) -> Text:return "action_list_element_teacher"
    async def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        element = tracker.get_slot("element")
        if not element:
            dispatcher.utter_message(text="Please specify the element.")
            return []
        conn = mysql.connector.connect(host="localhost",user="root",password="",database="chatbot")
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
            dispatcher.utter_message(text=f"Le professeur pour <b>{element}</b> est <b>{fname} {lname}</b>.")

        else:
            dispatcher.utter_message(text=f"Je n'ai pas trouvé de professeur pour l'élément {element}.")
        return [SlotSet("element", element)]


class ActionProvideProfessorEmail(Action):
    def name(self) -> str:return "action_provide_professor_email"
    def run(self, dispatcher: CollectingDispatcher,tracker: "Tracker",domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        first_name = tracker.get_slot("first_name")
        last_name = tracker.get_slot("last_name")
        print(first_name,last_name)
        if not first_name and not last_name:
            dispatcher.utter_message(text="Pouvez-vous me donner au moins le prénom ou le nom de famille du professeur ?")
            return []
        connection = mysql.connector.connect(host="localhost",user="root",password="",database="chatbot")
        cursor = connection.cursor()
        query = "SELECT email,fname,lname FROM Teacher WHERE"
        conditions = []
        params = []
        if first_name:
            conditions.append(" fname LIKE %s")
            params.append(f"%{first_name}%")
        if last_name:
            conditions.append(" lname LIKE %s")
            params.append(f"%{last_name}%")
        query += " AND".join(conditions)
        print(query)
        cursor.execute(query, tuple(params))
        result = cursor.fetchone()
        if result:
            email,fname,lname = result[0],result[1],result[2]
            dispatcher.utter_message(text=f"L'email de Professeur <b>{fname} {lname}</b> est : <b>{email}</b>")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas trouvé l'email de ce professeur.")
        cursor.close()
        connection.close()
        
        return [SlotSet("first_name", None), SlotSet("last_name", None)]
class ActionDefaultFallback(Action):
    def name(self) -> str:
        return "action_default_fallback"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Désolé, je ne comprends pas cette question. Pouvez-vous reformuler ou poser une question sur les filières, les modules, ou les enseignants ?")
        return []