// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import InterviewView from '../views/InterviewView.vue' // Import the new view

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/interview',
    name: 'interview',
    component: InterviewView,
    // You might want to add a meta field or a beforeEnter guard
    // to ensure questions are loaded before accessing this route.
    // meta: { requiresQuestions: true }
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
