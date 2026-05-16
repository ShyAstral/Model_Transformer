<script setup>
import { ref } from 'vue'

// --- ESTADO DEL GENERADOR (IA) ---
const promptText = ref('')
const suggestion = ref('')
const isPredicting = ref(false)
let typingTimer = null

const handleInput = () => {
  suggestion.value = ''
  clearTimeout(typingTimer)
  if (!promptText.value.trim()) return

  typingTimer = setTimeout(async () => {
    await fetchPrediction()
  }, 500)
}

const fetchPrediction = async () => {
  isPredicting.value = true
  try {
    const res = await fetch('http://127.0.0.1:8000/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: promptText.value, maxtokens: 2 })
    })
    const data = await res.json()
    suggestion.value = data.prediction
  } catch (error) {
    console.error("Error de conexión:", error)
  } finally {
    isPredicting.value = false
  }
}

const acceptSuggestion = () => {
  if (suggestion.value) {
    promptText.value += suggestion.value
    suggestion.value = ''
  }
}

// --- ESTADO DE LA BASE DE DATOS ---
const phraseText = ref('')
const dbResult = ref(null)
const isLoadingDb = ref(false)

const savePhrase = async () => {
  if (!phraseText.value) return;
  isLoadingDb.value = true;
  dbResult.value = null;

  try {
    const res = await fetch('http://127.0.0.1:8000/text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: phraseText.value })
    })
    const data = await res.json()
    dbResult.value = data
  } catch (error) {
    console.error("Error al guardar:", error)
  } finally {
    isLoadingDb.value = false;
  }
}
</script>

<template>
  <div class="lunar-dashboard">
    <main class="container">
      <header class="header">
        <h1>Centro de Comando IA</h1>
        <p class="subtitle">Asistente de escritura y registro de datos</p>
      </header>

      <div class="grid-layout">
        <section class="glass-card">
          <div class="card-header">
            <span class="indicator active"></span>
            <h2>Módulo de Generación</h2>
          </div>
          
          <div class="input-wrapper">
            <textarea 
              v-model="promptText" 
              @input="handleInput"
              @keydown.tab.prevent="acceptSuggestion"
              @keydown.right.prevent="acceptSuggestion"
              placeholder="Inicia la secuencia de texto..."
              class="lunar-input main-textarea"
            ></textarea>
            
            <div class="status-bar">
              <span v-if="isPredicting" class="status-text pulse">Analizando entropía...</span>
              <span v-else-if="suggestion" class="status-text success">
                <span class="suggestion-highlight">{{ suggestion }}</span>
                <span class="tooltip-badge">Tab ↹</span>
              </span>
              <span v-else class="status-text idle">Esperando entrada de datos</span>
            </div>
          </div>
        </section>

        <section class="glass-card">
          <div class="card-header">
            <span class="indicator db"></span>
            <h2>Registro de Frases</h2>
          </div>

          <div class="input-wrapper">
            <input 
              type="text" 
              v-model="phraseText" 
              placeholder="Ingresa una frase para indexar..." 
              class="lunar-input"
            />
          </div>

          <button class="lunar-btn" @click="savePhrase" :disabled="isLoadingDb">
            {{ isLoadingDb ? 'Procesando...' : 'Indexar en Memoria' }}
          </button>

          <Transition name="fade">
            <div v-if="dbResult" class="result-box">
              <div class="result-header">Registro Exitoso</div>
              <div class="result-data">
                <div><span class="label">ID:</span> {{ dbResult.id }}</div>
                <div><span class="label">Longitud:</span> {{ dbResult.word_count }} palabras</div>
              </div>
            </div>
          </Transition>
        </section>
      </div>
    </main>
  </div>
</template>

<style>
/* Reset básico para asegurar que tome toda la pantalla */
body, html {
  margin: 0;
  padding: 0;
  height: 100%;
  background-color: #0b0d17; /* Fondo de caída */
}
</style>

<style scoped>
/* --- Variables y Estructura Principal --- */
.lunar-dashboard {
  min-height: 100vh;
  /* Gradiente profundo estilo espacio lunar */
  background: radial-gradient(circle at 50% 0%, #1a1f35 0%, #0b0d17 70%, #05060a 100%);
  color: #e2e8f0;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  padding: 3rem 1rem;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

/* --- Tipografía y Cabecera --- */
.header {
  text-align: center;
  margin-bottom: 1rem;
}

h1 {
  font-size: 2.5rem;
  font-weight: 300;
  letter-spacing: 0.05em;
  color: #f8fafc;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 0 20px rgba(165, 180, 252, 0.3);
}

.subtitle {
  color: #94a3b8;
  font-size: 1rem;
  letter-spacing: 0.02em;
}

/* --- Layout --- */
.grid-layout {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* --- Tarjetas Glassmorphism --- */
.glass-card {
  background: rgba(21, 25, 43, 0.4);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3), 
              inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.glass-card:hover {
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 
              0 0 20px rgba(165, 180, 252, 0.05),
              inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding-bottom: 1rem;
}

.card-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 500;
  color: #cbd5e1;
}

/* Indicadores de estado visuales */
.indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  box-shadow: 0 0 10px currentColor;
}
.indicator.active { color: #818cf8; background: #818cf8; }
.indicator.db { color: #34d399; background: #34d399; }

/* --- Entradas de Texto (Inputs / Textareas) --- */
.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.lunar-input {
  width: 100%;
  background: rgba(9, 11, 20, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 8px;
  padding: 1rem;
  color: #f1f5f9;
  font-size: 1rem;
  outline: none;
  box-sizing: border-box;
  transition: all 0.2s ease;
}

.lunar-input::placeholder {
  color: #475569;
}

/* Estado Focused */
.lunar-input:focus {
  border-color: #818cf8;
  background: rgba(15, 23, 42, 0.8);
  box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.15), 
              inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

.main-textarea {
  min-height: 140px;
  resize: vertical;
  line-height: 1.6;
}

/* --- Botones --- */
.lunar-btn {
  background: linear-gradient(135deg, rgba(129, 140, 248, 0.9), rgba(99, 102, 241, 0.9));
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  letter-spacing: 0.05em;
  transition: all 0.2s ease;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
}

.lunar-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
  background: linear-gradient(135deg, rgba(129, 140, 248, 1), rgba(99, 102, 241, 1));
}

.lunar-btn:active:not(:disabled) {
  transform: translateY(1px);
}

.lunar-btn:disabled {
  background: rgba(71, 85, 105, 0.5);
  color: #94a3b8;
  box-shadow: none;
  cursor: not-allowed;
  border-color: transparent;
}

/* --- Tooltips y Barra de Estado --- */
.status-bar {
  display: flex;
  align-items: center;
  min-height: 28px;
  padding: 0 0.5rem;
}

.status-text {
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.status-text.idle { color: #475569; }
.status-text.success { color: #e2e8f0; }
.suggestion-highlight { color: #a5b4fc; font-weight: 500; }

.tooltip-badge {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-family: monospace;
  font-size: 0.75rem;
  color: #94a3b8;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.pulse {
  color: #818cf8;
  animation: pulse-animation 1.5s infinite;
}

@keyframes pulse-animation {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

/* --- Caja de Resultados (Base de Datos) --- */
.result-box {
  margin-top: 1.5rem;
  background: rgba(16, 185, 129, 0.05);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 8px;
  padding: 1rem;
}

.result-header {
  color: #34d399;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.result-data {
  display: flex;
  gap: 1.5rem;
  font-size: 0.85rem;
  color: #cbd5e1;
}

.result-data .label {
  color: #64748b;
}

/* Animación para cuando aparece el resultado */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>