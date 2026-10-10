<template>
  <div class="about-page">
    <div class="page-header">
      <h1 class="page-title">
        <i class="fas fa-info-circle"></i>
        О приложении
      </h1>
    </div>

    <!-- Краткое вступление -->
    <div class="card intro-card">
      <div class="intro-content">
        <div class="intro-icon">💰</div>
        <div class="intro-text">
          <h2>Финансы</h2>
          <p>
            Личный финансовый помощник для учёта доходов, расходов, долгов,
            переводов между счетами и анализа статистики. Всё в одном месте —
            просто, наглядно и удобно.
          </p>
        </div>
      </div>
    </div>

    <!-- Аккордеон с возможностями -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">
          <i class="fas fa-list-check"></i>
          Возможности приложения
        </h3>
      </div>

      <div class="accordion">
        <div
          v-for="(item, index) in features"
          :key="index"
          class="accordion-item"
          :class="{ 'is-open': openIndex === index }"
        >
          <button class="accordion-header" @click="toggleAccordion(index)">
            <div class="accordion-title">
              <i :class="item.icon" class="accordion-icon"></i>
              <span>{{ item.title }}</span>
            </div>
            <i
              class="fas accordion-arrow"
              :class="openIndex === index ? 'fa-chevron-up' : 'fa-chevron-down'"
            ></i>
          </button>

          <transition name="accordion-fade">
            <div v-show="openIndex === index" class="accordion-body">
              <p class="accordion-description">{{ item.description }}</p>
              <ul class="accordion-list">
                <li v-for="(point, i) in item.points" :key="i">
                  <i class="fas fa-check-circle"></i>
                  <span>{{ point }}</span>
                </li>
              </ul>
            </div>
          </transition>
        </div>
      </div>
    </div>

    <!-- Связь с разработчиком -->
    <div class="card contact-card">
      <div class="card-header">
        <h3 class="card-title">
          <i class="fas fa-envelope"></i>
          Связь с разработчиком
        </h3>
      </div>

      <div class="contact-content">
        <p class="contact-text">
          По вопросам работы приложения, предложениям и сообщениям об ошибках
          пишите на электронную почту:
        </p>

        <a href="mailto:m-zhitkov@inbox.ru" class="contact-email">
          <i class="fas fa-paper-plane"></i>
          m-zhitkov@inbox.ru
        </a>

        <p class="contact-note">
          <i class="fas fa-clock"></i>
          Отвечаю в течение 1–2 рабочих дней.
        </p>
      </div>
    </div>

    <!-- Футер с версией -->
    <div class="about-footer">
      <span>Финансы &copy; {{ currentYear }}</span>
      <span class="version-badge">v1.0.0</span>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'About',
  setup() {
    const openIndex = ref(0)
    const currentYear = new Date().getFullYear()

    const features = [
      {
        title: 'Дашборд',
        icon: 'fas fa-tachometer-alt',
        description:
          'Главный экран с ключевыми показателями ваших финансов и прогнозом на конец месяца.',
        points: [
          'Общий баланс, доходы и расходы за текущий месяц',
          'Прогноз остатка на конец месяца на основе средних трат',
          'Сравнение доходов и расходов с прошлым месяцем',
          'Курсы валют ЦБ РФ (USD, EUR, CNY)',
          'Быстрое добавление транзакции прямо с дашборда'
        ]
      },
      {
        title: 'Счета',
        icon: 'fas fa-credit-card',
        description:
          'Управление всеми вашими счетами: банковские карты, наличные, накопительные.',
        points: [
          'Создание, редактирование и удаление счетов',
          'Разделение на активные и неактивные',
          'Изменение баланса вручную',
          'Общая статистика: количество счетов и суммарный баланс',
          'Адаптивный интерфейс: карточки на мобильных, таблица на десктопе'
        ]
      },
      {
        title: 'Переводы между счетами',
        icon: 'fas fa-exchange-alt',
        description:
          'Перевод средств между любыми счетами, включая неактивные.',
        points: [
          'Перевод с любого счёта, в том числе неактивного',
          'История переводов с пагинацией',
          'Редактирование и удаление переводов',
          'Автоматическое обновление балансов после операции'
        ]
      },
      {
        title: 'Категории',
        icon: 'fas fa-tags',
        description:
          'Гибкая система категорий доходов и расходов с поддержкой подкатегорий.',
        points: [
          'Отдельные списки для доходов и расходов',
          'Древовидная структура: родительские и дочерние категории (глубина — 1 уровень)',
          'Быстрое создание подкатегории из списка',
          'Защита от создания подкатегории у подкатегории'
        ]
      },
      {
        title: 'Транзакции',
        icon: 'fas fa-receipt',
        description:
          'Учёт всех доходов и расходов с удобной фильтрацией и группировкой.',
        points: [
          'Добавление, редактирование и удаление транзакций',
          'Фильтры: тип, счёт, категория, сумма, диапазон дат',
          'Группировка по дням с итогом за день',
          'Пагинация и адаптивный вид: карточки и таблица'
        ]
      },
      {
        title: 'Долги',
        icon: 'fas fa-hand-holding-usd',
        description:
          'Учёт долгов: кому должны вы и кто должен вам.',
        points: [
          'Два типа: «Мне должны» и «Я должен»',
          'Создание долга с привязкой к счёту и контрагенту',
          'Частичное и полное погашение долга',
          'Статистика: итоги по каждому типу и общий баланс долгов'
        ]
      },
      {
        title: 'Статистика и аналитика',
        icon: 'fas fa-chart-line',
        description:
          'Наглядные отчёты по доходам и расходам за месяц и за год.',
        points: [
          'Разбивка по категориям с круговой диаграммой',
          'Детализация по подкатегориям с процентами',
          'Аналитика по месяцам: сумма, средняя, тренд, доля от максимума',
          'Годовые метрики: среднее, медиана, стандартное отклонение, коэффициент вариации',
          'График динамики по месяцам'
        ]
      },
      {
        title: 'Мой график (табель)',
        icon: 'fas fa-calendar-alt',
        description:
          'Учёт рабочих смен, выработки и заработка по периодам.',
        points: [
          'Календарь смен с отметками выработки',
          'Массовое проставление смен на выбранные даты',
          'Отпуска и больничные',
          'Статистика по периодам (1–15 и 16–31) и за месяц',
          'Производительность, мотивация, переработки, доплаты за холод',
          'Заработок в валюте (USD, EUR, CNY, KGS)',
          'Годовая статистика по часам и заработку',
          'Настройка ставок: час, переработка, холод, операция, непроизводственные работы'
        ]
      },
      {
        title: 'Адаптивный интерфейс',
        icon: 'fas fa-mobile-alt',
        description:
          'Приложение удобно работает на любом устройстве.',
        points: [
          'Мобильное боковое меню с оверлеем',
          'Карточки на телефонах и планшетах, таблицы на десктопе',
          'Свайпы для переключения карточек статистики на дашборде',
          'Оптимизированные touch-цели и размеры шрифтов'
        ]
      }
    ]

    const toggleAccordion = (index) => {
      openIndex.value = openIndex.value === index ? -1 : index
    }

    return {
      features,
      openIndex,
      toggleAccordion,
      currentYear
    }
  }
}
</script>

