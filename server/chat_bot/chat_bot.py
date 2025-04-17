from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

# Load environemt variables
load_dotenv()

# Wikipedia tool
def wikipedia_tool(query):
    # This tool searches wikipedia and returns the summary of the first resukt
    from wikipedia import summary
    try:
        return summary(query, sentences=2)
    except:
        return "I couldn't find any information on that."

# List of tools the agent can use
tools = [
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
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)

# The agent executor is responsible for managing the interaction between the user input,
# the agent, and the tools
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    memory=memory,
    handle_parsing_errors=True,
    verbose=False  # Set verbose to False to suppress intermediate thoughts
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
    # Add the user's message to the conversation memory
    memory.chat_memory.add_message(HumanMessage(content=user_input))

    try:
        # Get the response from the agent
        response = agent_executor.invoke({"input": user_input})
        
        # Extract the final response from the agent's output
        if isinstance(response, dict):
            response_text = response.get("output", "")
        else:
            response_text = str(response)
            
        # Clean up the response to remove any agent thoughts or internal processing
        if "Thought:" in response_text:
            response_text = response_text.split("Final Answer:")[-1].strip()
        elif "Final Answer:" in response_text:
            response_text = response_text.split("Final Answer:")[-1].strip()
            
        if not response_text:
            return "Sorry, I couldn't generate a response."
            
        # Add the AI's response to the conversation memory
        memory.chat_memory.add_message(AIMessage(content=response_text))
        return response_text
        
    except Exception as e:
        print(f"Error in chat_with_bot: {str(e)}")
        return "Sorry, there was an error processing your request."
