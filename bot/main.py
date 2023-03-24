import os
import os.path
import re

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import link, tg_token
from db_queries import DbQueries
from logger import logging

from bot.keyboards import markup_created_acc, markup_new_user

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

storage = MemoryStorage()

bot = Bot(tg_token)  # Initialize bot and dispatcher
dp = Dispatcher(bot, storage=storage)
db = DbQueries()  # соединение с БД


class Form(StatesGroup):
    create_acc = State()
    create_pwd = State()


async def savefile(message: types.Message) -> None:
    """Метод сохранения файла"""
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    downloaded_file = await bot.download_file(file_path)

    src = os.path.join(
        BASE_DIR,
        str("files/")
        + str(message.from_user.id)
        + "_"
        + str(message.document.file_name),
    )
    with open(src, "wb") as new_file:
        new_file.write(downloaded_file.getvalue())


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    """
    Приветственное сообщение при вводе команд `/start` или `/help`
    """
    await message.reply(
        f"Hello {message.from_user.first_name} {message.from_user.last_name}!\n"
        "Please select a button below:",
        reply=False,
        reply_markup=markup_new_user,
    )


@dp.callback_query_handler(text="create_account")
async def process_create_account(call: types.CallbackQuery, state: FSMContext):
    """Первый этап создания аккаунта. Получение названия аккаунта."""
    if not db.account_exist(int(call.from_user.id)):
        await call.message.reply("Please enter your account name below:", reply=False)
        await Form.create_acc.set()
    else:
        await call.message.reply(
            "You already have an account", reply=False, reply_markup=markup_created_acc
        )
        await state.finish()


@dp.message_handler(state=Form.create_acc)
async def process_account(message: types.Message, state: FSMContext):
    """Второй этап создания аккаунта. Получение пароля."""
    if re.match("^[A-Za-z0-9_-]*$", message.text):
        if not db.is_unique(message.text):
            async with state.proxy() as data:
                data["account_name"] = message.text
            await message.answer("Please enter a password:")
            await Form.create_pwd.set()
    else:
        await message.answer(
            "The account name is already taken or invalid. "
            "Please use only English letters and digits."
            "Try another account name:"
        )
        await Form.create_acc.set()


@dp.message_handler(state=Form.create_pwd)
async def process_pwd(message: types.Message, state: FSMContext):
    """Третий этап создания аккаунта. Занесение данных пользователя в БД."""
    async with state.proxy() as data:
        data["account_passwd"] = message.text
        db.add_account(
            message.from_user.id, data["account_name"], data["account_passwd"]
        )
    await message.answer(
        "Account successfully created!", reply_markup=markup_created_acc
    )
    await state.finish()


@dp.callback_query_handler(text="view_urls")
async def process_view_urls(call: types.CallbackQuery):
    """Просмотр персональных url-адресов."""
    if not db.account_exist(call.from_user.id):
        await call.message.answer("Please create an account first")
    else:
        acc_name = db.select_account_name(call.from_user.id)
        counter = db.select_counter(call.from_user.id)
        await call.message.reply(
            "Here are your own URLS\n\n"
            f"url 1: {link}?id={acc_name}&type=Twitter\n"
            f"Number of clicks: {counter}",
            reply=False,
        )


@dp.callback_query_handler(text="submit_work")
async def process_submit_work(call: types.CallbackQuery):
    """Предварительное сообщение перед отправкой работы."""
    if not db.account_exist(call.from_user.id):
        await call.message.answer("Please create an account first")
    else:
        await call.message.reply("Please attach your work and click Send:", reply=False)


@dp.message_handler(content_types=["document"])
async def handle_docs(message: types.Message):
    """Сохранение отправляемых документов."""
    file_name = str(message.from_user.id) + "_" + str(message.document.file_name)
    if db.check_work(message.from_user.id):
        try:
            await savefile(message)
            db.update_filename(file_name, message.from_user.id)
            await message.answer("The file received. Thank you!")
            logging.info("The file %s is uploaded", file_name)
            db.update_work(message.from_user.id, status=True)
        except Exception as e:
            await message.answer(str(e))
    else:
        try:
            await savefile(message)
            await message.answer("The file received. Thank you!")
            logging.info("The first file %s is uploaded", file_name)
            db.update_work(message.from_user.id, status=True)

            db.set_filename(file_name, message.from_user.id)
        except Exception as e:
            await message.answer(str(e))


@dp.callback_query_handler(text="approval_status")
async def process_approval_status(call: types.CallbackQuery):
    """Проверка статуса отправленных работ."""
    if not db.account_exist(call.from_user.id):
        await call.message.answer("Please create an account first")
    else:
        if db.check_work(call.from_user.id):
            await call.message.reply(
                "Here you can check the approval status of the work submitted to us.\n\n"
                "This feature will be added soon",
                reply=False,
            )
        else:
            await call.message.reply("You have not submitted any work yet", reply=False)


if __name__ == "__main__":
    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as E:
        logging.exception(E)
