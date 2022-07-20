import logging
import os.path
from aiogram import Bot, Dispatcher, executor, types

from keyboards import markup_new_user, markup_created_acc
import os
import re
from db_querries import DBquerries

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#db_path = os.path.join(BASE_DIR, "php_my_admin_db.db")

storage = MemoryStorage()

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# Initialize bot and dispatcher

bot = Bot(token=os.environ.get("TOKEN"))

dp = Dispatcher(bot, storage=storage)

# соединение с БД
db = DBquerries()


class Form(StatesGroup):
    create_acc = State()
    create_pwd = State()


async def savefile(message):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    downloaded_file = await bot.download_file(file_path)

    src = os.path.join(BASE_DIR,
                       str("files/") + str(message.from_user.id) + "_" + str(message.document.file_name))
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file.getvalue())


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply(f'Hello {message.from_user.first_name} {message.from_user.last_name}!\n'
                        'Please select a button below:'
                        , reply=False, reply_markup=markup_new_user)


@dp.callback_query_handler(text='create_account')
async def process_callback_button1(call: types.CallbackQuery, state: FSMContext):
    if not db.account_exist(call.from_user.id):
        await call.message.reply("Please enter your account name below:", reply=False)
        await Form.create_acc.set()
    else:
        await call.message.reply("You already have an account", reply=False, reply_markup=markup_created_acc)
        await state.finish()


@dp.message_handler(state=Form.create_acc)
async def process_account(message: types.Message, state: FSMContext):
    if re.match("^[A-Za-z0-9_-]*$", message.text):
        if not db.is_unique(message.text):
            async with state.proxy() as data:
                data['account_name'] = message.text
            await message.answer("Please enter a password:")
            await Form.create_pwd.set()
    else:
        await message.answer("The account name is already taken or invalid. Please use only English "
                             "letters and digits. "
                             "Try another account name:")
        await Form.create_acc.set()


@dp.message_handler(state=Form.create_pwd)
async def process_pwd(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['account_passwd'] = message.text
        db.add_account(message.from_user.id, data['account_name'], data['account_passwd'])
    await message.answer("Account successfully created!", reply_markup=markup_created_acc)
    await state.finish()


@dp.callback_query_handler(text='view_urls')
async def process_callback_button2(call: types.CallbackQuery):
    if not db.account_exist(call.from_user.id):
        await call.message.answer("Please create an account first")
    else:
        acc_name = db.select_account_name(call.from_user.id)
        counter = db.select_counter(call.from_user.id)
        await call.message.reply(f"Here are your own URLS\n\n"
                                 f"url 1: https://telegram.rebelstation.org/wp-json/bounty/v1/bounty-count/?id={acc_name}&type=Twitter\n"
                                 f"Number of clicks: {counter}", reply=False)


@dp.callback_query_handler(text='submit_work')
async def process_callback_button3(call: types.CallbackQuery):
    if not db.account_exist(call.from_user.id):
        await call.message.answer("Please create an account first")
    else:
        await call.message.reply(f"Please attach your work and click Send:", reply=False)


@dp.message_handler(content_types=['document'])
async def handle_docs(message: types.Message):
    fname = str(message.from_user.id) + "_" + str(message.document.file_name)
    if db.check_work(message.from_user.id):
        try:
            await savefile(message)
            db.update_filename(fname, message.from_user.id)
            await message.answer("The file received. Thank you!")
            print("The file " + fname + " is uploaded")
            db.update_work(message.from_user.id, status=True)
        except Exception as e:
            await message.answer(str(e))
    else:
        try:
            await savefile(message)
            await message.answer("The file received. Thank you!")
            print("The first file "+str(fname)+" is uploaded")
            db.update_work(message.from_user.id, status=True)

            db.set_filename(fname, message.from_user.id)
        except Exception as e:
            await message.answer(str(e))


@dp.callback_query_handler(text='approval_status')
async def process_callback_button4(call: types.CallbackQuery):
    if not db.account_exist(call.from_user.id):
        await call.message.answer("Please create an account first")
    else:
        if db.check_work(call.from_user.id):
            await call.message.reply(f"Here you can check the approval status of the work submitted to us.\n\n"
                                     f"This feature will be added soon", reply=False)
        else:
            await call.message.reply(f"You have not submitted any work yet", reply=False)


if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as E:
        logging.exception(E)
