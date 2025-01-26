from aiogram.utils.markdown import hbold

enter_email: str = hbold("Введите ваш email.")

password: str = (hbold('Введите пароль.')  +
                 "\nПароль должен быть не короче 5 символов и содержать "
                 "буквы и цифры.")

success_auth: str = "Вы авторизованы."

success_registration: str = ("Вы успешно зарегистрировались! Теперь вы имеете "
                             "доступ к остальному функционалу бота.")

greeting = (
    "Привет! Я телеграм бот для отслеживания привычек. "
    "Я помогу вам избавиться от ненужных и выработать новые. "
    "Чтобы узнать как пользоваться ботом, в меню бота выберите пункт "
    "как пользоваться ботом."
)