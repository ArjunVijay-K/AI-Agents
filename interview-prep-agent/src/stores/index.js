// src/stores/index.js
import { createPinia } from 'pinia'

const pinia = createPinia()

export default pinia

// You can define your stores in separate files within this directory
// e.g., src/stores/interviewStore.js
/*
import { defineStore } from 'pinia'

export const useInterviewStore = defineStore('interview', {
  state: () => ({
    resumeText: null,
    jobDescriptionText: null,
    questions: [],
    currentQuestionIndex: 0,
    // ... other relevant state
  }),
  actions: {
    setResumeText(text) {
      this.resumeText = text;
    },
    setJobDescriptionText(text) {
      this.jobDescriptionText = text;
    },
    // ... other actions
  },
  getters: {
    currentQuestion: (state) => {
      return state.questions.length > 0 ? state.questions[state.currentQuestionIndex] : null;
    }
  }
})
*/
