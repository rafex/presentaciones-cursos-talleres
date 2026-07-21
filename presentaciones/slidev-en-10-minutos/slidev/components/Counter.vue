<template>
  <div class="counter-container">
    <div class="counter-display">
      <span class="counter-value">{{ count }}</span>
    </div>
    <div class="counter-buttons">
      <button @click="decrement" class="btn btn-primary">−</button>
      <button @click="increment" class="btn btn-primary">+</button>
      <button @click="reset" class="btn btn-secondary">Reset</button>
    </div>
    <p class="counter-info">Esto es un componente Vue interactivo en Slidev</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const count = ref(0)

const increment = () => {
  count.value++
}

const decrement = () => {
  count.value--
}

const reset = () => {
  count.value = 0
}
</script>

<style scoped>
.counter-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  color: white;
  max-width: 300px;
  margin: 0 auto;
}

.counter-display {
  font-size: 48px;
  font-weight: bold;
  background: rgba(255, 255, 255, 0.1);
  padding: 20px 40px;
  border-radius: 8px;
  min-width: 150px;
  text-align: center;
}

.counter-value {
  font-size: 72px;
  font-weight: 900;
}

.counter-buttons {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  font-size: 18px;
  font-weight: bold;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: white;
  color: #667eea;
}

.btn-primary:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

.counter-info {
  font-size: 14px;
  opacity: 0.9;
}
</style>
