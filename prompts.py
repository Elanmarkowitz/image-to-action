
from PIL import Image

IMAGE_TO_ACTION_PROMPT_Pt1 = \
"""You are given and image and user instructions, your job is to refine the user instructions so that they contain all the information context from the image. 
You must explictly state any information about the image that is relevant to the user request.

Example: 
User instructions: Please schedule this call on my google calendar."""
EXAMPLE_IMAGE = Image.open("meeting.jpeg")
IMAGE_TO_ACTION_PROMPT_Pt2 = \
"""
Instructions: Please schedule a call with Ben today at 6pm on my google calendar. 

User instructions: {instructions}"""

EXTRACT_URL_PROMPT = \
"""What URL should I go to to first to do the following task? Given the following task to execute, return what URL is needed to complete the task. If no URL is explicitly mentioned, generate your best guess. 

e.g.
TASK INSTRUCTIONS: "Please schedule this call on my google calendar."
URL: http://calendar.google.com/

TASK INSTRUCTIONS: {task_instructions}
URL:"""

EXTRACT_RELEVANT_INFO_FROM_IMAGE_Pt1 = \
"""Describe any relevant information from or about the image that would be required to fulfill the user request. Include as much detail as possible. 

Example:
User request: Please schedule this call on my google calendar."""
# EXAMPLE_IMAGE
EXTRACT_RELEVANT_INFO_FROM_IMAGE_Pt2 = \
"""Context: The image shows an imessage conversation with Ben about scheduling a meeting. The agreed upon time is 6pm. These messages were sent today.

User request: {instructions}"""


CREATE_INSTRUCTIONS_WITH_CONTEXT = \
"""Given the contextual information and the user request, give a precise, detailed set of instructions that can be executed to fulfill the user request containing all required information.

Example:
Context: The image shows a conversation with Ben about scheduling a meeting. The agreed upon time is 6pm today.
User request: Please schedule this call on my google calendar.
Instructions: Please schedule a call with Ben today at 6pm on my google calendar. 

Context: {context}
User request: {instructions}
Instructions:"""

COMBINE_INSTRUCTIONS_PROMPT = \
"""Given two sets of instructions for the same task, combine them into a single set of instructions that contains all the necessary information from both sets.

Instructions 1: {instructions1}
Instructions 2: {instructions2}
Instructions:"""