<template>
  <div>
    <div class="page-header">
      <h1>Категории</h1>
      <button @click="openCreateModal" class="btn btn-primary">
        <i class="fas fa-plus"></i> Создать категорию
      </button>
    </div>

    <!-- Переключатель типов -->
    <div class="type-tabs">
      <button 
        @click="currentType = 'income'" 
        class="tab-btn" 
        :class="{ active: currentType === 'income' }"
      >
        <i class="fas fa-arrow-up"></i> Доходы
      </button>
      <button 
        @click="currentType = 'expense'" 
        class="tab-btn" 
        :class="{ active: currentType === 'expense' }"
      >
        <i class="fas fa-arrow-down"></i> Расходы
      </button>
    </div>

    <div class="card">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Загрузка категорий...</p>
      </div>
      
      <div v-else-if="categoriesList.length === 0" class="empty-state">
        <i class="fas fa-folder-open"></i>
        <p>Нет созданных категорий для {{ currentType === 'income' ? 'доходов' : 'расходов' }}</p>
        <button @click="openCreateModal" class="btn btn-primary">Создать первую категорию</button>
      </div>
      
      <div v-else class="categories-list">
        <div 
          v-for="category in categoriesList" 
          :key="category.id" 
          class="category-item"
          :style="{ marginLeft: category.level * 20 + 'px' }"
        >
          <div class="category-info">
            <i :class="category.has_children ? 'fas fa-folder-open' : 'fas fa-tag'" class="category-icon"></i>
            <span class="category-name">{{ category.name }}</span>
            <span class="category-badge" :class="category.has_children ? 'badge-parent' : 'badge-regular'">
              {{ category.has_children ? 'Родительская' : 'Категория' }}
            </span>
          </div>
          <div class="category-actions">
            <button @click="openCreateChildModal(category)" class="btn btn-sm btn-success" title="Добавить подкатегорию">
              <i class="fas fa-plus"></i>
            </button>
            <button @click="editCategory(category)" class="btn btn-sm btn-info" title="Редактировать">
              <i class="fas fa-edit"></i>
            </button>
            <button @click="confirmDelete(category)" class="btn btn-sm btn-danger" title="Удалить">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно создания/редактирования категории -->
    <div v-if="showCategoryModal" class="modal" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingCategory ? 'Редактировать категорию' : 'Создать категорию' }}</h3>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>

        <form @submit.prevent="saveCategory">
          <div class="form-group">
            <label class="form-label required">Название категории</label>
            <input 
              type="text" 
              v-model="formData.name" 
              class="form-control" 
              required
              placeholder="Например: Еда, Транспорт, Зарплата"
            >
          </div>

          <div class="form-group">
            <label class="form-label">Родительская категория</label>
            <select v-model="formData.parent" class="form-control">
              <option value="">— Корневая категория —</option>
              <option v-for="cat in availableParents" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">
              {{ editingCategory ? 'Обновить' : 'Создать' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно подтверждения удаления -->
    <div v-if="showDeleteModal" class="modal" @click.self="showDeleteModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Подтверждение удаления</h3>
          <button class="modal-close" @click="showDeleteModal = false">&times;</button>
        </div>
        
        <div class="alert alert-danger" v-if="categoryToDelete?.has_children">
          <i class="fas fa-exclamation-triangle"></i>
          Внимание! У этой категории есть дочерние категории, они также будут удалены!
        </div>
        
        <p>Вы уверены, что хотите удалить категорию <strong>"{{ categoryToDelete?.name }}"</strong>?</p>
        
        <div class="modal-footer">
          <button @click="showDeleteModal = false" class="btn btn-secondary">Отмена</button>
          <button @click="deleteCategory" class="btn btn-danger">Да, удалить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'CategoriesList',
  setup() {
    const categories = ref([])
    const currentType = ref('income')
    const loading = ref(false)
    const showCategoryModal = ref(false)
    const showDeleteModal = ref(false)
    const editingCategory = ref(null)
    const categoryToDelete = ref(null)
    const formData = ref({
      name: '',
      parent: ''
    })

    // Преобразуем в плоский список с уровнем вложенности
    const categoriesList = computed(() => {
      const result = []
      
      const flatten = (items, level = 0) => {
        for (const item of items) {
          result.push({
            ...item,
            level: level
          })
          if (item.children && item.children.length) {
            flatten(item.children, level + 1)
          }
        }
      }
      
      flatten(categories.value)
      return result
    })

    // Доступные родительские категории
    const availableParents = computed(() => {
      const result = []
      
      const flatten = (items, prefix = '') => {
        for (const item of items) {
          if (!editingCategory.value || item.id !== editingCategory.value.id) {
            result.push({ 
              id: item.id, 
              name: prefix + item.name 
            })
          }
          if (item.children && item.children.length) {
            flatten(item.children, prefix + '— ')
          }
        }
      }
      
      flatten(categories.value)
      return result
    })

    const loadCategories = async () => {
      loading.value = true
      try {
        // Добавляем параметр parent=true чтобы получить только корневые категории с их детьми
        const data = await apiService.getCategories(currentType.value, 1, 100, true)
        categories.value = data.results || []
        console.log('Загружено категорий:', categories.value)
      } catch (error) {
        console.error('Error loading categories:', error)
        categories.value = []
      } finally {
        loading.value = false
      }
    }

    const openCreateModal = () => {
      editingCategory.value = null
      formData.value = {
        name: '',
        parent: ''
      }
      showCategoryModal.value = true
    }

    const openCreateChildModal = (category) => {
      editingCategory.value = null
      formData.value = {
        name: '',
        parent: category.id
      }
      showCategoryModal.value = true
    }

    const editCategory = (category) => {
      editingCategory.value = category
      formData.value = {
        name: category.name,
        parent: category.parent || ''
      }
      showCategoryModal.value = true
    }

    const saveCategory = async () => {
      if (!formData.value.name.trim()) {
        alert('Введите название категории')
        return
      }
      
      try {
        if (editingCategory.value) {
          await apiService.updateCategory(
            editingCategory.value.id,
            formData.value.name,
            formData.value.parent || null
          )
        } else {
          await apiService.createCategory(
            formData.value.name,
            currentType.value,
            formData.value.parent || null
          )
        }
        closeModal()
        await loadCategories()
      } catch (error) {
        console.error('Error saving category:', error)
        alert('Ошибка при сохранении категории')
      }
    }

    const confirmDelete = (category) => {
      categoryToDelete.value = category
      showDeleteModal.value = true
    }

    const deleteCategory = async () => {
      try {
        await apiService.deleteCategory(categoryToDelete.value.id)
        showDeleteModal.value = false
        await loadCategories()
      } catch (error) {
        console.error('Error deleting category:', error)
        alert('Ошибка при удалении категории')
      }
    }

    const closeModal = () => {
      showCategoryModal.value = false
      editingCategory.value = null
      formData.value = {
        name: '',
        parent: ''
      }
    }

    watch(currentType, () => {
      loadCategories()
    })

    onMounted(() => {
      loadCategories()
    })

    return {
      categories,
      currentType,
      loading,
      categoriesList,
      availableParents,
      showCategoryModal,
      showDeleteModal,
      editingCategory,
      categoryToDelete,
      formData,
      openCreateModal,
      openCreateChildModal,
      editCategory,
      saveCategory,
      confirmDelete,
      deleteCategory,
      closeModal
    }
  }
}
</script>


<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.type-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  background: var(--white);
  padding: 0.5rem;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.tab-btn {
  flex: 1;
  padding: 0.75rem;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: var(--radius);
  font-weight: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.tab-btn.active {
  background: var(--primary-color);
  color: var(--white);
}

.categories-list {
  padding: 1rem;
  min-height: 400px;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  margin: 0.25rem 0;
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  transition: all 0.3s;
}

.category-item:hover {
  background: var(--light-color);
  transform: translateX(5px);
  box-shadow: var(--shadow);
}

.category-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.category-icon {
  color: var(--primary-color);
  font-size: 1.1rem;
}

.category-name {
  font-weight: 500;
  font-size: 1rem;
}

.category-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.badge-parent {
  background: #dbeafe;
  color: #1e40af;
}

.badge-child {
  background: #f3e8ff;
  color: #6b21a5;
}

.category-actions {
  display: flex;
  gap: 0.5rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--gray-color);
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state p {
  margin-bottom: 1.5rem;
}

.loading-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--gray-color);
}

.spinner {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 3px solid var(--light-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
}

.required:after {
  content: " *";
  color: var(--danger-color);
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .category-item {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .category-info {
    width: 100%;
  }
  
  .category-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>