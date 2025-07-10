import { defineStore } from 'pinia';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Backend API

export const useInterviewStore = defineStore('interview', {
  state: () => ({
    questions: [], // Full list of questions for the current interview
    currentQuestionIndex: 0,
    answers: [], // Stores { question_id, answer_text, feedback }
    isLoading: false, // For loading questions or general state
    isSubmittingAnswer: false, // Specifically for answer submission
    error: null,
    currentFeedback: null, // Feedback for the current answer
    feedbackType: 'info', // 'info', 'good', 'improvement'
    interviewEnded: false,
  }),
  getters: {
    totalQuestions: (state) => state.questions.length,
    currentQuestionNumber: (state) => state.currentQuestionIndex + 1,
    currentQuestion: (state) => {
      if (state.questions.length > 0 && state.currentQuestionIndex < state.questions.length) {
        // Add a temporary question_id if not present, for tracking answers
        // In a real scenario, backend should provide unique IDs for questions
        return {
            ...state.questions[state.currentQuestionIndex],
            question_id: state.questions[state.currentQuestionIndex].id || `q_${state.currentQuestionIndex}`
        };
      }
      return null;
    },
    isLastQuestion: (state) => state.currentQuestionIndex === state.questions.length - 1,
    allAnswersSubmitted: (state) => state.answers.length === state.questions.length,
    getCurrentAnswer: (state) => {
        const q = state.currentQuestion;
        if (!q) return '';
        const existingAnswer = state.answers.find(a => a.question_id === q.question_id);
        return existingAnswer ? existingAnswer.answer_text : '';
    }
  },
  actions: {
    startInterview(questionsList) {
      this.questions = questionsList.map((q, index) => ({...q, question_id: q.id || `q_${index}`}));
      this.currentQuestionIndex = 0;
      this.answers = [];
      this.error = null;
      this.currentFeedback = null;
      this.interviewEnded = false;
      this.isLoading = false;
      // Potentially persist to localStorage if needed
    },
    nextQuestion() {
      this.currentFeedback = null; // Clear feedback when moving to next question
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++;
      }
    },
    previousQuestion() {
      this.currentFeedback = null;
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--;
      }
    },
    async submitAnswer(questionId, answerText) {
      if (!answerText.trim()) {
        this.error = "Answer cannot be empty.";
        return;
      }
      this.isSubmittingAnswer = true;
      this.error = null;
      this.currentFeedback = null;

      // Store the answer locally first
      const answerIndex = this.answers.findIndex(a => a.question_id === questionId);
      if (answerIndex > -1) {
        this.answers[answerIndex] = { ...this.answers[answerIndex], answer_text: answerText, feedback: null };
      } else {
        this.answers.push({ question_id: questionId, answer_text: answerText, feedback: null });
      }

      // --- Placeholder for backend API call to get feedback ---
      // This is where you would send the question and answer to the backend
      // and the backend Llama model would provide feedback.
      try {
        // Simulate API call for feedback
        // const response = await axios.post(`${API_BASE_URL}/get-feedback/`, {
        //   question: this.currentQuestion.question,
        //   answer: answerText,
        // });
        // this.currentFeedback = response.data.feedback_text;
        // this.feedbackType = response.data.suggestions ? 'improvement' : 'good';

        // Simulate delay and dummy feedback
        await new Promise(resolve => setTimeout(resolve, 1000));
        if (answerText.toLowerCase().includes("synergy") || answerText.length < 20) {
            this.currentFeedback = "This answer could be more specific. Try to use the STAR method to structure your response with concrete examples.";
            this.feedbackType = 'improvement';
        } else {
            this.currentFeedback = "Good answer! Clear and concise.";
            this.feedbackType = 'good';
        }
        // Update the stored answer with feedback
        const updatedAnswerIndex = this.answers.findIndex(a => a.question_id === questionId);
        if (updatedAnswerIndex > -1) {
            this.answers[updatedAnswerIndex].feedback = this.currentFeedback;
        }

      } catch (err) {
        if (err.response && err.response.data && err.response.data.detail) {
          this.error = `Feedback Error: ${err.response.data.detail}`;
        } else {
          this.error = 'Feedback Error: Could not get feedback from server.';
        }
        // Even if feedback fails, the answer is stored locally.
      } finally {
        this.isSubmittingAnswer = false;
      }
    },
    endInterview() {
      this.interviewEnded = true;
      // Could do a final summary/save operation here
      console.log("Interview ended. Final answers:", JSON.parse(JSON.stringify(this.answers)));
      // Don't clear questions here, allow review until reset.
    },
    resetInterview() {
      this.questions = [];
      this.currentQuestionIndex = 0;
      this.answers = [];
      this.isLoading = false;
      this.isSubmittingAnswer = false;
      this.error = null;
      this.currentFeedback = null;
      this.interviewEnded = false;
    },
    // Action to be called if questions need to be loaded directly into interview store
    // e.g. if user bookmarks /interview page and we need to re-fetch or load from session
    async loadQuestionsFromSource() {
        // This is a placeholder. In a real app, you might:
        // 1. Check if there's an active interview ID in localStorage/sessionStorage
        // 2. Make an API call to fetch questions for that interview ID
        // For now, this assumes questions are passed from documentsStore or are already populated
        if (this.questions.length === 0) {
            console.warn("Attempted to load questions, but no source logic implemented yet and no questions available.");
            // this.error = "Could not load interview questions.";
            // this.router.push('/'); // or redirect
        }
    }
  },
});
