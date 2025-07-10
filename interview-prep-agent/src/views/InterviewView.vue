<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        <v-card v-if="!interviewStore.currentQuestion" class="pa-4 text-center">
          <v-card-title class="text-h5">Loading Interview...</v-card-title>
          <v-card-text>
            <p v-if="documentsStore.isLoading">Fetching questions...</p>
            <p v-else-if="!documentsStore.generatedQuestions.length">
              No questions generated. Please go back and upload your documents.
            </p>
            <v-btn color="primary" @click="goHome" class="mt-4">Go to Upload</v-btn>
          </v-card-text>
        </v-card>

        <v-card v-else class="pa-4 pa-md-6">
          <v-card-title class="text-h5 font-weight-medium mb-4 d-flex justify-space-between align-center">
            <span>Mock Interview</span>
            <v-chip color="primary" label>
              Question {{ interviewStore.currentQuestionNumber }} of {{ interviewStore.totalQuestions }}
            </v-chip>
          </v-card-title>

          <v-card-subtitle class="mb-4">
            Category: {{ interviewStore.currentQuestion.category || 'General' }}
          </v-card-subtitle>

          <div class="question-display pa-4 mb-6" style="background-color: #f5f5f5; border-radius: 4px;">
            <p class="text-h6">
              {{ interviewStore.currentQuestion.question }}
            </p>
          </div>

          <v-textarea
            v-model="currentAnswer"
            label="Your Answer"
            variant="outlined"
            rows="6"
            auto-grow
            class="mb-4"
            placeholder="Type your answer here..."
          />

          <div v-if="interviewStore.currentFeedback" class="feedback-display pa-3 mb-4"
               :class="interviewStore.feedbackType === 'good' ? 'bg-green-lighten-5' : 'bg-amber-lighten-5'">
            <p class="font-weight-medium">Feedback:</p>
            <p>{{ interviewStore.currentFeedback }}</p>
          </div>

          <v-row>
            <v-col cols="12" sm="auto">
              <v-btn
                color="grey"
                @click="interviewStore.previousQuestion()"
                :disabled="interviewStore.currentQuestionNumber <= 1"
                class="ma-1"
                block-sm-down
              >
                <v-icon left>mdi-chevron-left</v-icon>
                Previous
              </v-btn>
            </v-col>
            <v-spacer class="hidden-sm-and-down"></v-spacer>
            <v-col cols="12" sm="auto">
              <v-btn
                color="primary"
                @click="submitAndNext"
                :loading="interviewStore.isSubmittingAnswer"
                :disabled="!currentAnswer.trim() || interviewStore.isSubmittingAnswer"
                class="ma-1"
                block-sm-down
              >
                {{ interviewStore.isLastQuestion ? 'Submit & Finish' : 'Submit & Next' }}
                <v-icon right>{{ interviewStore.isLastQuestion ? 'mdi-check-circle-outline' : 'mdi-chevron-right' }}</v-icon>
              </v-btn>
            </v-col>
          </v-row>

          <v-divider class="my-4"></v-divider>

          <div class="text-center">
            <v-btn
              color="error"
              variant="text"
              @click="endInterviewConfirmation"
            >
              End Interview
            </v-btn>
          </div>
        </v-card>

        <!-- Confirmation Dialog for Ending Interview -->
        <v-dialog v-model="showEndConfirmation" persistent max-width="400">
          <v-card>
            <v-card-title class="text-h5">End Interview?</v-card-title>
            <v-card-text>Are you sure you want to end the mock interview? Your progress might not be fully saved if you haven't completed it.</v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="blue darken-1" text @click="showEndConfirmation = false">Cancel</v-btn>
              <v-btn color="red darken-1" text @click="confirmEndInterview">End Interview</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Interview Summary Dialog -->
         <v-dialog v-model="showSummary" persistent max-width="600">
          <v-card>
            <v-card-title class="text-h5">Interview Complete!</v-card-title>
            <v-card-text>
              <p>Great job completing the mock interview!</p>
              <!-- Summary details can go here -->
              <p v-if="interviewStore.answers.length > 0">You answered {{ interviewStore.answers.length }} questions.</p>
              <!-- Could show overall feedback or scores if implemented -->
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="primary" text @click="closeSummaryAndReset">Start New</v-btn>
              <v-btn color="secondary" text @click="showSummary = false; router.push('/');">Back to Home</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useDocumentsStore } from '@/stores/documentsStore';
