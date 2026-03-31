<template>
  <div class="h-screen w-full bg-slate-50 flex flex-col p-4 md:p-8 relative">
    
    <!-- Header Controls -->
    <div class="absolute top-4 left-4 right-4 flex justify-between gap-4 z-50">
        <div class="flex items-center gap-4 bg-white/50 backdrop-blur-sm p-1 rounded-2xl border border-slate-200 shadow-sm">
            <div v-if="(session.especialitats || []).length > 1" class="flex items-center gap-1">
                <button 
                  v-for="esp in (session.especialitats || [])" :key="esp"
                  @click="currentEspecialitat = esp; fetchData();"
                  class="px-4 py-1.5 rounded-xl font-bold text-xs transition-all flex items-center gap-2"
                  :class="currentEspecialitat === esp ? 'bg-brand-blue text-white shadow-md scale-105' : 'text-slate-500 hover:bg-slate-100'"
                >
                  <i class="ph-bold ph-graduation-cap"></i> {{ esp }}
                </button>
            </div>
            <div v-else class="bg-brand-blue text-white px-5 py-2 rounded-xl font-bold text-xs shadow-sm flex items-center gap-2">
                <i class="ph-bold ph-graduation-cap"></i> {{ currentEspecialitat }}
            </div>
        </div>

        <div class="bg-indigo-950 text-white p-2 px-4 rounded-2xl shadow-xl flex items-center gap-4 border border-indigo-800">
          <div class="flex flex-col">
            <span class="text-[9px] uppercase font-black text-indigo-400 tracking-tighter">Sessió Activa</span>
            <span class="text-sm font-bold">{{ session?.username }}</span>
          </div>
          <div class="h-6 w-px bg-indigo-800"></div>
          <button @click="logout" class="text-[10px] font-bold uppercase tracking-widest text-indigo-300 hover:text-white transition-colors">Sortir</button>
        </div>
    </div>

    <!-- Proxy Selection & Turn Control -->
    <div v-if="state.ordre" class="fixed bottom-4 right-4 bg-white p-4 rounded-xl shadow-2xl z-50 border-2 border-brand-blue/30 w-72">
      <h3 class="font-bold text-slate-800 mb-2 flex items-center gap-2">
        <i class="ph ph-user-switch text-brand-blue text-lg"></i>
        Gestió de Docents ({{ currentEspecialitat }})
      </h3>
      <div class="flex flex-col gap-2">
          <select v-model="proxyUserId" class="w-full border border-slate-300 rounded p-2 bg-slate-50 font-bold focus:ring-brand-blue outline-none" @change="fetchData">
            <option :value="null">-- Tria un docent --</option>
            <option v-for="user in state.ordre" :key="user" :value="user">
              {{ user }}
              {{ state.torn_actual === user ? '⭐ (Torn Actual)' : '' }}
            </option>
          </select>
          
          <div v-if="proxyUserId" class="flex gap-1 mt-1">
              <button 
                @click="setTurn(proxyUserId)"
                class="flex-1 bg-amber-100 text-amber-800 text-[10px] py-1.5 rounded font-extrabold hover:bg-amber-200 border border-amber-200 transition"
                title="Estableix aquest docent com el torn oficial"
              >
                ESTABLIR TORN
              </button>
          </div>
      </div>
      <p v-if="proxyUserId && state.torn_actual !== proxyUserId" class="text-xs text-amber-600 mt-2 font-medium">
        Avís: Estàs gestionant a algú que NO té el torn actiu.
      </p>
    </div>

    <div v-if="!proxyUserId" class="flex-1 flex flex-col items-center justify-center text-center p-8">
        <div class="mb-4">
          <div class="h-16 w-16 bg-blue-100 text-brand-blue rounded-2xl flex items-center justify-center text-3xl font-black shadow-inner mx-auto">
            {{ (currentEspecialitat || '?').toString().charAt(0) }}
          </div>
        </div>
        <h2 class="text-2xl font-black text-slate-800 leading-tight">Benvingut/da Cap de Departament</h2>
        <p class="text-slate-400 font-medium text-sm mt-3 max-w-sm mx-auto">
          Ets el responsable de la tria per l'especialitat <span class="text-brand-blue font-bold shadow-[0_4px_0_0_#cfe1ff]">{{ currentEspecialitat }}</span>. 
          Utilitza el panell d'accions per començar.
        </p>
    </div>

    <div v-else class="max-w-7xl mx-auto w-full flex-1 flex flex-col min-h-0 pt-16 md:pt-4">
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <div>
            <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-3">
                Tria de: {{ proxyUserId }}
            </h1>
            <p class="text-xs font-bold mt-1 inline-flex items-center px-2 py-1 rounded-full text-white shadow-sm" :class="socketConnected ? 'bg-emerald-500' : 'bg-red-500'">
                {{ socketConnected ? 'CONNECTAT' : 'DESCONNECTAT' }}
            </p>
        </div>
        <div class="flex flex-wrap gap-2">
            <button @click="exportPDF" class="bg-slate-900 text-white px-3 py-2 rounded-xl text-sm font-bold hover:bg-slate-800 shadow-sm transition-colors">
              Exportar Horari
            </button>
        </div>
      </div>

      <TriaDashboard 
        :selectedHours="myTotalLectives" 
        :currentTurnName="state.torn_actual || 'Cap'" 
        :isMyTurn="isMyTurn"
        class="mb-6 shrink-0"
      />

      <div class="bg-white rounded-xl shadow border border-slate-200 overflow-hidden flex flex-col flex-1 min-h-[500px]">
        <div class="flex border-b border-slate-200 bg-slate-50 overflow-x-auto no-scrollbar shrink-0">
          <button 
            v-for="group in availableGroups" :key="group"
            @click="activeGroup = group"
            class="px-6 py-4 font-medium text-sm whitespace-nowrap border-b-2 transition-colors outline-none cursor-pointer"
            :class="activeGroup === group ? 'border-brand-blue text-brand-blue bg-white' : 'border-transparent text-slate-500 hover:text-slate-700'"
          >
            {{ group }}
          </button>
        </div>

        <div class="overflow-y-auto flex-1 relative bg-slate-50">
           <table class="w-full text-sm border-collapse min-w-[800px] h-full" v-if="filteredSlots.length > 0">
             <thead class="sticky top-0 z-10">
               <tr>
                 <th class="border-b border-slate-200 bg-slate-100 p-3 w-20 text-slate-500 font-medium">Hora</th>
                 <th v-for="day in days" :key="day.id" class="border-b border-l border-slate-200 bg-slate-100 p-3 text-slate-600 font-medium w-1/5">
                   {{ day.label }}
                 </th>
               </tr>
             </thead>
             <tbody>
               <tr v-for="time in timeSlots" :key="time.id" class="group">
                 <td class="border-b border-slate-200 text-center text-xs text-slate-500 font-medium bg-white">
                   {{ time.label }}
                 </td>
                 <td v-for="day in days" :key="day.id" class="border-b border-l border-slate-200 p-2 relative bg-white">
                    <div class="absolute inset-0 flex flex-col gap-1 p-1 overflow-y-auto no-scrollbar">
                        <template v-for="slot in getSlotsForCell(day.id, time.id)" :key="slot.id">
                            <div 
                                @click="toggleAssign(slot)"
                                class="rounded-lg p-2 text-xs border transition-all cursor-pointer h-full flex flex-col justify-center overflow-hidden"
                                :class="getSlotStyles(slot)"
                            >
                                <div class="font-bold leading-tight break-words" :class="{'text-red-600': hasOverlap(slot) && !hasMyId(slot)}">
                                    {{ slot.modul_nom || slot.modul_id }}
                                </div>
                                <div class="truncate opacity-75 mt-0.5 flex flex-wrap gap-1">
                                    <span v-if="!(slot.docent_ids && slot.docent_ids.length > 0)">Lliure</span>
                                    <span v-for="d in slot.docent_ids || []" :key="d" class="bg-slate-200/50 px-1 rounded">{{ d }}</span>
                                </div>
                            </div>
                        </template>
                    </div>
                 </td>
               </tr>
             </tbody>
           </table>
        </div>
        
        <div class="p-4 border-t border-slate-200 bg-white flex justify-between items-center shrink-0 shadow-lg relative">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 font-bold border border-slate-200">
                    {{ roundSelectionCount }}
                </div>
                <div>
                    <p class="text-sm font-medium">Mòduls a la ronda per {{ proxyUserId }}</p>
                    <p class="text-xs text-slate-400">Recorda, cal tancar cada torn de 2 mòduls.</p>
                </div>
            </div>
            
            <button 
                @click="confirmTurn"
                :disabled="!isMyTurn || roundSelectionCount !== 2"
                class="px-8 py-3 rounded-xl font-bold transition-all shadow-sm"
                :class="isMyTurn && roundSelectionCount === 2 
                    ? 'bg-emerald-600 text-white hover:bg-emerald-700 cursor-pointer' 
                    : 'bg-slate-100 text-slate-400 border border-slate-200 cursor-not-allowed'"
            >
                Confirmar Torn de {{ proxyUserId }}
            </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import TriaDashboard from '../components/TriaDashboard.vue';

