from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from googleapiclient.discovery import build
import os

# Load environemt variables
load_dotenv()

# Wikipedia tool
def wikipedia_tool(query: str):
    # This tool searches wikipedia and returns the summary of the first resukt
    from wikipedia import summary
    try:
        return summary(query, sentences=2)
    except:
        return "I couldn't find any information on that."

def google_search_tool(query: str):
    # Search google using the custom search API
    try:
        # Get variables from env file (api key and search engine id)
        api_key = os.environ["GOOGLE_SEARCH_API_KEY"]
        search_engine_id = os.environ["GOOGLE_SEARCH_ENGINE_ID"]

        # Create service with name, version, and develpoer key props
        service = build("customsearch", "v1", developerKey=api_key)

        # REsult takes in query, engine id, and number of results
        result = service.cse().list(
            q=query,
            cx=search_engine_id,
            num=1
        ).execute()

        # Seeing if there are items in results, if so set up empty list 
        # and append desired formatted results to list
        if "items" in result:
            formatted_result = []
            for item in result["items"]:
                formatted_result.append(
                    f"Title: {item['title']}\n"
                    f"Link: {item['link']}\n"
                    f"Snippet: {item['snippet']}\n"
                )
            return "\n\n".join(formatted_result)
        else:
            return "No results found..."
    except Exception as e:
        return f"Error performing search: {str(e)}"


# List of tools the agent can use
tools = [
    Tool(
        name="GoogleSearchTool",
        func=google_search_tool,
        description="Useful when you need to find information on any topic."
    ),
    Tool(
        name="wikipediaTool",
        func=wikipedia_tool,
        description="Useful for when you need to know information about a topic."
    )
]

# Load the JSON chat prompt from the hub
prompt = hub.pull("hwchase17/structured-chat-agent")

# Create out ChatOpenAI model
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

# Create a structured chat agent with conversational buffer memory
memory = ConversationBufferWindowMemory(k=3, memory_key="chat_history", return_messages=True)
agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)

# The agent executor is responsible for managing the interaction between the user input,
# the agent, and the tools
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    memory=memory,
    handle_parsing_errors=True,
    verbose=False
)

# Initial system message to set the context for the chat
initial_system_message = """
You are a helpful AI assistant that can provide helpful responses using the 
available tools. Your task is to provide step-by-step instructions based on the user's input,
for example, if the user asks you to write a sales sequence targeting homeowners in Los Angeles, CA,
the sequence you generate would look something like this: 
Step 1: Hi 'owners first name', I've been keeping up with the news in LA. 
I hope you and your family are safe. let usknow if we canhelp in any way.
Step 2: I work at 'company name here', we release a new government aid program for homeowners
affected by the wildfires. Up to $2 million in aid. Let me know if you'd like to learn more.
Step 3: Also, it's a fully government supported program. No cost or burden to you whatsoever.
Let me know!
If you are unable to answer, just say you don't know.
"""

# Add the system message to the conversation memory
memory.chat_memory.add_message(SystemMessage(content=initial_system_message))

def chat_with_bot(user_input: str):
    print(f"Chat bot received input: {user_input}")
    
    # Add the user's message to the conversation memory
    memory.chat_memory.add_message(HumanMessage(content=user_input))

    try:
        print("Getting response from agent...")
        # Get the response from the agent
        response = agent_executor.invoke({"input": user_input})
        print(f"Raw agent response: {response}")
        
        # Extract the final response from the agent's output
        if isinstance(response, dict):
            response_text = response.get("output", "")
        else:
            response_text = str(response)
            
        print(f"Extracted response text: {response_text}")
            
        # Clean up the response to remove any agent thoughts or internal processing
        if "Thought:" in response_text:
            response_text = response_text.split("Final Answer:")[-1].strip()
        elif "Final Answer:" in response_text:
            response_text = response_text.split("Final Answer:")[-1].strip()
            
        if not response_text:
            print("No response text generated")
            return "Sorry, I couldn't generate a response."
            
        print(f"Final cleaned response: {response_text}")
        # Add the AI's response to the conversation memory
        memory.chat_memory.add_message(AIMessage(content=response_text))
        return response_text
        
    except Exception as e:
        print(f"Error in chat_with_bot: {str(e)}")
        return "Sorry, there was an error processing your request."
