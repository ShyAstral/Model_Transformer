<script setup>
import { ref } from 'vue'

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
        <h1>NexText</h1>
        <p class="subtitle">Modelo transformer para predicción de texto</p>
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
              <span v-if="isPredicting" class="status-text pulse">Esperando respuesta del modelo...</span>
              <span v-else-if="suggestion" class="status-text success">
                <span class="suggestion-highlight-prefix">Respuesta del modelo:</span>
                <span class="suggestion-highlight">{{ suggestion }}</span>
                <span class="tooltip-badge">Tab</span>
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