const router = useRouter();

const session = JSON.parse(localStorage.getItem('tria_session') || 'null');
if (!session || session.rol !== 'DEPARTAMENT') {
    router.replace('/login');
}

const proxyUserId = ref(null); // The teacher selected
const currentEspecialitat = ref(session?.especialitat || (session?.especialitats && session.especialitats[0]) || '');

const slots = ref([]);
const allGroupsMetadata = ref([]);
const state = ref({ torn_actual: null, ordre: [] });
const activeGroup = ref('');
const socketConnected = ref(false);
let ws = null;
const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001';
const wsUrl = backendUrl.replace('http', 'ws') + '/tria/ws';
const roundSelectionCount = ref(0);

const days = [{ id: 1, label: 'Dilluns' }, { id: 2, label: 'Dimarts' }, { id: 3, label: 'Dimecres' }, { id: 4, label: 'Dijous' }, { id: 5, label: 'Divendres' }];
const timeSlots = [
  { id: '08:00', label: '08:00' }, { id: '09:00', label: '09:00' }, { id: '10:00', label: '10:00' },
  { id: '11:00', label: '11:00' }, { id: '11:30', label: '11:30' }, { id: '12:30', label: '12:30' },
  { id: '13:30', label: '13:30' }, { id: '15:00', label: '15:00' }, { id: '16:00', label: '16:00' },
  { id: '17:00', label: '17:00' }, { id: '18:30', label: '18:30' }, { id: '19:30', label: '19:30' }, { id: '20:30', label: '20:30' }
];