import { useInterviewStore } from '@/stores/interviewStore'; // We'll create this store

const router = useRouter();
const documentsStore = useDocumentsStore();
const interviewStore = useInterviewStore(); // Initialize the new store

const currentAnswer = ref('');
const showEndConfirmation = ref(false);
const showSummary = ref(false);

// Watch for changes in the current question to clear the answer field
watch(() => interviewStore.currentQuestion, (newQuestion) => {
  currentAnswer.value = interviewStore.getCurrentAnswer() || ''; // Load saved answer if exists
  // Potentially clear feedback for the new question if feedback is per question
  // interviewStore.clearCurrentFeedback();
}, { immediate: true });


const submitAndNext = async () => {
  if (!currentAnswer.value.trim()) return;

  await interviewStore.submitAnswer(interviewStore.currentQuestion.question_id || interviewStore.currentQuestionNumber, currentAnswer.value);

  if (interviewStore.isLastQuestion && !interviewStore.isSubmittingAnswer) {
    // If it was the last question and answer submitted successfully
    showSummary.value = true;
  } else if (!interviewStore.isSubmittingAnswer) {
    // Move to next question if not last and no error during submission
    interviewStore.nextQuestion();
  }
  // currentAnswer.value = ''; // Cleared by watcher or if you prefer, here
};

const endInterviewConfirmation = () => {
  showEndConfirmation.value = true;
};

const confirmEndInterview = () => {
  showEndConfirmation.value = false;
  interviewStore.endInterview(); // Action in store to clean up
  router.push('/');
};

const closeSummaryAndReset = () => {
  showSummary.value = false;
  documentsStore.clearData(); // Clear resume/JD too for a fresh start
  interviewStore.resetInterview();
  router.push('/');
};

const goHome = () => {
  router.push('/');
}

onMounted(() => {
  if (!documentsStore.generatedQuestions || documentsStore.generatedQuestions.length === 0) {
    // If no questions are in documentsStore (e.g., page refresh on /interview),
    // try to see if they are already in interviewStore (e.g. from previous session state persistence)
    // or redirect. For now, simple redirect if documentsStore is empty.
    // A more robust solution might involve checking localStorage or fetching if an ID exists.
    console.log("No generated questions found in documents store on InterviewView mount.");
    // Potentially try to re-initialize interview from persisted state if that's implemented
    // For now, if interviewStore also doesn't have questions, it's an issue.
    if(!interviewStore.questions || interviewStore.questions.length === 0) {
        // If both are empty, definitely redirect or show error.
        // The v-if in template handles showing a message if currentQuestion is null.
    }
  }
  // Initialize the interview with questions from the documentsStore
  // This should ideally happen when 'Start Mock Interview' is clicked.
  // If navigating directly, we need a way to ensure questions are loaded.
  if (documentsStore.generatedQuestions.length > 0 && interviewStore.questions.length === 0) {
      interviewStore.startInterview(documentsStore.generatedQuestions);
  }
   // Set the current answer for the initially loaded question
  currentAnswer.value = interviewStore.getCurrentAnswer() || '';
});

</script>

<style scoped>
.question-display {
  border-left: 4px solid #1976D2; /* Vuetify primary color */
  background-color: #e3f2fd; /* A light blue, adjust as needed */
  padding: 16px;
  margin-bottom: 20px;
  border-radius: 4px;
}
.feedback-display {
  border-radius: 4px;
  border: 1px solid;
}
.bg-green-lighten-5 { /* Example for good feedback */
  background-color: #E8F5E9;
  border-color: #4CAF50;
  color: #2E7D32;
}
.bg-amber-lighten-5 { /* Example for needs improvement feedback */
  background-color: #FFF8E1;
  border-color: #FFC107;
  color: #FF8F00;
}
</style>
