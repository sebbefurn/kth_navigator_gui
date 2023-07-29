import openai
import json
import pandas as pd
import datetime
import re
from Levenshtein import distance
from api.models import TextBlock, User
import math

# OpanAI setup
openai.api_key_path = "/home/anon/.secret"
llm3 = "gpt-3.5-turbo"
llm4 = "gpt-4-0613"

functions=[
{
"name": "get_locations",
"description": "Provides directions to multiple locations",
"parameters": {
    "type": "object",
    "properties": {
        "locations": {
            "type": "array",
            "description": "The locations to provide directions for",
            "items": {
                "type": "string"
            }
        }
    },
    "required": ["locations"]
}},
{
"name": "get_schedule",
"description": "Provides the schedule within a time span",
"parameters": {
    "type": "object",
    "properties": {
        "start_date": {
            "type": "string",
            "description": "The start of the time span to retrieve the schedule from",
        },
        "end_date": {
            "type": "string",
            "description": "The end of the time span to retrieve the schedule from",
        }
    },
    "required": ["start_date","end_date"]
}}]

system_template = f"""
You are an assistant at the university of KTH and your task is to help students navigate campus and interpret their schedule in a serious manner.
Your abilities are that you can read their schedule and provide them with directions to different buildings, rooms and parks around campus.
Be as short and concise as possible in your answers and stick to your task, and if you're not sure about something you should say so. 
The current date is {datetime.date.today()}
"""
"""
user_question = "Where can I find E, V and B12?"

messages = []
messages.append({"role": "system", "content": system_template})
messages.append({"role": "user", "content": user_question})

response = openai.ChatCompletion.create(
    model=llm4,
    messages=messages,
    functions=functions,
    function_call="auto"
).choices[0].message

print(response)
function_name = response['function_call']['name']
function_arguments = response.to_dict()['function_call']['arguments']
function_arguments = json.loads(function_arguments)['locations']

print(function_name)
print(function_arguments)
function_name = eval(function_name)
print(function_name(function_arguments))
exit()
"""

# Test if user asked for specific place with regex
def test_name(name, location):
    name = name.lower()
    location = location.lower()
    test1 = location.replace('-', '')
    test2 = location.replace('-', ' ')

    match1 = re.search(f"(?:^|\s)({name})(?=\s|$)", test1)
    match2 = re.search(f"(?:^|\s)({name})(?=\s|$)", test2)
    if (match1 or match2):
        return True
    else:
        return False

def get_location(location):
    # Check the regex-places
    df = pd.read_csv("./chatbot/Data/regex_places.csv", delimiter='|')
    for i in df.iterrows():
        name = i[1][0]
        floor = i[1][3]
        if test_name(name, location) == True:
            coordinates = i[1][1]
            ret = f"[{location},({coordinates}),"
            if floor != "None" and not math.isnan(floor):
                ret += f"{int(floor)}]"
            else:
                ret += f"None]"
            # Do some more stuff with coordinates
            # print(coordinates)
            return ret

    # Check the levenshtein-places
    df = pd.read_csv("./chatbot/Data/levenshtein_places.csv", delimiter='|')
    coordinate_list = []
    best_score = -1
    tracker = -1
    for index, i in enumerate(df.iterrows()):
        name = i[1][0]
        coordinates = i[1][1]
        floor = i[1][3]
        coordinate_list.append([name, coordinates, floor])
        score = distance(location, name)
        if (score < best_score or best_score == -1):
            best_score = score
            tracker = index 

    best_guess = coordinate_list[tracker]
    ret = f"[{best_guess[0]},({best_guess[1]}),"
    if best_guess[2] != "None" and not math.isnan(best_guess[2]):
        ret += f"{int(best_guess[2])}]"
    else:
        ret += f"None]"
    # Do some stuff with coordinates
    #print(best_guess)
    return ret

