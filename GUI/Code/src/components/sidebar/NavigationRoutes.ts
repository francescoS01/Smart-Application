export interface INavigationRoute {
  name: string
  displayName: string
  meta: { icon: string }
  children?: INavigationRoute[]
}

export default {
  root: {
    name: '/',
    displayName: 'navigationRoutes.home',
  },
  routes: [
    {
      name: 'dashboard',
      displayName: 'menu.dashboard',
      meta: {
        icon: 'vuestic-iconset-dashboard',
      },
    },
    {
      name: 'kpi',
      displayName: 'KPI',
      meta: {
        icon: 'folder_shared',
      },
    },
    {
      name: 'history',
      displayName: 'History',
      meta: {
        icon: 'folder_shared',
      },
    },
    {
      name: 'chatbot',
      displayName: 'Chatbot',
      meta: {
        icon: 'folder_shared',
      },
    },
    {
      name: 'preferences',
      displayName: 'Profile',
      meta: {
        icon: 'folder_shared',
      },
    },
    {
      name: 'report',
      displayName: 'Report',
      meta: {
        icon: 'folder_shared',
      },
    },
    {
      name: 'settings',
      displayName: 'Settings',
      meta: {
        icon: 'folder_shared',
      },
    },
  ] as INavigationRoute[],
}
