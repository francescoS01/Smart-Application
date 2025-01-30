<template>
  <VaForm ref="form" @submit.prevent="submit">
    <h1 class="font-semibold text-4xl mb-4">Sign-in</h1>
    <p class="text-base mb-4 leading-5">
      Don't have an account yet?
      <RouterLink :to="{ name: 'signup' }" class="font-semibold text-primary">Register now</RouterLink>
    </p>
    <VaInput
      v-model="formData.email"
      :rules="[validators.required]"
      class="mb-4"
      label="Email"
      type="email"
    />
    <VaValue v-slot="isPasswordVisible" :default-value="false">
      <VaInput
        v-model="formData.password"
        :rules="[validators.required]"
        :type="isPasswordVisible.value ? 'text' : 'password'"
        class="mb-4"
        label="Password"
        @clickAppendInner.stop="isPasswordVisible.value = !isPasswordVisible.value"
      >
        <template #appendInner>
          <VaIcon
            :name="isPasswordVisible.value ? 'mso-visibility_off' : 'mso-visibility'"
            class="cursor-pointer"
            color="secondary"
          />
        </template>
      </VaInput>
    </VaValue>

    <div class="auth-layout__options flex flex-col sm:flex-row items-start sm:items-center justify-between">
      <VaCheckbox v-model="formData.keepLoggedIn" class="mb-2 sm:mb-0" label="Remember me" />
      <RouterLink :to="{ name: 'recover-password' }" class="mt-2 sm:mt-0 sm:ml-1 font-semibold text-primary">
        Forgot your password?
      </RouterLink>
    </div>

    <div class="flex justify-center mt-4">
  <VaButton class="w-full" @click="submit" :disabled="isLoading">
    <span v-if="!isLoading">Login</span>
    <VaProgressCircle v-else indeterminate size="small" color="white" />
  </VaButton>
</div>
  </VaForm>
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useForm, useToast } from 'vuestic-ui'
import { validators } from '../../services/utils'
import ServiceHTTP from '../../api/service'

const { validate } = useForm('form')
const { push } = useRouter()
const { init } = useToast()

const formData = reactive({
  email: '',
  password: '',
  keepLoggedIn: false,
})
const isLoading = ref(false)

const submit = async () => {
  if (!validate()) return

  isLoading.value = true // Mostra lo spinner di caricamento
  try {
    // Chiamata all'API per fare il login
    const token = await ServiceHTTP.login(formData.email, formData.password)

    // Salva il token nel localStorage
    localStorage.setItem('authToken', token)

    // Mostra un messaggio di successo
    init({ message: "You've successfully logged in", color: 'success' })

    // Reindirizza alla dashboard
    push({ name: 'dashboard' })
  } catch (error) {
    console.error('Login Error:', error)

    // Mostra un popup di errore
    init({ message: 'Login failed: Invalid email or password', color: 'danger' })
  } finally {
    isLoading.value = false // Nasconde lo spinner di caricamento
  }
}
</script>
