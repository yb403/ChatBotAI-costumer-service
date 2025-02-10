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

        #dispatcher.utter_message(text=f"The available sectors are: {', '.join(sectors)}")
        #dispatcher.utter_message(text=f"Les filières disponibles sont : {', '.join(sectors)}")
        dispatcher.utter_message(text=f"Les filières disponibles sont :  \n-" + "\n-".join(sectors) + ".")

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
            #dispatcher.utter_message(text=f"The semesters in {sector} are: {', '.join(semesters)}.")
            #dispatcher.utter_message(text=f"Les Semesters dans {sector} sont : {', '.join(semesters)}.")
            dispatcher.utter_message(text=f"Les Semesters dans {sector} sont :  \n-" + "\n-".join(semesters) + ".")
        else:
            #dispatcher.utter_message(text=f"No semesters found for the sector {sector}.")
            dispatcher.utter_message(text=f"Aucun Semester trouvé pour le filière {sector}.")
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

        # Validate inputs
        if not sector:
            dispatcher.utter_message(text="Please specify the sector.")
            return []

        # Connect to the database
        import mysql.connector

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="chatbot"
            )
            cursor = conn.cursor()

            # If semester is provided, fetch specific modules for that semester in the sector
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
                # If semester is not provided, fetch all modules for the sector
                query = """
                SELECT DISTINCT Module.name 
                FROM Module
                JOIN Semester ON Module.semester_id = Semester.id
                JOIN Sector ON Semester.sector_id = Sector.id
                WHERE Sector.name LIKE %s
                """
                cursor.execute(query, (f"%{sector}%",))

            # Retrieve modules
            modules = [row[0] for row in cursor.fetchall()]
        except mysql.connector.Error as e:
            dispatcher.utter_message(text=f"Une erreur est survenue lors de l'accès à la base de données : {str(e)}")
            
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        # Respond to the user
        if modules:
            if semester:
                #dispatcher.utter_message(text=f"The modules in {semester} for {sector} are: {', '.join(modules)}.")
                #dispatcher.utter_message(text=f"Les modules dans {semester} pour {sector} sont : {r'\n-'.join(modules)}.")
                dispatcher.utter_message(text=f"Les modules dans {semester} pour {sector} sont:  \n-" + "\n-".join(modules) + ".")

            else:
                #dispatcher.utter_message(text=f"The modules in {sector} are: {', '.join(modules)}.")
                #dispatcher.utter_message(text=f"Les modules dans {sector} sont : {', '.join(modules)}.")
                dispatcher.utter_message(text=f"Les modules dans {sector} sont :  \n-" + "\n-".join(modules) + ".")



        else:
            if semester:
                #dispatcher.utter_message(text=f"No modules found for {semester} in {sector}.")
                dispatcher.utter_message(text=f"Aucun module trouvé pour {semester} dans {sector}.")

            else:
                dispatcher.utter_message(text=f"Aucun module trouvé dans {sector}.")

        return []


class ActionListElements(Action):
    def name(self) -> Text:
        return "action_list_elements"

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
                        dispatcher.utter_message(text="Please specify the module.")
                        return []

        
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chatbot"
        )
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
            #dispatcher.utter_message(text=f"The elements in {module} are: {', '.join(elements)}.")
            
            dispatcher.utter_message(text=f"Les éléments dans {module} sont :  \n-" + "\n-".join(elements) + ".")

        else:
            #dispatcher.utter_message(text=f"No elements found for the module {module}.")
            dispatcher.utter_message(text=f"Aucun élément trouvé pour le module {module}.")

        if sector != None:
            return [SlotSet("sector", sector)]
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
            #dispatcher.utter_message(text=f"The teacher for {element} is {fname} {lname}.")
            dispatcher.utter_message(text=f"Le professeur pour {element} est {fname} {lname}.")

        else:
            #dispatcher.utter_message(text=f"I couldn't find a teacher for the element {element}.")
            dispatcher.utter_message(text=f"Je n'ai pas trouvé de professeur pour l'élément {element}.")
        return [SlotSet("element", element)]


class ActionProvideProfessorEmail(Action):
    def name(self) -> str:
        return "action_provide_professor_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: "Tracker",
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        first_name = tracker.get_slot("first_name")
        last_name = tracker.get_slot("last_name")
        print(first_name,last_name)
        if not first_name and not last_name:
            dispatcher.utter_message(text="Pouvez-vous me donner au moins le prénom ou le nom de famille du professeur ?")
            return []
        
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chatbot"
        )
        cursor = connection.cursor()

        # Build the query based on available information
        query = "SELECT email FROM Teacher WHERE"
        conditions = []
        params = []

        if first_name:
            conditions.append(" fname LIKE %s")
            params.append(f"%{first_name}%")  # Add wildcards for partial matches

        if last_name:
            conditions.append(" lname LIKE %s")
            params.append(f"%{last_name}%")  # Add wildcards for partial matches

        query += " AND".join(conditions)
        print(query)
        cursor.execute(query, tuple(params))
        result = cursor.fetchone()
        
        if result:
            email = result[0]
            dispatcher.utter_message(text=f"L'email de ce professeur est : {email}")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas trouvé l'email de ce professeur.")
        
        cursor.close()
        connection.close()
        
        return []
class ActionDefaultFallback(Action):
    def name(self) -> str:
        return "action_default_fallback"

    async def run(self, dispatcher, tracker, domain):
        # Cette partie peut être modifiée selon ce que vous voulez que l'action fasse
        dispatcher.utter_message(text="Désolé, je n'ai pas bien compris. Pouvez-vous reformuler ?")
        return []