<style scoped>
.about-page {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 1.875rem;
  color: var(--dark-color);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
}

.page-title i {
  color: var(--primary-color);
}

/* ===== Вступление ===== */
.intro-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.intro-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 0.5rem;
}

.intro-icon {
  font-size: 3rem;
  line-height: 1;
  flex-shrink: 0;
}

.intro-text h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  color: white;
}

.intro-text p {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
  opacity: 0.95;
}

/* ===== Карточки ===== */
.card {
  background: var(--white);
  border-radius: var(--radius);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow);
}

.card:last-of-type {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--light-color);
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  color: var(--dark-color);
}

.card-title i {
  color: var(--primary-color);
}

/* ===== Аккордеон ===== */
.accordion {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.accordion-item {
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  overflow: hidden;
  transition: all 0.3s ease;
  background: var(--white);
}

.accordion-item.is-open {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
}

.accordion-header {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  color: var(--dark-color);
  text-align: left;
  transition: background-color 0.2s;
  gap: 1rem;
}

.accordion-header:hover {
  background: var(--light-color);
}

.accordion-item.is-open .accordion-header {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
}

.accordion-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.accordion-icon {
  color: var(--primary-color);
  font-size: 1.1rem;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.accordion-arrow {
  color: var(--gray-color);
  font-size: 0.875rem;
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.accordion-body {
  padding: 1rem 1.25rem 1.25rem;
  border-top: 1px solid var(--light-color);
  background: #fafafa;
}

.accordion-description {
  margin: 0 0 1rem 0;
  font-size: 0.9rem;
  color: var(--gray-color);
  line-height: 1.5;
}

.accordion-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.accordion-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--dark-color);
  line-height: 1.5;
}

.accordion-list li i {
  color: var(--secondary-color);
  font-size: 0.875rem;
  margin-top: 0.2rem;
  flex-shrink: 0;
}

/* Анимация раскрытия */
.accordion-fade-enter-active,
.accordion-fade-leave-active {
  transition: opacity 0.25s ease;
}

.accordion-fade-enter-from,
.accordion-fade-leave-to {
  opacity: 0;
}

/* ===== Связь с разработчиком ===== */
.contact-card {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border: 1px solid #bbf7d0;
}

.contact-card .card-header {
  border-bottom-color: #bbf7d0;
}

.contact-content {
  text-align: center;
  padding: 0.5rem 0;
}

.contact-text {
  margin: 0 0 1.25rem 0;
  font-size: 0.95rem;
  color: #374151;
  line-height: 1.5;
}

.contact-email {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.75rem;
  background: var(--secondary-color);
  color: white;
  text-decoration: none;
  border-radius: var(--radius);
  font-size: 1.1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
  word-break: break-all;
}

.contact-email:hover {
  background: #059669;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.35);
}

.contact-email i {
  font-size: 1rem;
}

.contact-note {
  margin: 1rem 0 0 0;
  font-size: 0.8rem;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

/* ===== Футер ===== */
.about-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  margin-top: 2rem;
  padding: 1rem;
  font-size: 0.8rem;
  color: var(--gray-color);
}

.version-badge {
  background: var(--light-color);
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.7rem;
  color: var(--gray-color);
}

/* ===== Адаптивность ===== */
@media (max-width: 768px) {
  .page-title {
    font-size: 1.5rem;
  }

  .intro-content {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }

  .intro-icon {
    font-size: 2.5rem;
  }

  .intro-text h2 {
    font-size: 1.25rem;
  }

  .card {
    padding: 1rem;
  }

  .card-title {
    font-size: 1.1rem;
  }

  .accordion-header {
    padding: 0.875rem 1rem;
    font-size: 0.9rem;
  }

  .accordion-body {
    padding: 0.875rem 1rem 1rem;
  }

  .contact-email {
    font-size: 0.95rem;
    padding: 0.75rem 1.25rem;
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.25rem;
  }

  .accordion-title {
    gap: 0.5rem;
  }

  .accordion-icon {
    font-size: 1rem;
    width: 20px;
  }

  .accordion-list li {
    font-size: 0.8rem;
  }
}
</style>