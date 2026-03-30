<template>
  <div class="max-w-4xl mx-auto w-full flex flex-col pt-8">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-3">
        Administració (Cap d'Estudis)
      </h1>
      <button @click="$emit('exit')" class="bg-white border border-slate-200 text-slate-700 px-4 py-2 rounded-xl font-medium hover:bg-slate-50">
        Tornar a la Tria
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Gestió de l'Estat -->
      <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col gap-4">
        <h2 class="text-xl font-bold border-b pb-2">Estat del Sistema</h2>
        
        <div class="flex flex-col gap-2">
          <label class="text-sm font-bold text-slate-600">Fase del Procés:</label>
          <select v-model="localState.fase" class="border border-slate-300 rounded-lg p-2 bg-slate-50">
            <option value="PREPARACIO">Preparació (Tancat)</option>
            <option value="OBERT">Obert (En curs)</option>
            <option value="FINALITZAT">Finalitzat</option>
          </select>
        </div>

        <div class="flex flex-col gap-2 mt-2">
          <label class="text-sm font-bold text-slate-600">Forçar Torn Actual:</label>
          <select v-model="localState.torn_actual" class="border border-slate-300 rounded-lg p-2 bg-slate-50">
            <option :value="null">-- Cap --</option>
            <option v-for="user in localState.ordre" :key="user" :value="user">
              {{ user }}
            </option>
          </select>
        </div>
      </div>

      <!-- Gestió de l'Ordre -->
      <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col gap-4">
        <div class="flex justify-between items-center border-b pb-2">
            <h2 class="text-xl font-bold">Ordre de Prioritat</h2>
            <button @click="addDocent" class="text-xs bg-brand-blue text-white px-2 py-1 rounded">Afegir +</button>
        </div>

        <div class="flex flex-col gap-2 max-h-64 overflow-y-auto no-scrollbar">
          <div v-for="(user, idx) in localState.ordre" :key="idx" class="flex items-center gap-2 bg-slate-50 p-2 border border-slate-100 rounded">
            <span class="font-bold text-slate-400 w-6">{{ idx + 1 }}.</span>
            <input v-model="localState.ordre[idx]" class="flex-1 bg-white border border-slate-200 p-1 rounded text-sm" />
            
            <div class="flex gap-1 ml-auto">
              <button @click="moveUp(idx)" :disabled="idx === 0" class="p-1 bg-slate-200 rounded disabled:opacity-30">↑</button>
              <button @click="moveDown(idx)" :disabled="idx === localState.ordre.length - 1" class="p-1 bg-slate-200 rounded disabled:opacity-30">↓</button>
              <button @click="removeDocent(idx)" class="p-1 bg-red-100 text-red-600 rounded">✕</button>
            </div>
          </div>
          <div v-if="localState.ordre.length === 0" class="text-sm text-slate-500 italic">No hi ha docents a l'ordre.</div>
        </div>
      </div>
    </div>

    <div class="mt-6 flex justify-end gap-4 p-4 bg-white border border-slate-200 rounded-xl shadow-sm">
      <button @click="syncData" class="px-6 py-2 rounded-lg font-bold text-slate-600 hover:bg-slate-50">
        Desfer Canvis
      </button>
      <button @click="saveState" class="bg-emerald-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-emerald-700 shadow flex items-center gap-2">
        <span v-if="isSaving">Guardant...</span>
        <span v-else>Aplicar Estat a Tothom</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';

const props = defineProps(['state', 'backendUrl']);
const emit = defineEmits(['exit']);

const localState = ref({
  fase: 'PREPARACIO',
  torn_actual: null,
  ordre: []
});

const isSaving = ref(false);

const syncData = () => {
  localState.value = JSON.parse(JSON.stringify(props.state));
  if (!localState.value.ordre) localState.value.ordre = [];
};

watch(() => props.state, syncData, { deep: true, immediate: true });

const moveUp = (idx) => {
  if (idx > 0) {
    const temp = localState.value.ordre[idx - 1];
    localState.value.ordre[idx - 1] = localState.value.ordre[idx];
    localState.value.ordre[idx] = temp;
  }
};

const moveDown = (idx) => {
  if (idx < localState.value.ordre.length - 1) {
    const temp = localState.value.ordre[idx + 1];
    localState.value.ordre[idx + 1] = localState.value.ordre[idx];
    localState.value.ordre[idx] = temp;
  }
};

const addDocent = () => {
    const nom = prompt("Introdueix l'ID del docent (ex: profe_nou):");
    if(nom) localState.value.ordre.push(nom);
};

const removeDocent = (idx) => {
    localState.value.ordre.splice(idx, 1);
};

const saveState = async () => {
  isSaving.value = true;
  try {
    await fetch(`${props.backendUrl}/tria/admin/state`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(localState.value)
    });
    alert("Estat actualitzat! Els canvis s'han enviat a tots els professors.");
  } catch (e) {
      alert("Error en guardar l'estat.");
  } finally {
      isSaving.value = false;
  }
};
</script>
