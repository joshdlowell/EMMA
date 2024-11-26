from NewTasks import image_generation

task_list = [
    'Image Generation',
    'Video Generation',
    'Current Information',
    'Home Automation',
    'Kitchen Timer',
    'Chat',
    'Story Telling',
    'Other'
    ]

task_classifier_prompt = [
    {"role": "system",
     "content":
         "You are the system, a task classifier, you will determine which of the "
         f"tasks in the list {task_list} best fits the user's request. Your "
         "response MUST consist of only the task from the list that best fits the "
         "request. 'Kitchen Timer' is only for creating new timers, checking existing "
         "timers, and canceling existing timers."},
    {"role": "user", "content": "create an image of a kitten in the woods"},
    {"role": "system", "content": "Image Generation"},
    {"role": "user", "content": "What is the current weather in Baltimore"},
    {"role": "system", "content": "Current Information"},
    {"role": "user", "content": "are you doing today?"},
    {"role": "system", "content": "Chat"},
    {"role": "user", "content": "Where is lauren?"},
    {"role": "system", "content": "Current Information"},
    {"role": "user", "content": "Set a chicken timer for three minutes"},
    {"role": "system", "content": "Kitchen Timer"}]


conversation_prompt = [
    {"role": "system",
     "content":
         "You are David. You are a helpful assistant. Your responses will be truthful "
         "and in plain english optimized for text-to-speech. Range values should not "
         "be displayed as, for example, '5-9' or '(2-3)' but spelled out like "
         "'5 to 9' or '2 to 3' and abbreviations like kg., f., cm., lbs. should be "
         "spelled out kilograms, fahrenheit, centimeters, pounds."}]


current_info_prompt = [ # Not finished yet
    {"role": "system",
     "content":
         "You are the system, you have a list of 'actions' and a list of 'information. "
         "You will determine, based on the user content if the user's intent is to change "
         "the state of an item in the actions list.which of the "
         f"tasks in the list {task_list} best fits the user's request. Your "
         "response MUST consist of only the task from the list that best fits the "
         "request. 'Kitchen Timer' is only for creating new timers, checking existing "
         "timers, and canceling existing timers."},
    {"role": "system", "actions": ""},
    {"role": "system", "information": ""}]

image_generation_prompt = [
    {"role": "system",
         "content":
             "You are an AI artist, generate an image based on the user content"}]


def run(user_prompt, core_llm, **args):
    # core_llm = conversation.CoreLLM(args['llm_model'])
    call = core_llm.task_classifier(task_classifier_prompt, user_prompt)
    print(call)
    if call in ['Image Generation']:  # Offload GPU for other models
        del core_llm.model
        core_llm.model = None

    # Handles prompt based on task classifier response
    match call.strip():
        case 'Image Generation':
            image_llm = image_generation.ImageLLM(args['image_model'])
            msg, image = image_llm.image_generation(user_prompt)
            response = {"msg" : msg}
            if image:
                response["image"] = image
            del image_llm
        case 'Video Generation':
            # print(call)
            response = {"msg": call}  # Default, this only prompts the model to say the task
        case "Current Information" | 'Home Automation':
            # print(call)
            response = {"msg": call}  # Default, this only prompts the model to say the task
        case 'Kitchen Timer':
            # print(call)
            response = {"msg": call}  # Default, this only prompts the model to say the task
        case 'Chat' | 'Story Telling' | 'Other' | _:
            if call.strip() == 'Other':
                input(f"hit other, classification was {call.strip()}")
            response = {"msg" : core_llm.conversation(conversation_prompt, user_prompt)}

    if not core_llm.model:
        core_llm.regen()

    return response
