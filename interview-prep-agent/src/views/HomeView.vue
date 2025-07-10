<template>
  <v-container>
    <v-row class="text-center mb-6">
      <v-col cols="12">
        <v-img :src="logo" class="my-3" contain height="150" />
        <h1 class="text-h4 font-weight-bold mb-2">
          AI Interview Prep Agent
        </h1>
        <p class="text-subtitle-1">
          Upload your resume and job description to get tailored interview questions.
        </p>
      </v-col>
    </v-row>

    <v-row justify="center">
      <v-col cols="12" md="8" lg="7">
        <v-card class="pa-4 pa-md-6" elevation="2">
          <v-card-title class="text-h5 font-weight-medium mb-4">
            Step 1: Provide Your Details
          </v-card-title>
          <v-card-text>
            <v-form @submit.prevent="handleSubmit">
              <v-file-input
                v-model="resumeFileModel"
                label="Upload Resume/CV"
                prepend-icon="mdi-file-document-outline"
                variant="outlined"
                accept=".pdf,.doc,.docx"
                :rules="[rules.requiredFile]"
                class="mb-4"
                clearable
                show-size
                @change="handleFileChange"
              />

              <v-textarea
                v-model="jobDescriptionModel"
                label="Paste Job Description"
                prepend-inner-icon="mdi-text-box-outline"
                variant="outlined"
                rows="8"
                auto-grow
                :rules="[rules.requiredText]"
                class="mb-4"
                clearable
              />

              <v-alert
                v-if="documentsStore.error"
                type="error"
                density="compact"
                class="mb-4"
                closable
                @click:close="documentsStore.error = null"
              >
                {{ documentsStore.error }}
              </v-alert>

              <v-alert
                v-if="documentsStore.successMessage && !documentsStore.generatedQuestions.length"
                type="info"
                density="compact"
                class="mb-4"
                closable
                @click:close="documentsStore.successMessage = ''"
              >
                {{ documentsStore.successMessage }}
              </v-alert>

              <v-btn
                :loading="documentsStore.isLoading"
                :disabled="documentsStore.isLoading"
                color="primary"
                block
                size="large"
                type="submit"
                class="mb-2"
              >
                <v-icon left class="mr-2">mdi-arrow-right-circle-outline</v-icon>
                Upload & Generate Questions
              </v-btn>
              <v-btn
                v-if="documentsStore.uploadedResumeText || documentsStore.generatedQuestions.length"
                color="grey"
                variant="text"
                block
                size="small"
                @click="handleClearData"
                class="mt-2"
              >
                Clear Data & Start Over
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-if="documentsStore.isLoading && !documentsStore.generatedQuestions.length" justify="center" class="mt-6">
        <v-col cols="auto">
            <v-progress-circular indeterminate color="primary" size="64" />
            <p class="mt-2 text-center">Processing your documents and generating questions...</p>
        </v-col>
    </v-row>

    <v-row v-if="!documentsStore.isLoading && documentsStore.generatedQuestions.length > 0" justify="center" class="mt-8">
      <v-col cols="12" md="10" lg="8">
        <v-card class="pa-4 pa-md-6" elevation="2">
          <v-card-title class="text-h5 font-weight-medium mb-4 d-flex justify-space-between align-center">
            <span>Step 2: Your Mock Interview Questions</span>
            <v-chip color="green" text-color="white" small>
              <v-icon start>mdi-check-circle</v-icon>
              Ready
            </v-chip>
          </v-card-title>
          <v-card-text>
            <p class="mb-4">Here are some questions tailored for you. Prepare your answers!</p>
            <v-list lines="two" density="compact">
              <v-list-item
                v-for="(q, index) in documentsStore.generatedQuestions"
                :key="index"
                :title="`${index + 1}. ${q.question}`"
                :subtitle="`Category: ${q.category || 'General'}`"
                class="mb-2"
              >
                <template v-slot:prepend>
                  <v-icon color="primary">mdi-chat-question-outline</v-icon>
                </template>
              </v-list-item>
            </v-list>

            <v-divider class="my-4"></v-divider>

            <v-alert
              v-if="documentsStore.successMessage"
              type="success"
              density="compact"
              class="mt-4"
              closable
              @click:close="documentsStore.successMessage = ''"
            >
              {{ documentsStore.successMessage }}
            </v-alert>

            <div class="mt-6 text-center">
                <p class="text-subtitle-1">Next steps would be to start a mock interview session.</p>
                <v-btn color="secondary" class="mt-2" @click="startMockInterview">
                    <v-icon left class="mr-2">mdi-microphone</v-icon>
                    Start Mock Interview (Coming Soon)
                </v-btn>
            </div>

          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

  </v-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useDocumentsStore } from '@/stores/documentsStore';
import { useInterviewStore } from '@/stores/interviewStore';
import logo from '@/assets/logo.svg';

const router = useRouter();
const documentsStore = useDocumentsStore();
const interviewStore = useInterviewStore();

const resumeFileModel = ref(null); // For v-file-input, it expects an array by default if not `multiple=false`
                                 // Vuetify 3 v-file-input v-model is an array of File objects or a single File object if not multiple.
                                 // Let's assume single file for resume.

const jobDescriptionModel = computed({
  get: () => documentsStore.jobDescription,
  set: (val) => documentsStore.setJobDescription(val)
});

const rules = {
  requiredFile: value => {
    // Check if value is null, or an empty array, or if the first element is null
    if (!value || (Array.isArray(value) && value.length === 0) || (Array.isArray(value) && !value[0])) {
      return 'Resume file is required.';
    }
    return true;
  },
  requiredText: value => !!(value && value.trim()) || 'Job description cannot be empty.',
};

// Watch for changes in resumeFileModel (from v-file-input) and update store's resumeFile
// v-file-input's v-model can be an array of files. We take the first one.
watch(resumeFileModel, (newFiles) => {
  if (newFiles && newFiles.length > 0) {
    documentsStore.setResumeFile(newFiles[0]);
  } else {
    documentsStore.setResumeFile(null);
  }
});


const handleSubmit = async () => {
  // Use the store's resumeFile for validation as it's directly updated by the watcher
  if (!documentsStore.resumeFile || !jobDescriptionModel.value.trim()) {
    documentsStore.error = 'Please provide both a resume file and a job description.';
    return;
  }

  await documentsStore.uploadAndProcessDocuments();
  // UI will update based on store changes (show questions section or error)
};

const handleClearData = () => {
  documentsStore.clearData();
  interviewStore.resetInterview();
  resumeFileModel.value = []; // Reset the file input model (Vuetify expects an array)
};

const startMockInterview = () => {
  if (documentsStore.generatedQuestions && documentsStore.generatedQuestions.length > 0) {
    interviewStore.startInterview(documentsStore.generatedQuestions);
    router.push('/interview');
  } else {
    documentsStore.error = "No questions available. Please upload documents and generate questions first.";
  }
};

</script>

<style scoped>
.v-img {
  margin-left: auto;
  margin-right: auto;
}
.v-card {
  transition: box-shadow 0.3s ease-in-out;
}
.v-card:hover {
  box-shadow: 0px 4px 20px rgba(0,0,0,0.1) !important;
}
</style>
