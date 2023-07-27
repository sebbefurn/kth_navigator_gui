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

system_template = """
Here are the actions you have access to along with a description of each one so you know when to use them:
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

I will give you a question and I want you to go about answering my question in a very specific way following this system:
Question: My question to you
Thought: You will think about the question and think step by step on how to find the information needed to answer the question based on the actions you have available
Action: You will now decide which action to take next based on your plan and provide arguments within square-brackets
Observation: The result of the action
(This Thought, Action, Observation can repeat 6 times and needs to happen at least once. If none of the available actions seem relevant I want your answer to be: 'Couldn't find relevant action to your question')
Thought: I have the answer
Final Answer: The final answer to the original question


EXAMPLES (Just to show the thought pattern, all information here is fabricated):
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

You are an assistant for KTH and your mission is to help students interpret their schedule and navigate campus.
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
    df = pd.read_csv("/home/anon/Code/Other/test/chatbot/Data/regex_places.csv", delimiter='|')
    for i in df.iterrows():
        name = i[1][0]
        floor = i[1][3]
        print(f"name: {name}, floor: {floor}")
        if test_name(name, location) == True:
            coordinates = i[1][1]
            ret = f"[{location}]{coordinates}"
            if floor != "None" and not math.isnan(floor):
                ret += f" (Floor {int(floor)})"
            # Do some more stuff with coordinates
            # print(coordinates)
            return ret

    # Check the levenshtein-places
    df = pd.read_csv("/home/anon/Code/Other/test/chatbot/Data/levenshtein_places.csv", delimiter='|')
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
    ret = f"[{best_guess[0]}]{best_guess[1]}"
    if best_guess[2] != "None" and not math.isnan(best_guess[2]):
        ret += f" (Floor {int(best_guess[2])})"
    # Do some stuff with coordinates
    #print(best_guess)
    return ret

# The callable functions
def get_locations(locations):
    locations = locations.split(",")
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


def calculate_week_number(week_string):
    # Retrieve current week number in case week_string is relative
    current_week = datetime.date(datetime.year, datetime.data.month, datetime.data.day).isocalendar().week
    prompt = f"""
    The current week is {current_week} and I want you to tell me the week number that the user refers to, and make sure that your answer is an integer.

    Here is an example so you understand better:
    EXAMPLE CURRENT WEEK: 10
    EXAMPLE INPUT: next week
    EXAMPLE OUTPUT: 11

    INPUT: {week_string}
    OUTPUT:
    """
    response = openai.ChatCompletion.create(
        model=llm4,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    week_nr = response["choices"][0]["message"]
    try:
        week_nr = int(week_nr)
    except:
        print("AI did not return week as a number")
        exit()

    return week_nr

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

def get_schedule(timespan, grade):
    start, end = format_date(timespan).split(',')
    start = start.strip()
    end = end.strip()
    activities = []
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end, "%Y-%m-%d")
    if (end_date - start_date).days >= 20:
        return "Your time span is too large. You have to select a time span smaller than 20 days"
    df = pd.read_csv(f"/home/anon/Code/Other/test/chatbot/Data/tefy_schedule_s{grade}.csv", delimiter=',')
    for i in df.iterrows():
        template_date = datetime.datetime.strptime(i[1][0], "%Y-%m-%d")
        if start_date <= template_date <= end_date:
            activities.append([i[1][0], i[1][1], i[1][3], i[1][4], i[1][6], i[1][7]])
    
    answer = ""
    for activity in activities:
        rooms = make_location_list(activity[5].split(','))
        answer += f"date: {activity[0]},start: {activity[1]},end: {activity[2]},activity: {activity[3]},course: {activity[4]},room: {rooms}\n"
    if answer == "":
        return f"There are no activities happening on {timespan}"
    return answer

def get_microwaves():
    # Read data from microwave file and just return it pretty much
    pass

 
# User interaction
def call_function(message, grade):
    thought_end = message.index("Action")
    function_name_start = thought_end + len("Action: ")
    function_name_end = message.index("[")
    function_args_start = function_name_end + 1
    function_args_end = message.index("]")
    function_name = message[function_name_start:function_name_end]
    function_args = message[function_args_start:function_args_end]

    callable_function = eval(function_name)
    if function_name == "get_schedule":
        function_response = callable_function(function_args, grade)
    else:
        function_response = callable_function(function_args)

    prev_content = message[:function_args_end+2]
    prev_content += f"\nObservation: {function_response}"

    return prev_content
    
def get_role(role):
    if role == 1:
        return "user"
    else:
        return "assistant"

def main(user_id, grade):
    history = [
        {"role": "system", "content": system_template},
    ]
    safe_net = 5
    messages = TextBlock.objects.filter(user=user_id).order_by('created_at')

    message_len = len(messages)
    for i in range(message_len-1):
        print(f"is_user: {get_role(messages[i].is_user)}, content: {messages[i].text}")
        history.append({"role": get_role(messages[i].is_user), "content": messages[i].text})
    history.append({"role": get_role(messages[message_len-1].is_user), "content": "Question: "+messages[message_len-1].text})

    while(safe_net >= 0):
        safe_net -= 1
        response = openai.ChatCompletion.create(
            model=llm4,
            messages=history,
        )
        message = response["choices"][0]["message"]["content"]
        if "Final Answer" in message:
            start_end = message.index("Final Answer") + len("Final Answer: ")
            final_answer = message[start_end:]
            history.append({"role": "assistant", "content": final_answer})
            print(f"Final Answer: {final_answer}")
            return final_answer
        message = response["choices"][0]["message"]["content"]
        prev_message = call_function(message, grade)
        print(prev_message)
        history.append({"role": "assistant", "content": prev_message})

