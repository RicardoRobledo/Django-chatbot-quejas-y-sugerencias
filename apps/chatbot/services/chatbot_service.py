from ..repositories import chatbot_repository


async def send_message(dates:str, thread_id:str, message:str):
    return await chatbot_repository.send_message(dates, thread_id, message)