# The callable functions
def get_locations(locations):
    ans = []
    for location in locations:
        ans.append(get_location(location))
    return "\n".join(ans)

def format_date(timespan):
    current_date = datetime.date.today()
    prompt = f"""
    The current date is {current_date} and I will provide you with a timespan that I want you to transform into a start-date and and end-date. The dates you output should be in the format xxxx-xx-xx and make sure to think step by step when calculating the dates.

    Here is an example so you understand better:
    EXAMPLE CURRENT DATE: 2023-07-14
    EXAMPLE INPUT: next week
    EXAMPLE OUTPUT: 2023-07-17,2023-07-23
    EXAMPLE INPUT: between 27th september and 30th september
    EXAMPLE OUTPUT: 2023-09-27,2023-09-30

    INPUT: {timespan}
    OUTPUT:
    """
    response = openai.ChatCompletion.create(
        model=llm4,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    date_ans = response["choices"][0]["message"]["content"]

    return date_ans


def make_location_list(rooms):
    df = pd.read_csv("/home/anon/Code/Other/test/chatbot/Data/regex_places.csv", delimiter='|')
    ret = []
    check = []
    for i in df.iterrows():
        name = str(i[1][0]).strip()
        if name in rooms:
            coordinates = i[1][1]
            ret.append(f"[{name}]({coordinates})")
            check.append(name)

    for i in rooms:
        if i.strip() not in check:
            ret.append(i)


    return ret

def get_schedule(arr):
    start, end, grade = arr
    start = start.strip()
    end = end.strip()
    activities = []
    print(f"start: {start}, end: {end}")

    start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end, "%Y-%m-%d")

    if (end_date - start_date).days > 20:
        return "Ditt tidsspann är för långt. Det måste vara mindre än 20 dagar."
    elif end_date > datetime.datetime.strptime("2024-01-15", "%Y-%m-%d"):
        return "Schemat är avkapat vid 15th January 2024."

    ans = ""
    with open(f"./chatbot/Data/tefy_schedule_s{grade}.csv") as file:
        ans += file.readline()
        print(grade)
        for line in file.readlines():
            try:
                template_date = datetime.datetime.strptime(line[0:10], "%Y-%m-%d")
            except:
                continue
            if "Begin" in line or start_date <= template_date <= end_date:
                ans += line
    
    if ans.strip() == "Startdatum,Starttid,Sluttid,Aktivitet,Tillfälleskod/kurskod,Lokal":
        return f"Det verkar inte vara några aktiviteter mellan {start} och {end}"
    print(f"schedule: {ans}")
    return ans

def get_microwaves():
    # Read data from microwave file and just return it pretty much
    pass

def get_role(role):
    if role == 1:
        return "user"
    else:
        return "assistant"

def main(user_id, grade):
    messages = [
        {"role": "system", "content": system_template},
    ]

    # Gets the chatlog for the specified user with and id of user_id
    text_blocks = TextBlock.objects.filter(user=user_id).order_by('created_at')
    start = max(0, len(text_blocks)-4)
    text_blocks = text_blocks[start:]

    # Adds the chatlog to 'messages'
    for text_block in text_blocks:
        role = get_role(text_block.is_user)
        content = text_block.text
        messages.append({"role": role, "content": content})

    response = openai.ChatCompletion.create(
        model=llm4,
        messages=messages,
        functions=functions,
        function_call="auto"
    ).choices[0].message
    response_text = response['content']

    if response_text != None:
        # Didn't return a function
        return response_text

    # Did return a function
    # Parses function name and arguements
    function_name = response['function_call']['name']
    function_arguments = response.to_dict()['function_call']['arguments']
    function_arguments = json.loads(function_arguments)

    if function_name == 'get_locations':
        function_arguments = function_arguments['locations']
    else:
        function_arguments = [function_arguments['start_date'], function_arguments['end_date'], grade]

    function_name = eval(function_name)
    func_response = function_name(function_arguments)

    return func_response

