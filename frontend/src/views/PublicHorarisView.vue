<template>
  <div class="min-h-screen bg-slate-50 text-slate-800">
    <div class="bg-indigo-900 text-white px-6 py-4 flex justify-between items-center shadow-lg">
        <h1 class="text-2xl font-extrabold flex items-center gap-2">
            <i class="ph ph-calendar text-brand-blue"></i> Quadre Públic de Resultats
        </h1>
        <router-link to="/login" class="text-indigo-200 text-sm font-bold hover:text-white transition-colors">Accés Responsables</router-link>
    </div>

    <div class="max-w-7xl mx-auto p-6">
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8 text-center flex flex-col items-center">
            <h2 class="text-xl font-bold mb-4">Busca el teu horari personalizat:</h2>
            <div class="flex max-w-md w-full gap-2">
                <input v-model="searchQuery" type="text" placeholder="Introdueix el teu cognom o ID..." class="flex-1 border border-slate-300 rounded-lg px-4 py-3 outline-none focus:ring-2 focus:ring-brand-blue/50" />
                <button @click="search" class="bg-brand-blue text-white px-6 rounded-lg font-bold hover:bg-blue-600 transition shadow">Buscar</button>
            </div>
            
            <div v-if="searchResult && mySlots.length > 0" class="mt-8 w-full">
                <h3 class="text-xl font-extrabold text-slate-800 border-b pb-2 mb-4 text-left text-brand-blue">Horari Confirmat de {{ searchResult }}</h3>
                <div class="bg-slate-50 border border-slate-200 rounded-xl overflow-hidden">
                    <table class="w-full text-left text-sm border-collapse">
                        <thead class="bg-slate-100 uppercase text-xs text-slate-500 border-b border-slate-200">
                            <tr>
                                <th class="p-3">Dia</th>
                                <th class="p-3">Hora inici</th>
                                <th class="p-3">Mòdul</th>
                                <th class="p-3">Grup</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="s in mySlots" :key="s.id" class="border-b border-slate-100 last:border-0 hover:bg-white transition-colors">
                                <td class="p-3 font-medium">{{ ['Dilluns','Dimarts','Dimecres','Dijous','Divendres'][s.dia_setmana-1] || s.dia_setmana }}</td>
                                <td class="p-3 text-slate-500">{{ s.hora_inici }}</td>
                                <td class="p-3 font-bold text-slate-800">{{ s.modul_nom || s.modul_id }}</td>
                                <td class="p-3">{{ s.grup_nom || s.grup_id }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div v-else-if="searchResult" class="mt-8 text-center bg-amber-50 rounded-xl border border-amber-200 p-6 w-full text-amber-800">
                Aquest docent no té cap mòdul assignat en aquest moment.
            </div>
        </div>

    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
const searchQuery = ref('');
const searchResult = ref('');
const allSlots = ref([]);
const mySlots = ref([]);
const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001';

const fetchData = async () => {
    try {
        const res = await fetch(`${backendUrl}/horaris/`);
        allSlots.value = await res.json();
    } catch(e) { console.error(e); }
};

const search = () => {
    if(!searchQuery.value.trim()) return;
    searchResult.value = searchQuery.value.trim();
    mySlots.value = allSlots.value.filter(s => (s.docent_ids || []).includes(searchResult.value) || s.docent_id === searchResult.value);
    mySlots.value.sort((a,b) => (a.dia_setmana !== b.dia_setmana ? a.dia_setmana - b.dia_setmana : a.hora_inici.localeCompare(b.hora_inici)));
};

onMounted(fetchData);
</script>
