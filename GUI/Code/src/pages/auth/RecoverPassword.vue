<template>
  <VaForm ref="passwordForm" @submit.prevent="submit">
    <h1 class="font-semibold text-4xl mb-4">Forgot your password?</h1>
    <p class="text-base mb-4 leading-5">
      If you've forgotten your password, don't worry. Enter your email address below, and we'll send you an email
      to set a new password.
    </p>
    <VaInput
      v-model="email"
      :rules="[(v) => !!v || 'Email field is required']"
      class="mb-4"
      label="Insert your email"
      type="email"
    />
    <VaButton class="w-full mb-2" @click="submit">Confirm</VaButton>
    <VaButton :to="{ name: 'login' }" class="w-full" preset="secondary" @click="submit">Go back</VaButton>
  </VaForm>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { useForm } from 'vuestic-ui'
import { useRouter } from 'vue-router'

const email = ref('')
const form = useForm('passwordForm')
const router = useRouter()

const submit = () => {
  if (form.validate()) {
    router.push({ name: 'recover-password-email' })
  }
}
</script>
