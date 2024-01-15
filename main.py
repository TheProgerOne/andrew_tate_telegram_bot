import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import aiohttp
#import openai

# Configure logging
logging.basicConfig(level=logging.INFO)

# Telegram Bot Token
TELEGRAM_TOKEN = "6904496907:AAFbNvSAeIAZOaeOazoosw3oNMXhGM0u7Kc"

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# Define keyboard buttons
button1 = KeyboardButton(text='Get Dating Advice')
keyboard = ReplyKeyboardMarkup(keyboard=[[button1]], resize_keyboard=True)

class CharmGPTState(StatesGroup):
    waiting_for_context = State()
    waiting_for_message = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Hello! I'm here to provide dating advice. What's your situation?", reply_markup=keyboard)
    await state.set_state(CharmGPTState.waiting_for_context)

@dp.message(CharmGPTState.waiting_for_context)
async def process_context(message: types.Message, state: FSMContext):
    await state.update_data(context=message.text)
    await message.answer("Got it. What did she say or what's your question?")
    await state.set_state(CharmGPTState.waiting_for_message)

@dp.message(CharmGPTState.waiting_for_message)
async def process_message(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    context = user_data.get('context')
    user_message = message.text

    async with aiohttp.ClientSession() as session:
        response = await session.post(
            'http://server-for-bot-gpt/getDatingAdvice',
            json={'context': context, 'message': user_message, 'maxLength': 200, 'temperature': 0.7}
        )
        if response.status == 200:
            gpt_response = await response.json()
            await message.answer(gpt_response.get('advice', 'No advice found.').strip())
        else:
            await message.answer("Sorry, there was an error processing your request.")
    await state.clear()

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
