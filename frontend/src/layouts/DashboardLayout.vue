<!-- src/layouts/DashboardLayout.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'

// Sidebar collapse state (mobile + optional desktop toggle)
const sidebarOpen = ref(false)
</script>

<template>
  <div class="drawer lg:drawer-open">
    <input id="sidebar-drawer" type="checkbox" class="drawer-toggle" v-model="sidebarOpen" />

    <!-- Main page content -->
    <div class="drawer-content flex flex-col">
      <!-- Top Navbar -->
      <div class="navbar bg-base-100 shadow-md px-4">
        <div class="flex-none lg:hidden">
          <label for="sidebar-drawer" class="btn btn-square btn-ghost drawer-button">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </label>
        </div>

        <div class="flex-1">
          <h1 class="text-xl font-semibold">My Dashboard</h1>
        </div>

        <div class="flex-none">
          <!-- User dropdown or notifications -->
          <div class="dropdown dropdown-end">
            <label tabindex="0" class="btn btn-ghost btn-circle avatar">
              <div class="w-10 rounded-full">
                <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=admin" alt="User" />
              </div>
            </label>
            <ul tabindex="0" class="menu dropdown-content mt-3 p-2 shadow bg-base-100 rounded-box w-52">
              <li><a>Profile</a></li>
              <li><a>Settings</a></li>
              <li><a class="text-error">Logout</a></li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Page Content -->
      <div class="flex-1 p-6 bg-base-200">
        <RouterView />
      </div>
    </div>

    <!-- Sidebar -->
    <div class="drawer-side">
      <label for="sidebar-drawer" class="drawer-overlay"></label>
      <aside class="w-64 h-full bg-base-100 shadow-xl flex flex-col">
        <!-- Logo -->
        <div class="p-6 border-b border-base-300">
          <RouterLink to="/dashboard" class="text-2xl font-bold flex items-center gap-3">
            <div class="w-10 h-10 bg-primary rounded-lg flex items-center justify-center text-white">A</div>
            Admin
          </RouterLink>
        </div>

        <!-- Navigation Menu -->
        <ul class="menu p-4 flex-1">
          <li>
            <RouterLink to="/dashboard" active-class="bg-primary text-white" exact>
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
              </svg>
              Dashboard
            </RouterLink>
          </li>
          <li>
            <RouterLink to="/dashboard/users" active-class="bg-primary text-white">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
              </svg>
              Users
            </RouterLink>
          </li>
          <li>
            <RouterLink to="/dashboard/files" active-class="bg-primary text-white">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              Files
            </RouterLink>
          </li>
          <li>
            <RouterLink to="/dashboard/settings" active-class="bg-primary text-white">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.337.435 2.202 1.826 2.202 3.182 0 1.356-.865 2.747-2.202 3.182-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 01-2.202-3.182c0-1.356.865-2.747 2.202-3.182zM14 8a2 2 0 10-4 0 2 2 0 004 0z"/>
              </svg>
              Settings
            </RouterLink>
          </li>
        </ul>

        <!-- Footer in sidebar (optional) -->
        <div class="p-4 border-t border-base-300 text-sm text-center text-base-content/70">
          v1.0.0
        </div>
      </aside>
    </div>
  </div>
</template>
