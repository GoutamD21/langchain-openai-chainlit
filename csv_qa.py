from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_community.llms import OpenAI
from langchain_openai import OpenAI
# from langchain.llms import OpenAI
import pandas as pd
import chainlit as cl
import os
import io

# # Chainlit fetches env variables from .env automatically
# """
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()
# """


OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")
print(OPENAI_API_KEY);

# Create an OpenAI object.
llm = OpenAI()


def create_agent(data: str, llm):
    """Create a Pandas DataFrame agent."""
    return create_pandas_dataframe_agent(llm, data, verbose=False, allow_dangerous_code=True)


@cl.on_chat_start
async def on_chat_start():

    # Sending an image with the local file path
    elements = [
    cl.Image(name="image1", display="inline", path="./robot.jpeg")
    ]
    await cl.Message(content="Hello there, Welcome to AskAnyQuery related to Data!", elements=elements).send()

    files = None

    # Wait for user to upload csv data
    while files is None:
        files = await cl.AskFileMessage(
            content="Please upload a csv file to begin!", 
            accept=["text/csv"],
            max_size_mb= 100,
            timeout = 180,
        ).send()

    if not files:
        await cl.Message(content="No file was uploaded. Please try again.").send()
        return
    
    # Log the attributes of the AskFileResponse object
    file = files[0]  # Access the first file in the list
    # await cl.Message(content=f"File attributes: {dir(file)}").send()

    # # Access the file content and name
    # file_name = file.name
    # file_content = await file.read()  # Use the read method to get the content

    msg = cl.Message(content=f"Processing `{file.name}`...")
    await msg.send()
    
    df = pd.read_csv(file.path)
    
    # csv_file = io.StringIO(file.content.decode('utf-8'))
    # df = pd.read_csv(csv_file)

    # # Read csv file with pandas
    # csv_file = io.StringIO(file.content)
    # df = pd.read_csv(csv_file, encoding="utf-8")

    # creating user session to store data
    cl.user_session.set('data', df)

    # Send response back to user
    # Let the user know that the system is ready
    msg.content = f"Processing `{file.name}` done. You can now ask questions!"
    await msg.update()


@cl.on_message
async def main(message: str):

    # Get data
    df = cl.user_session.get('data')

    # Agent creation
    agent = create_agent(df, llm)

    # Run model 
    response = agent.run(message)

    # Send a response back to the user
    await cl.Message(
        content=response,
    ).send()