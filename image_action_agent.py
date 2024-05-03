import google.generativeai as genai
from PIL import Image
import os
from urlextract import URLExtract
from retry import retry
import traceback
import logging

from langchain_community.agent_toolkits import MultionToolkit
from multion.client import MultiOn

logging.basicConfig(level=logging.INFO)

from prompts import EXTRACT_URL_PROMPT, \
    IMAGE_TO_ACTION_PROMPT_Pt1, IMAGE_TO_ACTION_PROMPT_Pt2, EXAMPLE_IMAGE, \
    EXTRACT_RELEVANT_INFO_FROM_IMAGE_Pt1, EXTRACT_RELEVANT_INFO_FROM_IMAGE_Pt2, \
    CREATE_INSTRUCTIONS_WITH_CONTEXT, \
    COMBINE_INSTRUCTIONS_PROMPT

from dotenv import load_dotenv
load_dotenv()

IS_LOCAL = os.getenv('LOCAL')
if IS_LOCAL == "TRUE":
    LOCAL=True
else:
    LOCAL=False

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
MULTION_API_KEY = os.getenv('MULTION_API_KEY')

genai.configure(api_key=GOOGLE_API_KEY)
vision_model = genai.GenerativeModel('gemini-pro-vision')
text_model = genai.GenerativeModel('gemini-pro')

multion_client = MultiOn(api_key=MULTION_API_KEY)

def run_agent(image_path, instructions, command_history):
    """Run the agent with the given image and instructions."""
    
    command1, command2, command = parse_intent3(image_path, instructions)
    command += "\n Do the above task with no pauses or further human input."
    command_history.append(f"Extracted Instructions: {command}")

    try:
        url = parse_url(command)
        command_results, final_status = run_multion(command, command_history, url)
        if final_status != "DONE":
            logging.info(f"Final status was {final_status}.")
            raise ValueError(f"Final status was {final_status}.")
        return command_results, final_status
    except Exception as e:  # TODO: overly broad exception
        logging.info(traceback.format_exc())
        command_history.append(f"ERROR: {str(e)}")
        command_history.append("Retrying with command: {command1}")
        url = parse_url(command1)
        return run_multion(command1, command_history, url)

def run_multion(command, command_history, url):
    """Run the multion session with the given command and url."""
    session_id = start_session(url, LOCAL)
    
    continuing = True
    while continuing:
        response = step_session(session_id, command, url)
        continuing = (response.status in ['CONTINUE', 'PAUSED'])
        logging.info(response.status)
        logging.info(response.message)
        command_history.append(f"STATUS: {response.status}, MESSAGE: {response.message}")
    
    final_status = response.status
    close_session_response = multion_client.sessions.close(session_id=session_id)
    logging.info("close_session_response: ", close_session_response)

    return command_history, final_status


@retry(exceptions=TimeoutError, tries=3, delay=1, backoff=2, logger=None)
def step_session(session_id, command, url):
    """Step the multion session with the given command and url."""
    response = multion_client.sessions.step(
        session_id = session_id,
        cmd=command,
        url=url
    )
    return response

@retry(exceptions=TimeoutError, tries=3, delay=1, backoff=2, logger=None)
def start_session(url, local):
    """Start the multion session with the given url. Run locally if local."""
    create_session_response = multion_client.sessions.create(
        url=url,
        local=LOCAL
    )
    session_id = create_session_response.session_id
    logging.info(create_session_response.status)
    logging.info(create_session_response.message)
    return session_id

@retry(exceptions=ValueError, tries=3, delay=1, backoff=2, logger=None)
def parse_intent(image_path, instructions):
    """Parse the intended instruction from the given image and instructions."""
    # Load the image with PIL
    image = Image.open(image_path)

    # Generate a response using the model
    full_prompt = [IMAGE_TO_ACTION_PROMPT_Pt1, 
                   EXAMPLE_IMAGE, 
                   IMAGE_TO_ACTION_PROMPT_Pt2.format(instructions=instructions),
                   image]
    response = vision_model.generate_content(full_prompt)
    response.resolve()

    logging.info(response.text)
    return response.text

@retry(exceptions=ValueError, tries=3, delay=1, backoff=2, logger=None)
def parse_image_context(image_path, instructions):
    """Parse the relevant context from the given image based on the instructions."""
    # Load the image with PIL
    image = Image.open(image_path)

    # Generate a response using the model
    full_prompt = [EXTRACT_RELEVANT_INFO_FROM_IMAGE_Pt1, 
                   EXAMPLE_IMAGE, 
                   EXTRACT_RELEVANT_INFO_FROM_IMAGE_Pt2.format(instructions=instructions),
                   image]
    response = vision_model.generate_content(full_prompt)
    response.resolve()

    logging.info(response.text)
    return response.text

@retry(exceptions=ValueError, tries=3, delay=1, backoff=2, logger=None)
def parse_intent2(image_path, instructions):
    """Parse the intended instruction from the given image and instructions."""
    context = parse_image_context(image_path, instructions)
    full_prompt = [CREATE_INSTRUCTIONS_WITH_CONTEXT.format(context=context, instructions=instructions)]

    response = text_model.generate_content(full_prompt)

    logging.info(response.text)
    return response.text

@retry(exceptions=ValueError, tries=3, delay=1, backoff=2, logger=None)
def combine_intents(command1, command2):
    """Combine the two command versions into one."""
    full_prompt = [COMBINE_INSTRUCTIONS_PROMPT.format(instructions1=command1, instructions2=command2)]
    response = text_model.generate_content(full_prompt)

    logging.info(response.text)
    return response.text

def parse_intent3(image_path, instructions):
    """Parse the intended instruction from the given image and instructions using the two different parse patterns"""
    # combines both parse_intent1 and parse_intent2
    command1 = parse_intent(image_path, instructions)
    command2 = parse_intent2(image_path, instructions)
    command = combine_intents(command1, command2)
    return command1, command2, command


@retry(exceptions=ValueError, tries=3, delay=1, backoff=2, logger=None)
def parse_url(task_instructions):
    """Determine the URL to start at from the given task instructions."""
    full_prompt = EXTRACT_URL_PROMPT.format(task_instructions=task_instructions)
    response = text_model.generate_content([full_prompt])
    response.resolve()

    logging.info(response.text)
    extractor = URLExtract()
    try:
        url = extractor.find_urls(response.text)[0]
    except IndexError:
        raise ValueError("No URL found in response.")
    return url

if __name__ == "__main__":
    run_agent("example.jpg", "Please schedule this call on my google calendar.")

