<!-- src/layouts/DefaultLayout.vue -->
<template>
  <div class="min-h-screen flex flex-col">
    <!-- Navbar -->
    <header>
      <TheNavbar />
    </header>

    <!-- Main content -->
    <main class="flex-1 bg-base-200">
      <slot /> <!-- Page content goes here -->
    </main>

    <!-- Optional Footer -->
    <footer class="footer footer-center p-6 bg-base-300 text-base-content">
      <p>© 2025 MyApp – Built with Vue 3 + DaisyUI</p>
    </footer>
  </div>
</template>