const isMyTurn = computed(() => proxyUserId.value && state.value.torn_actual === proxyUserId.value);
const myTotalLectives = computed(() => slots.value.filter(hasMyId).length);

const availableGroups = computed(() => {
    // Handling both legacy (strings) and new (objects) formats
    const groupsImplicatedNames = allGroupsMetadata.value
        .filter(g => {
            if (typeof g === 'string') return true; // Legacy fallback
            return (g.especialitats || []).includes(currentEspecialitat.value);
        })
        .map(g => typeof g === 'string' ? g : g.name);
    
    return Array.from(new Set(groupsImplicatedNames)).filter(Boolean).sort();
});

const filteredSlots = computed(() => {
    let base = activeGroup.value ? slots.value.filter(s => (s.grup_nom || s.grup_id) === activeGroup.value) : [];
    // Also filter slots by especialitats_permises
    return base.filter(s => {
        if (!s.especialitats_permises || s.especialitats_permises.length === 0) return true;
        return s.especialitats_permises.includes(currentEspecialitat.value);
    });
});

const logout = () => { localStorage.removeItem('tria_session'); router.push('/login'); };

const sanitizeSlots = (dataArray) => dataArray.map(s => {
    if (!s.docent_ids) s.docent_ids = [];
    if (s.docent_id && !s.docent_ids.includes(s.docent_id)) s.docent_ids.push(s.docent_id);
    if (!s.max_docents) s.max_docents = 1;
    return s;
});

const fetchData = async () => {
    try {
        const resSlots = await fetch(`${backendUrl}/horaris/`);
        slots.value = sanitizeSlots(await resSlots.json());
        
        // Try v2 first, fallback to legacy
        let resG = await fetch(`${backendUrl}/grups_v2`);
        if (!resG.ok) resG = await fetch(`${backendUrl}/grups`);
        allGroupsMetadata.value = await resG.json();

        if (!availableGroups.value.includes(activeGroup.value)) {
            activeGroup.value = availableGroups.value.length > 0 ? availableGroups.value[0] : '';
        }

        const resState = await fetch(`${backendUrl}/tria/state/${currentEspecialitat.value}`);
        state.value = await resState.json();
    } catch (e) { console.error(e); }
};

