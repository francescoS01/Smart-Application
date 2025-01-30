<template>
  <VaDropdown :offset="[13, 0]" class="notification-dropdown" stick-to-edges :close-on-content-click="false">
    <template #anchor>
      <VaButton preset="secondary" color="textPrimary">
        <VaBadge overlap>
          <template #text> 2+</template>
          <VaIconNotification class="notification-dropdown__icon" />
        </VaBadge>
      </VaButton>
    </template>
    <VaDropdownContent class="h-full sm:max-w-[420px] sm:h-auto">
      <section class="sm:max-h-[320px] p-4 overflow-auto">
        <VaList class="space-y-1 mb-2">
          <template v-for="(item, index) in notificationsWithRelativeTime" :key="item.id">
            <VaListItem class="text-base">
              <VaListItemSection icon class="mx-0 p-0">
                <VaIcon :name="item.icon" color="secondary" />
              </VaListItemSection>
              <VaListItemSection>
                <span :style="{ color: getStatusColor(item.status) }">
                  {{ item.message }}
                </span>
              </VaListItemSection>
              <VaListItemSection icon class="mx-1">
                {{ item.updateTimestamp }}
              </VaListItemSection>
            </VaListItem>
            <VaListSeparator v-if="item.separator && index !== notificationsWithRelativeTime.length - 1" class="mx-3" />
          </template>
        </VaList>

        <VaButton preset="primary" class="w-full" @click="redirectTo('history')">See all notification </VaButton>
      </section>
    </VaDropdownContent>
  </VaDropdown>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import VaIconNotification from '../../../icons/VaIconNotification.vue'

const { t, locale } = useI18n()
const router = useRouter()
const baseNumberOfVisibleNotifications = 4
const rtf = new Intl.RelativeTimeFormat(locale.value, { style: 'short' })
const displayAllNotifications = ref(false)

interface INotification {
  message: string
  icon: string
  id: number
  separator?: boolean
  updateTimestamp: Date
  status: string
}

function redirectTo(routeName: string) {
  router.push({ name: routeName }).catch((err) => {
    // Gestione degli errori (opzionale), ad esempio rotta inesistente
    if (err.name !== 'NavigationDuplicated') {
      console.error(err)
    }
  })
}

const makeDateFromNow = (timeFromNow: number) => {
  const date = new Date()
  date.setTime(date.getTime() + timeFromNow)
  return date
}

const notifications: INotification[] = [
  {
    message: 'Low oil pressure',
    icon: 'battery_1_bar',
    id: 2,
    separator: true,
    updateTimestamp: makeDateFromNow(-3 * 60 * 60 * 1000),
    status: 'Low',
  },
  {
    message: 'Critical component failure',
    icon: 'alarm',
    id: 6,
    separator: true,
    updateTimestamp: makeDateFromNow(-9 * 60 * 60 * 1000),
    status: 'High',
  },
  {
    message: 'Machine overheated',
    icon: 'trending_down',
    id: 7,
    separator: false,
    updateTimestamp: makeDateFromNow(-1 * 60 * 60 * 1000),
    status: 'Low',
  },
  {
    message: 'Sensor malfunction detected',
    icon: 'trending_down',
    id: 7,
    separator: false,
    updateTimestamp: makeDateFromNow(-1 * 60 * 60 * 1000),
    status: 'Medium',
  }
].sort((a, b) => new Date(b.updateTimestamp).getTime() - new Date(a.updateTimestamp).getTime())

const TIME_NAMES = {
  second: 1000,
  minute: 1000 * 60,
  hour: 1000 * 60 * 60,
  day: 1000 * 60 * 60 * 24,
  week: 1000 * 60 * 60 * 24 * 7,
  month: 1000 * 60 * 60 * 24 * 30,
  year: 1000 * 60 * 60 * 24 * 365,
}

const getTimeName = (differenceTime: number) => {
  return Object.keys(TIME_NAMES).reduce(
    (acc, key) => (TIME_NAMES[key as keyof typeof TIME_NAMES] < differenceTime ? key : acc),
    'month',
  ) as keyof typeof TIME_NAMES
}

const notificationsWithRelativeTime = computed(() => {
  const list = displayAllNotifications.value ? notifications : notifications.slice(0, baseNumberOfVisibleNotifications)

  return list.map((item, index) => {
    const timeDifference = Math.round(new Date().getTime() - new Date(item.updateTimestamp).getTime())
    const timeName = getTimeName(timeDifference)

    let separator = false

    const nextItem = list[index + 1]
    if (nextItem) {
      const nextItemDifference = Math.round(new Date().getTime() - new Date(nextItem.updateTimestamp).getTime())
      const nextItemTimeName = getTimeName(nextItemDifference)

      if (timeName !== nextItemTimeName) {
        separator = true
      }
    }

    return {
      ...item,
      updateTimestamp: rtf.format(-1 * Math.round(timeDifference / TIME_NAMES[timeName]), timeName).replace('fa', 'ago'),
      separator,
    }
  })
})

// Funzione per determinare il colore in base allo stato
const getStatusColor = (status: string): string => {
  switch (status) {
    case 'Low':
      return 'green' // Colore verde per stato Low
    case 'Medium':
      return 'orange' // Colore arancione per stato Medium
    case 'High':
      return 'red' // Colore rosso per stato High
    default:
      return 'black' // Colore di default se lo stato è sconosciuto
  }
}
</script>

<style lang="scss" scoped>
.notification-dropdown {
  cursor: pointer;

  .notification-dropdown__icon {
    position: relative;
    display: flex;
    align-items: center;
  }

  .va-dropdown__anchor {
    display: inline-block;
  }
}
</style>
