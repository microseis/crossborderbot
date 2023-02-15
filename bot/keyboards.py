from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

inline_btn_1 = InlineKeyboardButton('Create Account', callback_data='create_account')
inline_btn_2 = InlineKeyboardButton('View URLs', callback_data='view_urls')
inline_btn_3 = InlineKeyboardButton('Submit your Work', callback_data='submit_work')
inline_btn_4 = InlineKeyboardButton('Approval status', callback_data='approval_status')

markup_new_user = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2, inline_btn_3, inline_btn_4)

markup_created_acc = InlineKeyboardMarkup()

markup_created_acc.add(inline_btn_2, inline_btn_3, inline_btn_4)
