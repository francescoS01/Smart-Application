<template>
  <h1 class="page-title font-bold">Report</h1>
  <section class="flex flex-col gap-4">
    <VaCard>
      <VaCardTitle class="flex justify-between">
        <h1 class="card-title text-secondary font-bold uppercase">Reports</h1>
      </VaCardTitle>
      <VaCardContent class="flex flex-col gap-1">
        <div class="flex justify-between">
          <VaButtonToggle v-model="selectedPeriod" :options="periods" color="background-element" size="small" />
          <div></div>
        </div>

        <VaDataTable
          class="notifications-table"
          :columns="[
            { key: 'date', label: 'Date' },
            { key: 'download', label: 'Download PDF' },
          ]"
          :items="filteredData"
        >
          <template #cell(download)="{ rowData }">
            <div class="flex items-center">
              <VaButton size="small" icon="download" @click="downloadPDF()">PDF</VaButton>
            </div>
          </template>
        </VaDataTable>
      </VaCardContent>
    </VaCard>
  </section>
</template>

<script setup lang="ts">
import { ref, Ref, computed } from 'vue'
import { downloadAsCSV } from '../../../services/toCSV'

const selectedPeriod = ref('Today') as Ref<'Today' | 'Week' | 'Month'>
const periods = ['Today', 'Week', 'Month'].map((period) => ({ label: period, value: period }))

// Funzione per filtrare le notifiche in base al periodo selezionato
const filteredData = computed(() => {
  if (selectedPeriod.value === 'Today') {
    return report.value.slice(0, 3)
  } else if (selectedPeriod.value === 'Week') {
    return report.value.slice(0, 9)
  } else if (selectedPeriod.value === 'Month') {
    return report.value
  }
  return []
})

const report = ref([
  {
    date: '2024-11-19',
    download: '',
  },
  {
    date: '2024-11-19',
    download: '',
  },
  {
    date: '2024-11-19',
    download: '',
  },
  {
    date: '2024-11-18', // 3 escluso
    download: '',
  },
  {
    date: '2024-11-18',
    download: '',
  },
  {
    date: '2024-11-16',
    download: '',
  },
  {
    date: '2024-11-15',
    download: '',
  },
  {
    date: '2024-11-14',
    download: '',
  },
  {
    date: '2024-11-13',
    download: '',
  },
  {
    date: '2024-10-21', // 9 escluso
    download: '',
  },
  {
    date: '2024-10-21',
    download: '',
  },
  {
    date: '2024-10-20',
    download: '',
  },
])

const downloadPDF = () => {
  downloadAsCSV(report.value, 'region-revenue')
}
</script>

<style lang="scss" scoped>
.notifications-table {
  ::v-deep(tbody) {
    tr {
      border-top: 1px solid var(--va-background-border);
    }
  }
}
</style>
