import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import CommandStart

API_TOKEN = '7924465298:AAHk7ToscQx56Ue7c3c4ksSUn1MnhdH2V7A'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class OrderState(StatesGroup):
    waiting_for_price = State()
    waiting_for_shipping = State()

# Основное меню с добавлением кнопки "Связь с менеджером"
main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🧮 Калькулятор")],
    [KeyboardButton(text="🛍 Магазин", web_app=types.WebAppInfo(url="https://dolcedeals.ru"))],
    [KeyboardButton(text="🌐 Наши ресурсы"), KeyboardButton(text="ℹ️ О нас")],
    [KeyboardButton(text="❓ FAQ")],
    [KeyboardButton(text="💬 Связь с менеджером")]
], resize_keyboard=True)

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        "Добро пожаловать в *Dolce Deals* — Ваш персональный консьерж в мире моды 🖤\n\n"
        "Пожалуйста, выберите действие:",
        reply_markup=main_menu,
        parse_mode="Markdown"
    )

@dp.message(F.text == "🧮 Калькулятор")
async def start_calculation(message: types.Message, state: FSMContext):
    await message.answer("💬 Пожалуйста, введите стоимость желаемой вещи в евро:")
    await state.set_state(OrderState.waiting_for_price)

@dp.message(OrderState.waiting_for_price)
async def process_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text.replace(',', '.'))
        await state.update_data(price=price)

        if price <= 300:
            options = ["Почта (45 €)", "EMS (55 €)", "Курьер (70 €)"]
        else:
            options = ["Курьер (70 €)"]

        builder = ReplyKeyboardBuilder()
        for opt in options:
            builder.add(KeyboardButton(text=opt))
        await message.answer(
            "📦 Пожалуйста, выберите способ доставки:\n\n"
            "Почта - бюджетный вариант для тех, кто не спешит. Доставка занимает от 10 до 18 дней.\n"
            "EMS - почтовое экспресс отправление. Доставка занимает от 4 до 10 дней.\n"
            "Курьер - Ваше отправление передается нашему курьеру, который передаст Вам посылку лично в руки или отправит по России любым удобным способом.",
            reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
        )
        await state.set_state(OrderState.waiting_for_shipping)
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число, например: 250.50")

@dp.message(OrderState.waiting_for_shipping)
async def process_shipping(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    price = user_data.get("price")

    delivery_map = {
        "Почта (45 €)": 45,
        "EMS (55 €)": 55,
        "Курьер (70 €)": 70
    }
    delivery_cost = delivery_map.get(message.text.strip(), 70)

    full_price = price + delivery_cost

    if full_price <= 300:
        commission = 0.15
    elif full_price <= 1000:
        commission = 0.10
    elif full_price <= 2000:
        commission = 0.09
    elif full_price <= 3500:
        commission = 0.08
    else:
        commission = 0.05

    total_eur = full_price * (1 + commission)
    eur_rate = get_eur_rate() + 3
    total_rub = int(total_eur * eur_rate)

    await message.answer(
        f"✅ Предварительный расчет:\n\n"
        f"💵 Приблизительно: *{total_rub:,} ₽*"
        .replace(",", " "),
        parse_mode="Markdown"
    )

    # Кнопки для дальнейших действий
    buttons = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Сделать заказ")],
            [KeyboardButton(text="Вернуться в меню")]
        ], resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer("Если вас устраивает расчет, выберите одно из действий ниже:", reply_markup=buttons)

    await state.clear()

def get_eur_rate():
    try:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
        data = response.json()
        return data["Valute"]["EUR"]["Value"]
    except:
        return 100

@dp.message(F.text == "🛍 Магазин")
async def open_site(message: types.Message):
    await message.answer("Вы можете перейти на наш магазин: https://dolcedeals.ru")

@dp.message(F.text == "🌐 Наши ресурсы")
async def resources(message: types.Message):
    await message.answer(
        "Полезные ссылки:\n\n"
        "🔗 Наш Telegram-канал: https://t.me/dolcedeals\n"
        "📸 Instagram: https://www.instagram.com/dolce_deals\n"
        "🌍 Сайт: https://dolcedeals.ru\n"
        "📌 Tik-Tok: https://www.tiktok.com/@dolce.deals"
    )

@dp.message(F.text == "ℹ️ О нас")
async def about_us(message: types.Message):
    await message.answer(
        "🖤 *Dolce Deals* — это простой и выгодный шопинг, который мы с Вами так любим.\n\n"
        "Наш сервис существует уже более двух лет и с лёгкостью справляется даже с самыми нестандартными заказами.\n\n"
        "Команда Dolce Deals занимается перепродажей лимитированной одежды с 2016 года, мы знаем, где искать, как выгодно купить и как доставить.",
        parse_mode="Markdown"
    )

@dp.message(F.text == "❓ FAQ")
async def faq(message: types.Message):
    await message.answer(
        "🛍 *Как работает сервис Dolce Deals:*\n\n"
        "1. Вы отправляете желаемую вещь — это может быть ссылка, фото или просто описание.\n"
        "2. Мы находим товар и уточняем наличие нужного размера.\n"
        "3. Обсуждаем с Вами способы и сроки доставки.\n"
        "4. Рассчитываем финальную стоимость.\n"
        "5. Если Вас всё устраивает — Вы переводите озвученную сумму.\n"
        "6. Мы совершаем выкуп и отчитываемся перед Вами.\n"
        "7. После этого отправляем заказ и остаёмся на связи до момента получения.\n\n"
        "💬 На каждом этапе с Вами работает персональный менеджер.",
        parse_mode="Markdown"
    )

@dp.message(F.text == "💬 Связь с менеджером")
async def contact_manager(message: types.Message):
    await message.answer("Связаться с менеджером можно по ссылке: [@dolcedealsmanager](https://t.me/dolcedealsmanager)", parse_mode="Markdown")

# Обработчик для кнопки "Сделать заказ"
@dp.message(F.text == "Сделать заказ")
async def make_order(message: types.Message):
    await message.answer("Для оформления заказа свяжитесь с нашим менеджером: [@dolcedealsmanager](https://t.me/dolcedealsmanager)", parse_mode="Markdown")

# Обработчик для кнопки "Вернуться в меню"
@dp.message(F.text == "Вернуться в меню")
async def back_to_menu(message: types.Message):
    await message.answer(
        "Вы вернулись в главное меню. Пожалуйста, выберите действие:",
        reply_markup=main_menu
    )

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())





