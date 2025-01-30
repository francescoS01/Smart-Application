import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => {
    return {
      userName: 'Mario Rossi',
      email: 'mario@gmail.com',
      memberSince: '26/11/1980',
      pfp: 'https://picsum.photos/id/22/200/300',
      is2FAEnabled: false,
    }
  },

  actions: {
    toggle2FA() {
      this.is2FAEnabled = !this.is2FAEnabled
    },

    changeUserName(userName: string) {
      this.userName = userName
    },
  },
})
