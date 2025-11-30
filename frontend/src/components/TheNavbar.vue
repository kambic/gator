<!-- src/components/TheNavbar.vue -->
<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="navbar bg-base-100 shadow-xl sticky top-0 z-50">
    <div class="flex-1">
      <RouterLink to="/" class="btn btn-ghost text-2xl font-bold">MyApp</RouterLink>
    </div>

    <div class="flex-none">
      <!-- Desktop menu -->
      <ul class="menu menu-horizontal px-1 hidden lg:flex">
        <li><RouterLink to="/"          active-class="bg-primary text-white">Home</RouterLink></li>
        <li><RouterLink to="/about"     active-class="bg-primary text-white">About</RouterLink></li>
        <li><RouterLink to="/dashboard" active-class="bg-primary text-white">Dashboard</RouterLink></li>
      </ul>

      <!-- Mobile hamburger -->
      <div class="dropdown dropdown-end lg:hidden">
        <label tabindex="0" class="btn btn-ghost">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </label>
        <ul tabindex="0" class="menu dropdown-content mt-3 p-2 shadow bg-base-100 rounded-box w-52">
          <li><RouterLink to="/">Home</RouterLink></li>
          <li><RouterLink to="/about">About</RouterLink></li>
          <li><RouterLink to="/dashboard">Dashboard</RouterLink></li>
        </ul>
      </div>
    </div>
  </div>
</template>
