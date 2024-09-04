# Local LLM Agent

## Work In Progress

This Local LLM Agent is designed to run directly on your system using an OpenAI API key. Currently, it's in its early stages, with ongoing development to bring more features and improvements. Here's what the agent can do so far:

- **Develop Applications:** Build web applications and games, then save them directly on your system.
- **Code Debugging:** Analyze and debug its own code.
- **Self-Correction:** Automatically call itself, evaluate compiler outputs, and rewrite code to fix any issues.
- **Local Environment Access:** Interact with Python and CMD local environments for versatile task execution.
- **File System Interaction:** Find, update, and delete files/folders on your system, providing seamless file management.
- **Version Control Integration:** Push code directly to GitHub (Yes, you read that right!).
- **Data Analysis:** The Agent can analyze csv files and create intended graphs for intuitive data representation.
- **Internet Search Functionality:** The Agent can search the internet for real-time information to assist with tasks.

Stay tuned for more exciting features and enhancements in the near future!

## Example Output: Tic Tac Toe with Smart AI Opponent

With just a single prompt, the Local LLM Agent can create a fully functional Tic Tac Toe game featuring a smart AI opponent.

![Local LLM Agent Image](imgs/pic-1.png)

## Example Output: Clock 

With just a single prompt, the Local LLM Agent can create a fully functional clock application.

![Clock Example](imgs/pic-2.png)


## How to Use the Local LLM Agent

To start using the Local LLM Agent, follow these steps:

1. **Clone the Repository**: First, clone the repository to your local machine using the following command:
   ```bash
   git clone https://github.com/your-username/local-llm-agent.git
2. **Navigate to the Project Directory**: Move into the project directory:
   ```bash
   cd local-llm-agent
3. **Create a `.env` File**: Create a `.env` file in the root directory of the project and include your OpenAI and Preplexity(for search) API keys. The `.env` file should look like this:
   ```bash
   OPENAI_API = "your-openai-api-key"
   PERPLEXITY_API = "your-perplexity-api-key"
4. **Install Dependencies**: Install the necessary Python dependencies by running:
   ```bash
   pip install -r requirements.txt
5. **Run the Agent**: Start the agent by executing the following command:
   ```bash
   python interact_AGENT.py
6. **Interact with the Agent**: Once the agent is running, you can start interacting with it through the terminal. You can give it tasks like "Create a Tic Tac Toe game" or "Debug this piece of code," and the agent will handle everything from development to debugging and even self-correction.





