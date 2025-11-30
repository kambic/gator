// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: DefaultLayout,
      children: [
        { path: '', name: 'home', component: () => import('@/views/HomeView.vue') },
        { path: 'about', component: () => import('@/views/AboutView.vue') },
        { path: 'dashboard', component: () => import('@/views/dashboard/Home.vue') },
      ],
    },
    {
      path: '/auth',
      component: AuthLayout,
      children: [
        { path: 'login', component: () => import('@/views/auth/LoginView.vue') },
        { path: 'register', component: () => import('@/views/auth/RegisterView.vue') },
      ],
    },
    {
      path: '/dashboard',
      component: () => import('@/layouts/DashboardLayout.vue'),
      children: [
        { path: '', component: () => import('@/views/dashboard/Home.vue') },
        { path: 'users', component: () => import('@/views/dashboard/Users.vue') },
        { path: 'files', component: () => import('@/views/dashboard/Files.vue') },
      ],
    },
  ],
})

export default router
