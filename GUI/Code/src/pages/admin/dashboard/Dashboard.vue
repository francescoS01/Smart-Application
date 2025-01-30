<script lang="ts" setup>
import RevenueUpdates from './cards/RevenueReport.vue'
import Notifications from './cards/Notifications.vue'
import ProjectTable from './cards/ProjectTable.vue'
import DataSection from './DataSection.vue'
import MonthlyEarnings from './cards/MonthlyEarnings.vue'
import RegionRevenue from './cards/RegionRevenue.vue'
import RevenueByLocationMap from './cards/RevenueByLocationMap.vue'
import Timeline from './cards/Timeline.vue'
</script>

<template>
  <h1 class="page-title font-bold">Dashboard</h1>
  <section class="flex flex-col gap-4">
    <div class="flex flex-col sm:flex-row gap-4">
      <MonthlyEarnings class="w-full sm:w-[70%]" />
      <DataSection class="flex gap-4 w-full sm:w-[30%]" />
    </div>

    <Notifications />
  </section>
</template>
