# from langgraph_sdk import get_client
# from langchain_core.messages import convert_to_messages
# from langchain_core.messages import HumanMessage, SystemMessage
# # Connect via SDK
# url_for_cli_deployment = "http://localhost:8123"
# client = get_client(url=url_for_cli_deployment)

# async def main():
#     thread = await client.threads.create()

#     config = {"configurable": {"user_id": "Test"}}
#     graph_name = "retrieval_graph" 
#     async for chunk in client.runs.stream(thread["thread_id"], 
#                                       graph_name, 
#                                       input={"input_data":"." },
#                                       config=config,
#                                       interrupt_before=["human_edit"],
#                                       stream_mode="messages-tuple"):
#         if chunk.event == "messages":
#             print("".join(data_item['content'] for data_item in chunk.data if 'content' in data_item), end="", flush=True)
#     print()
#     thread_state = await client.threads.get_state(thread['thread_id'])

#     # for m in convert_to_messages(thread_state['values']['messages']):
#     #     m.pretty_print()
#     # print()



#     copied_thread = await client.threads.copy(thread['thread_id'])
#     copied_thread_state = await client.threads.get_state(copied_thread['thread_id'])
#     # for m in convert_to_messages(copied_thread_state['values']['messages']):
#     #     m.pretty_print()
    
#     # Get the history of the thread
#     # states = await client.threads.get_history(thread['thread_id'])
#     # # print("---"*25)
#     # # print(states)
#     # # print("---"*25)
#     # # # Pick a state update to fork
#     # to_fork = states[-3]
#     # # # print(len(to_fork))
#     # # print(f"\nto_fork : {to_fork['values']}\n")
#     # # print("---"*25, "\n")

#     # user_input = await asyncio.to_thread(input, "Enter additional info: ")
#     # forked_input = {"human_message": user_input}

#     # # # # Update the state, creating a new checkpoint in the thread
#     # forked_config = await client.threads.update_state(
#     #     thread["thread_id"],
#     #     forked_input,
#     #     checkpoint_id=to_fork['checkpoint_id']
#     # )
#     current_human_messages = thread_state['values'].get('human_messages', [])

#     # Take user input
#     user_input = await asyncio.to_thread(input, "Enter the chages you want to make: ")

#     # Create a new human message
#     new_human_message = {
#         "content": user_input,
#         "role": "human"
#     }

#     # Append the new human message to the existing list
#     updated_human_messages = current_human_messages + [new_human_message]

#     # Prepare the update for the thread state
#     update_input = {
#         "human_messages": updated_human_messages  # Updated list of messages
#     }

#     # Update the thread state
#     forked_config = await client.threads.update_state(
#         thread["thread_id"],
#         update_input
#     )

#     async for chunk in client.runs.stream(thread["thread_id"], 
#                                       graph_name, 
#                                       input=None,
#                                       config=config,
#                                       checkpoint_id=forked_config['checkpoint_id'],
#                                       stream_mode="messages-tuple"):

#         if chunk.event == "messages":
#             print("".join(data_item['content'] for data_item in chunk.data if 'content' in data_item), end="", flush=True)


#     # # async for chunk in client.runs.stream(thread["thread_id"], 
#     # #                                   graph_name, 
#     # #                                   input=None,
#     # #                                   config=config,
#     # #                                   interrupt_before=["More_Info"],
#     # #                                   stream_mode="messages-tuple"):
#     # #     # print(chunk)
#     # #     # print("==="*25)
#     # #     if chunk.event == "messages":
#     # #         print("".join(data_item['content'] for data_item in chunk.data if 'content' in data_item), end="", flush=True)


# import asyncio

# asyncio.run(main())
from langgraph_sdk import get_client
from langchain_core.messages import convert_to_messages
from langchain_core.messages import HumanMessage, SystemMessage
import asyncio

# Connect via SDK
url_for_cli_deployment = "http://localhost:8123"
client = get_client(url=url_for_cli_deployment)

async def main():
    # Create thread
    thread = await client.threads.create()

    config = {"configurable": {"user_id": "Test"}}
    graph_name = "retrieval_graph" 

    # Initial run
    async for chunk in client.runs.stream(
        thread["thread_id"], 
        graph_name, 
        input={"input_data":"." },
        config=config,
        interrupt_before=["human_edit"],
        stream_mode="messages-tuple"
    ):
        if chunk.event == "messages":
            print("".join(data_item['content'] for data_item in chunk.data if 'content' in data_item), end="", flush=True)
    print()

    # Editing loop
    while True:
        # Get the current thread state
        thread_state = await client.threads.get_state(thread['thread_id'])

        # Get current human messages
        current_human_messages = thread_state['values'].get('human_messages', [])

        # Prompt for user input
        print("\nPlease provide feedback or type 'satisfied' to complete editing:")
        user_input = await asyncio.to_thread(input, "Your input: ")

        # Check for satisfaction condition
        if "satisfied" in user_input.lower():
            break

        # Create a new human message as a string not as HumanMessage
        new_human_message = {
            "content": user_input,
            "role": "human"
        }

        # Append the new human message to the existing list
        updated_human_messages = current_human_messages + [new_human_message]

        # Prepare the update for the thread state
        update_input = {
            "human_messages": updated_human_messages  # Updated list of messages
        }

        # Update the thread state
        forked_config = await client.threads.update_state(
            thread["thread_id"],
            update_input
        )

        # Continue the run with the updated state
        async for chunk in client.runs.stream(
            thread["thread_id"], 
            graph_name, 
            input=None,
            config=config,
            checkpoint_id=forked_config['checkpoint_id'],
            interrupt_before=["human_edit"],
            stream_mode="messages-tuple"
        ):
            if chunk.event == "messages":
                print("".join(data_item['content'] for data_item in chunk.data if 'content' in data_item), end="", flush=True)

    print("Editing process completed.")

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())