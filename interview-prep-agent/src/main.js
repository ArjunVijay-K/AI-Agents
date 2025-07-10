// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './stores' // Assuming Pinia setup will be in src/stores/index.js
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'

loadFonts()

const app = createApp(App)

app.use(router)
app.use(pinia)
app.use(vuetify)

app.mount('#app')
