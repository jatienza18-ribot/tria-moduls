<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-100 p-4">
    <div class="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 max-w-sm w-full">
      <div class="mb-8 text-center">
        <h1 class="text-2xl font-extrabold text-slate-900">Tria de Mòduls</h1>
        <p class="text-slate-500 text-sm mt-1">Accés per a Caps de Departament i Direcció</p>
      </div>

      <form @submit.prevent="handleLogin" class="flex flex-col gap-4">
        <div>
          <label class="block text-sm font-bold text-slate-700 mb-1">Codi d'Usuari</label>
          <input v-model="username" type="text" placeholder="Ex: inf, fol, admin" class="w-full border border-slate-300 rounded-lg p-3 outline-none focus:border-brand-blue" required />
        </div>
        <div>
          <label class="block text-sm font-bold text-slate-700 mb-1">Contrasenya</label>
          <input v-model="password" type="password" placeholder="••••••••" class="w-full border border-slate-300 rounded-lg p-3 outline-none focus:border-brand-blue" required />
        </div>

        <div v-if="error" class="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-2 font-medium border border-red-100">
          {{ error }}
        </div>

        <button type="submit" class="bg-brand-blue text-white rounded-lg p-3 font-bold hover:bg-blue-600 transition-colors shadow-sm">
          <span v-if="isLoading">Accedint...</span>
          <span v-else>Iniciar Sessió</span>
        </button>
      </form>
      
      <div class="mt-6 text-center text-sm border-t pt-4 border-slate-100">
          <p class="text-slate-500">Ets docent general?</p>
          <router-link to="/" class="text-brand-blue font-bold hover:underline">Ves a l'Altaveu Públic</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const username = ref('');
const password = ref('123'); // Preset for test convenience
const error = ref('');
const isLoading = ref(false);

const backendUrl = 'http://localhost:8001';

const handleLogin = async () => {
  error.value = '';
  isLoading.value = true;
  try {
    const res = await fetch(`${backendUrl}/tria/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.value, password: password.value })
    });
    
    if (!res.ok) {
        error.value = "Credencials incorrectes.";
        return;
    }
    
    const data = await res.json();
    localStorage.setItem('tria_session', JSON.stringify(data));
    
    if (data.rol === 'ADMIN') {
        router.push('/admin');
    } else {
        router.push('/dept');
    }
  } catch (e) {
    error.value = "Error al connectar amb el servidor.";
  } finally {
    isLoading.value = false;
  }
};
</script>