const hasMyId = (slot) => proxyUserId.value && (slot.docent_ids || []).includes(proxyUserId.value);
const getSlotsForCell = (day, time) => filteredSlots.value.filter(s => s.dia_setmana === day && s.hora_inici === time);
const hasOverlap = (targetSlot) => slots.value.some(s => s.id !== targetSlot.id && hasMyId(s) && s.dia_setmana === targetSlot.dia_setmana && s.hora_inici === targetSlot.hora_inici);

const getSlotStyles = (slot) => {
    if (hasMyId(slot)) return 'bg-blue-100 border-brand-blue text-brand-blue shadow-[0_0_0_1px_rgba(40,111,255,0.2)]';
    const isFull = (slot.docent_ids || []).length >= (slot.max_docents || 1);
    if (isFull) return 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed';
    return 'bg-white border-dashed border-slate-300 text-slate-600 hover:border-brand-blue hover:shadow-md';
};

const toggleAssign = async (slot) => {
    if (!proxyUserId.value) return alert("Has de seleccionar quin docent està fent la tria ara mateix.");
    if (!isMyTurn.value) return alert(`Avís: No és el torn oficial de ${proxyUserId.value}`);

    if (hasMyId(slot)) {
        roundSelectionCount.value = Math.max(0, roundSelectionCount.value - 1);
        try {
            await fetch(`${backendUrl}/tria/release`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ docent_id: proxyUserId.value, modul_id: slot.modul_id, grup_id: slot.grup_id }) });
        } catch (e) { console.error(e); }
    } else {
        if (roundSelectionCount.value >= 2) return alert("Aquesta ronda ja ha triat 2 mòduls. Confirma el torn.");
        if (hasOverlap(slot)) return alert("Solapament d'horari detectat!");
        roundSelectionCount.value++;
        try {
            await fetch(`${backendUrl}/tria/take`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ docent_id: proxyUserId.value, modul_id: slot.modul_id, grup_id: slot.grup_id }) });
        } catch (e) { roundSelectionCount.value--; }
    }
};

const confirmTurn = async () => {
    if (!isMyTurn.value || roundSelectionCount.value < 2) return;
    try {
        const res = await fetch(`${backendUrl}/tria/next_turn/${currentEspecialitat.value}`, { method: 'POST' });
        if (res.ok) { roundSelectionCount.value = 0; alert("Torn passat!"); }
    } catch(e) { console.error(e); }
};

const setTurn = async (docentId) => {
    if (!confirm(`Vols posar a ${docentId} com al torn oficial actual?`)) return;
    try {
        await fetch(`${backendUrl}/tria/set_turn/${currentEspecialitat.value}`, { 
            method: 'POST', 
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ torn_actual: docentId })
        });
        alert("Torn canviat.");
    } catch(e) { console.error(e); }
};

const connectWebSocket = () => {
    ws = new WebSocket(wsUrl);
    ws.onopen = () => socketConnected.value = true;
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "MODULE_TAKEN") {
            slots.value.forEach(s => { if (data.slots.includes(s.id)) { if (!s.docent_ids) s.docent_ids = []; if (!s.docent_ids.includes(data.docent_id)) s.docent_ids.push(data.docent_id); } });
        } else if (data.type === "MODULE_RELEASED") {
            slots.value.forEach(s => { if (data.slots.includes(s.id) && s.docent_ids) s.docent_ids = s.docent_ids.filter(id => id !== data.docent_id); });
        } else if (data.type === "TURN_CHANGED" && data.especialitat === session.especialitat) {
            state.value.torn_actual = data.torn_actual;
        }
    };
    ws.onclose = () => { socketConnected.value = false; setTimeout(connectWebSocket, 3000); };
};

const exportPDF = () => {
    if(!proxyUserId.value) return;
    const mySlots = slots.value.filter(hasMyId);
    const win = window.open('', '', 'height=800,width=800');
    win.document.write(`<html><body><h2>Horari - ${proxyUserId.value}</h2><script>window.onload=function(){window.print()}<\/script></body></html>`);
    win.document.close();
};

onMounted(() => { fetchData(); connectWebSocket(); });
onUnmounted(() => { if (ws) ws.close(); });
</script>
