tools = """
{
    {
        Action: get_locations,
        Description: Used whenever the question involves location of any sort,
        {
            Argument: locations,
            Description: A comma-separated list of the locations the user is asking for,
        },
        Required arguments: [location],
    },
    {
        Action: get_schedule,
        Description: Returns the schedule for the specified timespan,
        {
            Argument: timespan,
            Description: The timespan the user want to know the schedule of,
        },
        Required arguments: [timespan],
    },
}
"""

examples = """
Question: Where can can I find Alba Nova and B25?
Thought: In order to provide the user the location of Alba Nova and B25 we have to call the function get_locations with correct arguments
Action: get_locations[Alba Nova,B25]
Observation: 
[Alba Nova](https://www.google.com/maps/place/59.35393306147455,18.057654294803914)
[B25](https://www.google.com/maps/place/59.35151479446071,18.068663853571927) (Floor 3)
Thought: I have the answer
Final Answer: 
[Alba Nova](https://www.google.com/maps/place/59.35393306147455,18.057654294803914)
[B25](https://www.google.com/maps/place/59.35151479446071,18.068663853571927) (Floor 3)
Question: What is happening on 13th October?
Thought: In order to tell the user what happens on 13th October we first need to get the schedule for that day by calling get_schedule. We can then use that information answer the question
Action: get_schedule[13th October]
Observation:
date,start,end,activity,course,rooms
2023-10-13,08:00,10:00,Partial Exam/Quiz,SG1113,"V23,V32-33,W25,W37"
2023-10-13,13:00,15:00,Exercise,SF1683,"V11,V21-22"
2023-10-13,15:00,17:00,Math help session,SI1146,FB52
Thought: I have the answer
Final Answer: 
Schedule:

2023-10-13:
08:00-10:00 - Partial Exam/Quiz
   Course: SG1113
   Rooms: V23, V32-33, W25, W37

13:00-15:00 - Exercise
   Course: SF1683
   Rooms: V11, V21-22

15:00-17:00 - Math help session
   Course: SI1146
   Room: FB52
"""

sql_template = """
Du är expert på SQL och din uppgift är att hämta de relevanta raderna utifrån användarens önskemål.

SQL tabellen har följande kolumner: Startdatum,Starttid,Sluttid,Aktivitet,Kurskod,Lokal

Startdatum definieras: YYYY-MM-DD
Starttid och Sluttid definieras: XX:YY
"""