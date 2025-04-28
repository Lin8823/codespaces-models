import os
import json
import random
import asyncio
from openai import OpenAI
from autogen.agentchat import register_function
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import StructuredMessage, TextMessage
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_core.models import SystemMessage, UserMessage
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient, OpenAIChatCompletionClient
from pydantic import BaseModel


with open("profile.json", "r") as file:
    profiles = json.load(file)
    random_index = random.randint(0, len(profiles) - 1)
    random_profile = profiles[random_index]

client = OpenAIChatCompletionClient(
    model="gpt-4o", 
    api_key=os.environ["GITHUB_TOKEN"], 
    base_url="https://models.inference.ai.azure.com"
)


sys_messages = """
    You are a professional nutritional manager.  
    1. Recommend a nutritionally balanced meal tailored to the user's age, gender, height, weight, activity level, disease history, dietary record and sleep condition.
    2. Provide three meal options formatted as a JSON menu, clearly listing the food items, calorie count for each item, and the total calorie count for the meal options. Exclude additional descriptors such as "choice" or "option" in the meal names. Ensure the structure is clear and accurate.  
    3. Base the menu recommendations on the time specified by the user. If no time is provided, default to the current time. Ensure the recommendations align with appropriate food choices for that time of day. If it is not a suitable time for eating, notify the user and offer guidance.  
    4. For users with chronic diseases, cancer, or other medical conditions, ensure the menu accounts for their specific dietary needs by recommending foods that support their condition and avoiding any that may exacerbate it.  
    5. Provide additional dietary advice, such as portion control, nutrition_considerations that enhance nutrient absorption.
    6. If the user requests to change the menu, avoid recommending any options that were previously provided and stored in memory.
    7. If possible, identify nearby restaurants serving meals similar to the recommended menus based on the user’s location and provide the name and details of the closest restaurant.  
    8. Always return True to new_menu.

    The following JSON data is user's profile:
    {profile}
""".format(profile=json.dumps(random_profile))

response = None

class FoodItem(BaseModel):
    food: str
    calories: int
class MealOption(BaseModel):
    menu_name: str
    item: list[FoodItem]
    total_calories: int
class NutritionConsiderations(BaseModel):
    calorie_target: int
    sodium_limit: str
    fiber_goal: str
    protein_focus: str
    note: str
class MealRecommender(BaseModel):
    meal_time: str
    meal_options: list[MealOption]
    nutrition_considerations: NutritionConsiderations
    dietary_advice: str
    new_menu: bool


async def get_dietary_data(query: str) -> str:
    """Get User dietary data."""
    return "Average daily intake of 1300 calories in the past week."
async def get_sleep_data(query: str) -> str:
    """Get User sleep data."""
    return "Average 7 hours of sleep per day in the past week."


async def save_recommendation_to_memory(meal_options):
    """Save recommendation to memory."""
    for meal_option in meal_options:
        await user_memory.add(MemoryContent(content=meal_option, mime_type=MemoryMimeType.TEXT))

dietary_tool = FunctionTool(
    get_dietary_data,
    description="Get dietary condition.",
    strict=True
)
sleep_tool = FunctionTool(
    get_sleep_data,
    description="Get sleep condition.",
    strict=True
)

user_memory = ListMemory()
meal_recommender_agent = AssistantAgent(
    name="MealRecommender",
    description="A helpful assistant that can manage diet.",
    system_message=sys_messages,
    output_content_type = MealRecommender,
    tools=[dietary_tool, sleep_tool],
    memory=[user_memory],
    model_client=client
)




async def run_agents():
    try:
        response = await meal_recommender_agent.on_messages(
            [TextMessage(content="Please recommend a meal plan.", source="user")],
            cancellation_token=CancellationToken(),
        )
        meal_options = (json.loads((response.chat_message.content).json())).get("meal_options")
        print(f"Response received: {meal_options}")

        # meal_option = [{'menu_name': 'Grilled Salmon Salad', 'item': [{'food': 'Grilled Salmon', 'calories': 250}, {'food': 'Mixed Green Salad with Olive Oil Dressing', 'calories': 150}, {'food': 'Quinoa', 'calories': 200}], 'total_calories': 600}, {'menu_name': 'Lentil Soup with Whole Grain Bread', 'item': [{'food': 'Lentil Soup', 'calories': 300}, {'food': 'Whole Grain Bread', 'calories': 150}, {'food': 'Steamed Broccoli', 'calories': 100}], 'total_calories': 550}, {'menu_name': 'Grilled Chicken Wrap', 'item': [{'food': 'Grilled Chicken Breast', 'calories': 200}, {'food': 'Whole Wheat Tortilla', 'calories': 150}, {'food': 'Vegetable Mix with Avocado', 'calories': 200}], 'total_calories': 550}]
        # meal_option = [{'menu_name': 'Mediterranean Lentil Salad', 'item': [{'food': 'Cooked lentils', 'calories': 180}, {'food': 'Diced cucumbers', 'calories': 8}, {'food': 'Chopped parsley', 'calories': 5}, {'food': 'Crumbled feta cheese', 'calories': 80}, {'food': 'Olive oil and lemon dressing', 'calories': 50}], 'total_calories': 323}, {'menu_name': 'Turkey and Hummus Roll-Ups', 'item': [{'food': 'Whole wheat tortillas', 'calories': 150}, {'food': 'Sliced turkey breast', 'calories': 90}, {'food': 'Hummus', 'calories': 70}, {'food': 'Spinach leaves', 'calories': 10}], 'total_calories': 320}, {'menu_name': 'Quinoa and Black Bean Bowl', 'item': [{'food': 'Cooked quinoa', 'calories': 120}, {'food': 'Black beans', 'calories': 114}, {'food': 'Diced tomatoes', 'calories': 20}, {'food': 'Chopped avocados', 'calories': 80}, {'food': 'Fresh lime juice', 'calories': 10}], 'total_calories': 344}]
        # meal_option = [{'menu_name': 'Tofu and Stir-Fry Vegetables', 'item': [{'food': 'Firm tofu (grilled)', 'calories': 120}, {'food': 'Stir-fried mixed vegetables (broccoli, carrots, peppers)', 'calories': 85}, {'food': 'Soy sauce (low sodium)', 'calories': 15}, {'food': 'Brown rice', 'calories': 215}], 'total_calories': 435}, {'menu_name': 'Grilled Salmon with Steamed Vegetables', 'item': [{'food': 'Grilled salmon fillet', 'calories': 200}, {'food': 'Steamed asparagus', 'calories': 20}, {'food': 'Steamed baby carrots', 'calories': 35}, {'food': 'Quinoa', 'calories': 110}], 'total_calories': 365}, {'menu_name': 'Vegetable Chickpea Curry', 'item': [{'food': 'Cooked chickpeas', 'calories': 180}, {'food': 'Sautéed spinach', 'calories': 85}, {'food': 'Curry sauce (light)', 'calories': 100}, {'food': 'Basmati rice', 'calories': 205}], 'total_calories': 570}]

        for meal_option in meal_options:
            await user_memory.add(MemoryContent(content=meal_option, mime_type=MemoryMimeType.TEXT))
        # print("Recommendation saved to memory.")
        # print(user_memory.content)

        # await Console(
        #     meal_recommender_agent.on_messages_stream(
        #         [TextMessage(content="Please recommend a meal plan.", source="user")],
        #         cancellation_token=CancellationToken(),
        #     ),
        #     output_stats=True,
        # )
        return meal_options
    except Exception as e:
        print(f"Error in run_agents: {e}")  # 增加日誌
        raise

# asyncio.run(run_agents())