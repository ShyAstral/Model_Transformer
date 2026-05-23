<script setup>
import { ref, computed, onMounted } from 'vue'

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

    await postMetric(0, 1)
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

    postMetric(1, 0)

    clearTimeout(typingTimer)
    typingTimer = setTimeout(async () => {
      await fetchPrediction()
    }, 150)
  }
}

const phraseText = ref('')
const dbResult = ref(null)
const isLoadingDb = ref(false)
const isTraining = ref(false)
const trainMessage = ref('')

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

const trainModel = async () => {
  isTraining.value = true
  trainMessage.value = ''
  try {
    await fetch('http://127.0.0.1:8000/train')
    trainMessage.value = '¡Modelo optimizado con éxito!'
  } catch (error) {
    console.error("Error al entrenar:", error)
    trainMessage.value = 'Fallo en el entrenamiento.'
  } finally {
    isTraining.value = false
  }
}

const metrics = ref({ total_tabs: 0, total_tips: 0 })

const maxMetric = computed(() => Math.max(metrics.value.total_tips, metrics.value.total_tabs, 1))
const tipHeight = computed(() => (metrics.value.total_tips / maxMetric.value) * 100)
const tabHeight = computed(() => (metrics.value.total_tabs / maxMetric.value) * 100)
const acceptanceRate = computed(() => {
  if (metrics.value.total_tips === 0) return 0;
  return ((metrics.value.total_tabs / metrics.value.total_tips) * 100).toFixed(1);
})

const fetchMetrics = async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/metric')
    const data = await res.json()
    metrics.value = data
  } catch (error) {
    console.error("Error al obtener métricas:", error)
  }
}

const postMetric = async (tabs, tips) => {
  try {
    await fetch('http://127.0.0.1:8000/metric', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tabcount: tabs, tipcount: tips })
    })
    await fetchMetrics()
  } catch (error) {
    console.error("Error al guardar métrica:", error)
  }
}

const selectedFile = ref(null)
const fileInput = ref(null)

const handleDrop = (event) => {
  const files = event.dataTransfer.files
  if (files.length > 0) {
    selectedFile.value = files[0]
  }
}

const handleFileUpload = (event) => {
  selectedFile.value = event.target.files[0]
}

const uploadDataset = async () => {
  if (!selectedFile.value) return
  isLoadingDb.value = true
  
  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const res = await fetch('http://127.0.0.1:8000/upload-dataset', {
      method: 'POST',
      body: formData
    })
    if (res.ok) alert("Modelo entrenado con el nuevo archivo")
  } catch (err) {
    console.error(err)
  } finally {
    isLoadingDb.value = false
  }
}

const resetMetrics = async () => {
  await fetch('http://127.0.0.1:8000/metric', { method: 'DELETE' })
  alert("Métricas borradas")
  window.location.reload();
}

onMounted(() => {
  fetchMetrics()
})
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
            <h2>Entrenamiento del Modelo</h2>
          </div>

          <div class="drop-zone" @dragover.prevent @drop.prevent="handleDrop">
            <input type="file" ref="fileInput" @change="handleFileUpload" class="hidden-input" accept=".txt"/>
            <div class="upload-content" @click="$refs.fileInput.click()">
              <div class="upload-icon">📁</div>
              <p v-if="!selectedFile">Arrastra tu archivo .txt aquí o <span>haz clic para subir</span></p>
              <p v-else class="file-name">Archivo seleccionado: {{ selectedFile.name }}</p>
            </div>
          </div>

          <button class="lunar-btn" @click="uploadDataset" :disabled="isLoadingDb || !selectedFile">
            {{ isLoadingDb ? 'Entrenando modelo...' : 'Iniciar Entrenamiento' }}
          </button>
        </section>

        <section class="glass-card">
          <div class="card-header">
            <span class="indicator active"></span>
            <h2>Centro de Telemetría</h2>
          </div>

          <div class="telemetry-layout">
            <div class="stats-summary-grid">
              <div class="stat-mini-card">
                <small>Tasa de Aceptación</small>
                <div class="value">{{ acceptanceRate }}%</div>
              </div>
              <div class="stat-mini-card">
                <small>Peticiones Totales (Tips)</small>
                <div class="value sub-indigo">{{ metrics.total_tips }}</div>
              </div>
              <div class="stat-mini-card">
                <small>Aceptadas (Tabs)</small>
                <div class="value sub-emerald">{{ metrics.total_tabs }}</div>
              </div>
            </div>

            <div class="hologram-chart-box">
              <div class="chart-axis-y">
                <span>Máx</span>
                <span>50%</span>
                <span>0</span>
              </div>
              
              <div class="chart-content">
                <div class="chart-bars-container">
                  <div class="bar-column">
                    <div class="bar-rail">
                      <div class="glow-bar tip-glow" :style="{ height: tipHeight + '%' }">
                        <div class="bar-tooltip">{{ metrics.total_tips }}</div>
                      </div>
                    </div>
                  </div>

                  <div class="bar-column">
                    <div class="bar-rail">
                      <div class="glow-bar tab-glow" :style="{ height: tabHeight + '%' }">
                        <div class="bar-tooltip">{{ metrics.total_tabs }}</div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="chart-axis-x">
                  <span class="axis-label"><i class="dot indigo-dot"></i> Peticiones (Tips)</span>
                  <span class="axis-label"><i class="dot emerald-dot"></i> Aceptadas (Tabs)</span>
                </div>
              </div>
            </div>
          </div>

          <div class="metrics-controls">
            <button class="reset-btn" @click="resetMetrics">
              <span class="icon">↺</span> Reiniciar Estadísticas
            </button>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>