<template>
  <div class="modal" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>{{ isEditing ? 'Изменить цель' : 'Установить цель на месяц' }}</h3>
        <button class="modal-close" @click="$emit('close')">&times;</button>
      </div>

      <form @submit.prevent="save">
        <div class="form-group">
          <label class="form-label required">Тип цели</label>
          <select v-model="form.goal_type" class="form-control" @change="onTypeChange">
            <option value="save">💰 Сэкономить (доходы минус расходы)</option>
            <option value="limit">🚫 Не превысить лимит расходов</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label required">Сумма (₽)</label>
          <input type="number" v-model.number="form.amount" class="form-control" step="any" min="1" required />
        </div>

        <div class="form-group" v-if="form.goal_type === 'limit'">
          <label class="form-label">Категория (если не выбрана — все расходы)</label>
          <select v-model="form.category" class="form-control">
            <option :value="null">Все расходы</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Отмена</button>
          <button type="submit" class="btn btn-primary" :disabled="saving">
            <i v-if="saving" class="fas fa-spinner fa-spin"></i>
            Сохранить
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'GoalModal',
  props: {
    existingGoal: { type: Object, default: null }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const saving = ref(false)
    const categories = ref([])
    const form = ref({
      goal_type: props.existingGoal?.goal_type || 'save',
      amount: props.existingGoal?.amount || 30000,
      category: props.existingGoal?.category || null
    })

    const onTypeChange = () => {
      if (form.value.goal_type === 'save') form.value.category = null
    }

    const loadCategories = async () => {
      try {
        const data = await apiService.getCategories('expense', 1, 100, true)
        categories.value = data.results || []
      } catch (e) {
        console.error('Load cats error', e)
      }
    }

    const save = async () => {
      saving.value = true
      try {
        await apiService.saveGoal(form.value)
        emit('saved')
        emit('close')
      } catch (e) {
        console.error('Save goal error', e)
        alert('Ошибка при сохранении цели')
      } finally {
        saving.value = false
      }
    }

    onMounted(loadCategories)

    return { form, saving, categories, onTypeChange, save }
  }
}
</script>

<style scoped>
/* Стили можно скопировать из любого вашего модального окна */
.modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: var(--white); border-radius: var(--radius); padding: 1.5rem; width: 100%; max-width: 400px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.modal-close { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--gray-color); }
.form-group { margin-bottom: 1rem; }
.form-label { display: block; margin-bottom: 0.5rem; font-size: 0.9rem; color: var(--dark-color); }
.form-control { width: 100%; padding: 0.5rem; border: 1px solid var(--gray-color); border-radius: var(--radius); background: var(--white); color: var(--dark-color); }
.modal-footer { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1.5rem; }
</style>