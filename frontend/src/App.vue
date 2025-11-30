<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <!-- Navbar with DaisyUI styling -->
  <div class="navbar bg-base-100 shadow-lg sticky top-0 z-50">
    <div class="flex-1">
      <!-- Optional: Add a logo or brand name -->
      <RouterLink to="/" class="btn btn-ghost text-xl font-bold">
        MyApp
      </RouterLink>
    </div>

    <div class="flex-none">
      <ul class="menu menu-horizontal px-1">
        <li>
          <RouterLink
            to="/"
            class="rounded-lg"
            active-class="bg-primary text-primary-content"
            exact-active-class="bg-primary text-primary-content"
          >
            Home
          </RouterLink>
        </li>
        <li>
          <RouterLink
            to="/about"
            class="rounded-lg"
            active-class="bg-primary text-primary-content"
          >
            About
          </RouterLink>
        </li>
        <li>
          <RouterLink
            to="/files"
            class="rounded-lg"
            active-class="bg-primary text-primary-content"
          >
            Files
          </RouterLink>
        </li>
      </ul>
    </div>
  </div>

  <!-- Main content area -->
  <main class="min-h-screen bg-base-200">
    <div class="container mx-auto px-4 py-8">
      <RouterView />
    </div>
  </main>
</template>

<!-- No custom CSS needed! DaisyUI + Tailwind handles everything -->
