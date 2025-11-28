<script setup>
import Chart from 'chart.js/auto'

const bufferChartRef = ref()
const bitrateChartRef = ref()

function setupCharts() {
  bufferChart = new Chart(bufferChartRef.value.getContext('2d'), baseChartConfig('Buffer (s)'))
  bitrateChart = new Chart(
    bitrateChartRef.value.getContext('2d'),
    baseChartConfig('Bitrate (kbps)'),
  )
}

</script>

<template></template>

<style scoped></style>
