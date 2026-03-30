<template>
  <div class="h-screen w-full bg-slate-100 flex flex-col p-4 relative">
    
    <div class="absolute top-4 right-4 bg-slate-900 text-white p-2 rounded-lg shadow flex gap-4 items-center">
      <span class="text-xs uppercase font-bold text-slate-400">Cap d'Estudis Admin</span>
      <button @click="logout" class="bg-red-500 hover:bg-red-600 px-3 py-1 rounded text-sm font-bold shadow-sm">Sortir</button>
    </div>

    <div class="max-w-7xl mx-auto w-full pt-16">
      <h1 class="text-3xl font-extrabold text-slate-900 mb-8 border-b pb-4">Panell d'Administració Global</h1>

      <!-- Tab Navigation -->
      <div class="mb-6 flex justify-center bg-white p-2 rounded-xl shadow-sm border border-slate-200 gap-2">
        <button @click="viewMode = 'ESTAT'" :class="viewMode === 'ESTAT' ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'" class="px-6 py-2 rounded-lg font-bold flex-1 transition">Configuració Departaments</button>
        <button @click="viewMode = 'HORARIS'" :class="viewMode === 'HORARIS' ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'" class="px-6 py-2 rounded-lg font-bold flex-1 transition">Editor Mestre d'Horaris</button>
        <button @click="viewMode = 'GRUPS'" :class="viewMode === 'GRUPS' ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'" class="px-6 py-2 rounded-lg font-bold flex-1 transition">Gestió Grups</button>
        <button @click="viewMode = 'USUARIS'" :class="viewMode === 'USUARIS' ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'" class="px-6 py-2 rounded-lg font-bold flex-1 transition">Usuaris i Càrrecs</button>
      </div>

      <!-- Action Buttons Row -->
      <div class="mb-6 flex justify-end">
        <button v-if="viewMode === 'ESTAT'" @click="createSpecialty" class="bg-brand-blue text-white px-6 py-2 rounded-full font-bold shadow hover:bg-blue-600 transition">
            + Nova Especialitat
        </button>
        <button v-if="viewMode === 'HORARIS'" @click="openCreateModal" class="bg-emerald-600 text-white px-6 py-2 rounded-full font-bold shadow hover:bg-emerald-700 transition">
            + Nova Franja
        </button>
        <button v-if="viewMode === 'GRUPS'" @click="addGroup" class="bg-indigo-600 text-white px-6 py-2 rounded-full font-bold shadow hover:bg-indigo-700 transition">
            + Nou Grup
        </button>
        <button v-if="viewMode === 'USUARIS'" @click="openUserModal()" class="bg-purple-600 text-white px-6 py-2 rounded-full font-bold shadow hover:bg-purple-700 transition">
            + Nou Usuari
        </button>
      </div>

      <div v-if="viewMode === 'ESTAT'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Card per Especialitat -->
        <div v-for="(state, especialitat) in allStates" :key="especialitat" class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <div class="flex items-center gap-2 border-b pb-3 mb-4">
                <input
                    v-model="renameInputs[especialitat]"
                    class="text-xl font-bold text-brand-blue flex-1 border border-transparent rounded px-1 focus:border-brand-blue focus:bg-blue-50 outline-none transition"
                />
                <button
                    @click="renameSpecialty(especialitat)"
                    class="text-xs bg-slate-100 hover:bg-brand-blue hover:text-white text-slate-600 font-bold px-3 py-1 rounded border border-slate-200 transition"
                >Reanomenar</button>
            </div>
            
            <div class="mb-4">
                <span class="text-xs font-bold uppercase text-slate-400">Estat</span>
                <select v-model="state.fase" class="block w-full mt-1 border border-slate-300 rounded p-2">
                    <option value="PREPARACIO">En preparació</option>
                    <option value="OBERT">Tria Oberta</option>
                    <option value="FINALITZAT">Tancat</option>
                </select>
            </div>

            <div class="mb-4">
                <span class="text-xs font-bold uppercase text-slate-400">Torn Actual</span>
                <select v-model="state.torn_actual" class="block w-full mt-1 border border-brand-blue text-brand-blue bg-blue-50 font-bold rounded p-2">
                    <option :value="null">-- Sense Torn --</option>
                    <option v-for="user in state.ordre || []" :key="user" :value="user">{{ user }}</option>
                </select>
            </div>

            <div class="mb-4">
                <span class="text-xs font-bold uppercase text-slate-400 flex justify-between">
                    Ordre Assignat 
                    <button @click="addDocent(especialitat)" class="text-brand-blue hover:underline">Afegir Docent</button>
                </span>
                <div class="mt-2 flex flex-col gap-1 max-h-48 overflow-auto border border-slate-200 rounded p-2 bg-slate-50">
                    <div v-for="(user, idx) in state.ordre" :key="idx" class="flex items-center gap-2 bg-white rounded border border-slate-200 p-1">
                        <span class="font-bold text-slate-400 text-xs w-4">{{ idx + 1 }}.</span>
                        <input v-model="state.ordre[idx]" class="text-sm font-medium border-0 focus:ring-0 w-full" />
                        <button @click="state.ordre.splice(idx,1)" class="text-red-500 px-2 font-bold hover:bg-red-50 rounded">✕</button>
                    </div>
                </div>
            </div>

            <button @click="saveState(especialitat)" class="w-full bg-brand-blue text-white font-bold py-2 rounded-lg hover:bg-blue-600 shadow">
                Salvar Canvis d'Especialitat
            </button>
        </div>
      </div>
      
      <div v-if="viewMode === 'ESTAT' && Object.keys(allStates).length === 0" class="text-center py-10 bg-white rounded-xl border border-dashed border-slate-300">
          <p class="text-slate-500">No hi ha departaments configurats a la base de dades. Contacta un desenvolupador per fer el seed de `tria_state`.</p>
      </div>

      <!-- Editor d'Horaris Mestre -->
      <div v-if="viewMode === 'HORARIS'" class="bg-white rounded-xl shadow border border-slate-200 overflow-hidden flex flex-col flex-1 h-[70vh]">
        <div class="p-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
            <h2 class="font-bold text-slate-800">Cerca del Mòdul a Desplaçar:</h2>
            <select v-model="activeGroup" class="border border-slate-300 rounded p-2 text-sm bg-white">
                <option v-for="g in availableGroups" :key="g" :value="g">{{ g }}</option>
            </select>
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
                 <td class="border-b border-slate-200 p-3 text-center text-xs text-slate-500 font-medium bg-white">
                   {{ time.label }}
                 </td>
                 <td v-for="day in days" :key="day.id" class="border-b border-l border-slate-200 p-2 relative bg-white transition-colors hover:bg-slate-50 min-h-[5rem]">
                    <div class="flex flex-col gap-1 w-full h-full">
                        <template v-for="slot in getSlotsForCell(day.id, time.id)" :key="slot.id">
                            <div 
                                @click="openMoveModal(slot)"
                                class="rounded p-2 text-xs border transition-all cursor-pointer bg-white border-slate-300 hover:border-brand-blue hover:shadow-md"
                            >
                                <div class="font-bold text-slate-800 break-words whitespace-normal leading-tight">{{ slot.modul_nom || slot.modul_id }}</div>
                                <div class="mt-1" v-if="(slot.max_docents || 1) > 1">
                                    <span class="text-[10px] bg-amber-100 text-amber-800 px-1 rounded font-bold">DESDOBLAT</span>
                                </div>
                            </div>
                        </template>
                    </div>
                 </td>
               </tr>
             </tbody>
           </table>
        </div>
      </div>

      <!-- Editor d'Usuaris -->
      <div v-if="viewMode === 'USUARIS'" class="bg-white rounded-xl shadow border border-slate-200 p-6">
        <table class="w-full text-sm text-left">
            <thead>
                <tr class="border-b">
                    <th class="pb-3 text-slate-500 font-bold">Nom d'Usuari</th>
                    <th class="pb-3 text-slate-500 font-bold">Rol Tècnic</th>
                    <th class="pb-3 text-slate-500 font-bold">Especialitats Adjudicades</th>
                    <th class="pb-3 text-slate-500 font-bold text-center">Accions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="user in allUsers" :key="user.username" class="border-b last:border-0 hover:bg-slate-50 transition">
                    <td class="py-4 font-bold text-slate-800">{{ user.username }}</td>
                    <td class="py-4">
                        <span class="px-2 py-1 rounded text-xs font-bold" :class="user.rol === 'ADMIN' ? 'bg-red-100 text-red-800' : 'bg-slate-100 text-slate-700'">
                            {{ user.rol }}
                        </span>
                    </td>
                    <td class="py-4">
                        <div class="flex gap-1 flex-wrap">
                            <span v-for="esp in user.especialitats" :key="esp" class="bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded text-xs">{{ esp }}</span>
                            <span v-if="user.rol === 'ADMIN'" class="text-slate-400 italic text-xs">Accés Global</span>
                        </div>
                    </td>
                    <td class="py-4 flex gap-2 justify-center">
                        <button @click="openUserModal(user)" class="text-indigo-600 hover:text-indigo-800 font-bold text-xs uppercase px-2 py-1 border border-indigo-200 rounded hover:bg-indigo-50 transition">Editar</button>
                        <button v-if="user.username !== 'admin'" @click="deleteUser(user.username)" class="text-red-500 hover:text-red-700 font-bold text-xs uppercase px-2 py-1 border border-red-200 rounded hover:bg-red-50 transition">Eliminar</button>
                    </td>
                </tr>
            </tbody>
        </table>
      </div>

      <!-- Gestió de Grups -->
      <div v-if="viewMode === 'GRUPS'" class="bg-white rounded-xl shadow border border-slate-200 p-6">
          <div class="flex justify-between items-center mb-6">
              <h2 class="text-xl font-bold text-slate-800">Llistat Maestro de Grups</h2>
              <button @click="openGroupModal()" class="bg-indigo-600 text-white px-4 py-2 rounded-lg font-bold hover:bg-indigo-700 shadow-sm transition">+ Nou Grup</button>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div v-for="g in allGroups" :key="g.name" class="bg-slate-50 border border-slate-200 p-4 rounded-xl flex flex-col gap-2 shadow-sm relative group">
                  <div class="flex justify-between items-center">
                    <span class="font-extrabold text-slate-800">{{ g.name }}</span>
                    <div class="flex gap-1">
                        <button @click="openGroupModal(g)" class="text-slate-400 hover:text-indigo-600 p-1 transition">
                            <i class="ph ph-pencil-simple"></i>
                        </button>
                        <button @click="removeGroup(g.name)" class="text-slate-400 hover:text-red-600 p-1 transition">✕</button>
                    </div>
                  </div>
                  <div class="flex flex-wrap gap-1">
                      <span v-for="esp in g.especialitats" :key="esp" class="bg-indigo-100 text-indigo-700 text-[10px] px-1.5 py-0.5 rounded uppercase font-bold border border-indigo-200">{{ esp }}</span>
                      <span v-if="!g.especialitats || g.especialitats.length === 0" class="text-[10px] text-slate-400 italic">Cap especialitat assignada</span>
                  </div>
              </div>
          </div>
          <div v-if="allGroups.length === 0" class="text-center py-10 text-slate-400 italic">No hi ha grups configurats.</div>
      </div>

    </div>

    <!-- Edit/Create Modal -->
    <div v-if="showMoveModal" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden flex flex-col max-h-[90vh]">
        <div class="p-4 border-b bg-slate-50 flex justify-between items-center">
            <h2 class="font-bold text-lg">{{ isCreating ? 'Nova Franja' : 'Editar Mòdul' }}</h2>
            <button @click="showMoveModal = false" class="text-slate-400 hover:text-slate-600 font-bold text-xl">✕</button>
        </div>
        <div class="p-6 overflow-y-auto w-full">
            <div class="flex flex-col gap-4">
                <div v-if="isCreating">
                    <label class="block text-sm font-bold text-slate-700 mb-1">Grup de Destinació</label>
                    <select v-model="editSlot.grup_id" class="w-full border border-slate-300 p-2 rounded bg-slate-50 mb-2">
                        <option v-for="g in availableGroups" :key="g" :value="g">{{ g }}</option>
                        <option value="NOU_GRUP">+ Crear grup nou...</option>
                    </select>
                    
                    <div v-if="editSlot.grup_id === 'NOU_GRUP'">
                        <input v-model="newGroupName" type="text" placeholder="Escriu el nom (Ex: SMX 2B)" class="w-full border-2 border-brand-blue p-2 rounded outline-none text-brand-blue font-bold" />
                    </div>
                </div>

                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-1">Nom del Mòdul</label>
                    <input v-model="editSlot.modul_nom" type="text" placeholder="Ex: M01 - Sistemes Operatius" class="w-full border border-slate-300 p-2 rounded" />
                </div>

                <div class="flex gap-4">
                    <div class="flex-1">
                        <label class="block text-sm font-bold text-slate-700 mb-1">Dia</label>
                        <select v-model="editSlot.dia_setmana" class="w-full border border-slate-300 p-2 rounded">
                            <option v-for="d in days" :key="d.id" :value="d.id">{{ d.label }}</option>
                        </select>
                    </div>
                    <div class="flex-1">
                        <label class="block text-sm font-bold text-slate-700 mb-1">Hora d'Inici</label>
                        <select v-model="editSlot.hora_inici" class="w-full border border-slate-300 p-2 rounded">
                            <option v-for="t in timeSlots" :key="t.id" :value="t.id">{{ t.label }}</option>
                        </select>
                    </div>
                </div>

                <label class="mt-2 flex items-center gap-3 bg-amber-50 p-3 rounded-lg border border-amber-200 cursor-pointer hover:bg-amber-100 transition">
                    <input v-model="editModeDesdoblament" type="checkbox" class="w-5 h-5 accent-brand-blue" />
                    <div class="flex flex-col">
                        <span class="font-bold text-amber-900 text-sm">És un desdoblament?</span>
                        <span class="text-xs text-amber-700">Permet a dues persones diferents adjudicar-se aquest mateix bloc al seu horari.</span>
                    </div>
                </label>

                <div class="mt-2 text-slate-500 font-bold text-xs uppercase px-1 border-b pb-1">Restringir a Especialitats:</div>
                <div class="grid grid-cols-2 gap-2 bg-slate-50 p-3 rounded-lg border border-slate-200">
                    <label v-for="esp in Object.keys(allStates)" :key="esp" class="flex items-center gap-2 cursor-pointer hover:bg-slate-100 p-1 rounded transition">
                        <input type="checkbox" :value="esp" v-model="editSlot.especialitats_permises" class="w-4 h-4 accent-indigo-600" />
                        <span class="text-xs font-bold text-slate-600">{{ esp }}</span>
                    </label>
                    <div v-if="Object.keys(allStates).length === 0" class="text-[10px] text-slate-400 italic col-span-2">No hi ha especialitats creades.</div>
                </div>
                <p class="text-[10px] text-slate-400 italic">Si no en selecciones cap, qualsevol especialitat el podrà triar.</p>
            </div>

            <div class="flex flex-col gap-2 mt-8">
                <button @click="submitEdit" class="w-full bg-brand-blue text-white py-3 rounded-lg font-bold hover:bg-blue-600 shadow-md">
                    {{ isCreating ? 'Crear Mòdul Corresponent' : 'Desar Canvis' }}
                </button>
                <button v-if="!isCreating" @click="deleteSlot" class="w-full bg-white text-red-600 border border-red-200 py-3 rounded-lg font-bold hover:bg-red-50 hover:border-red-300 transition-colors">
                    Eliminar Mòdul Definitivament
                </button>
            </div>
        </div>
      </div>
    </div>

    <!-- User Modal -->
    <div v-if="showUserModal" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm overflow-hidden flex flex-col max-h-[90vh]">
        <div class="p-4 border-b bg-slate-50 flex justify-between items-center">
            <h2 class="font-bold text-lg">{{ isEditingUser ? 'Editar Usuari' : 'Nou Usuari' }}</h2>
            <button @click="showUserModal = false" class="text-slate-400 hover:text-slate-600 font-bold text-xl">✕</button>
        </div>
        <div class="p-6 overflow-y-auto">
            <div class="flex flex-col gap-4">
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-1">Nom d'Usuari</label>
                    <input v-model="editUser.username" :disabled="isEditingUser" type="text" placeholder="ex: matematiques_cap" class="w-full border border-slate-300 p-2 rounded outline-none focus:border-brand-blue" />
                </div>
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-1">Contrasenya</label>
                    <input v-model="editUser.password" type="text" placeholder="ex: 12345" class="w-full border border-slate-300 p-2 rounded outline-none focus:border-brand-blue" />
                </div>
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-1">Tipus de Permisos</label>
                    <select v-model="editUser.rol" class="w-full border border-slate-300 p-2 rounded outline-none bg-slate-50">
                        <option value="DEPARTAMENT">Cap de Departament</option>
                        <option value="ADMIN">Cap d'Estudis (Admin)</option>
                    </select>
                </div>
                <div v-if="editUser.rol === 'DEPARTAMENT'">
                    <label class="block text-sm font-bold text-slate-700 mb-2">Especialitat/s que pot gestionar</label>
                    <div class="max-h-48 overflow-y-auto border border-slate-200 rounded p-2 flex flex-col gap-2 bg-slate-50">
                        <label v-for="(state, espc) in allStates" :key="espc" class="flex items-center gap-2 text-sm cursor-pointer hover:bg-slate-200 p-1 rounded">
                            <input type="checkbox" :value="espc" v-model="editUser.especialitats" class="accent-brand-blue" />
                            {{ espc }}
                        </label>
                        <div v-if="Object.keys(allStates).length === 0" class="text-xs text-slate-500 italic">Crea primer una especialitat.</div>
                    </div>
                </div>
            </div>
            <button @click="saveUser" class="w-full mt-6 bg-brand-blue text-white py-3 rounded-lg font-bold hover:bg-blue-600 shadow-md">
                {{ isEditingUser ? 'Desar Canvis' : 'Crear Credencial' }}
            </button>
        </div>
      </div>
    </div>

    <!-- Group Modal -->
    <div v-if="showGroupModal" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm overflow-hidden flex flex-col">
        <div class="p-4 border-b bg-slate-50 flex justify-between items-center">
            <h2 class="font-bold text-lg">{{ isEditingGroup ? 'Editar Grup' : 'Nou Grup' }}</h2>
            <button @click="showGroupModal = false" class="text-slate-400 hover:text-slate-600 font-bold text-xl">✕</button>
        </div>
        <div class="p-6 overflow-y-auto">
            <div class="flex flex-col gap-4">
                <div>
                  <label class="block text-sm font-bold text-slate-700 mb-1">Nom del Grup</label>
                  <input v-model="editGroup.name" :disabled="isEditingGroup" type="text" placeholder="Ex: 1r SMX A" class="w-full border border-slate-300 rounded-lg p-3 outline-none focus:border-brand-blue" />
                </div>
                <div>
                  <label class="block text-sm font-bold text-slate-700 mb-1">Especialitats Implicades</label>
                  <div class="grid grid-cols-2 gap-2 bg-slate-50 p-3 rounded-xl border border-slate-200">
                    <label v-for="esp in Object.keys(allStates)" :key="esp" class="flex items-center gap-2 cursor-pointer hover:bg-slate-100 p-1 rounded transition">
                        <input type="checkbox" :value="esp" v-model="editGroup.especialitats" class="w-4 h-4 accent-indigo-600" />
                        <span class="text-xs font-bold text-slate-600">{{ esp }}</span>
                    </label>
                  </div>
                </div>
            </div>
            <button @click="saveGroup" class="w-full bg-indigo-600 text-white py-3 rounded-lg font-bold mt-6 hover:bg-indigo-700 shadow-md transition">
              Desar Grup
            </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const session = JSON.parse(localStorage.getItem('tria_session') || 'null');
if (!session || session.rol !== 'ADMIN') { router.replace('/login'); }

const allStates = ref({});
const allSlots = ref([]);
const allUsers = ref([]);
const allGroups = ref([]);
const renameInputs = ref({});

const activeGroup = ref('');
const viewMode = ref('ESTAT'); // ESTAT, HORARIS, GRUPS, USUARIS

const showMoveModal = ref(false);
const isCreating = ref(false);
const selectedSlotToMove = ref(null);
const editModeDesdoblament = ref(false);
const editSlot = ref({ grup_id: '', dia_setmana: 1, hora_inici: '08:00', modul_nom: '' });
const newGroupName = ref('');

const showUserModal = ref(false);
const isEditingUser = ref(false);
const originalUsername = ref('');
const editUser = ref({ username: '', password: '', rol: 'DEPARTAMENT', especialitats: [] });

const showGroupModal = ref(false);
const isEditingGroup = ref(false);
const editGroup = ref({ name: '', especialitats: [] });

const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001';

const days = [{ id: 1, label: 'Dilluns' }, { id: 2, label: 'Dimarts' }, { id: 3, label: 'Dimecres' }, { id: 4, label: 'Dijous' }, { id: 5, label: 'Divendres' }];
const timeSlots = [
  { id: '08:00', label: '08:00' }, { id: '09:00', label: '09:00' }, { id: '10:00', label: '10:00' },
  { id: '11:00', label: '11:00' }, { id: '11:30', label: '11:30' }, { id: '12:30', label: '12:30' },
  { id: '13:30', label: '13:30' }, { id: '15:00', label: '15:00' }, { id: '16:00', label: '16:00' },
  { id: '17:00', label: '17:00' }, { id: '18:30', label: '18:30' }, { id: '19:30', label: '19:30' }, { id: '20:30', label: '20:30' }
];

const availableGroups = computed(() => {
    const fromSlots = Array.from(new Set(allSlots.value.map(s => s.grup_nom || s.grup_id))).filter(Boolean);
    const fromMaster = allGroups.value.map(g => g.name);
    return Array.from(new Set([...fromSlots, ...fromMaster])).sort();
});
const filteredSlots = computed(() => activeGroup.value ? allSlots.value.filter(s => (s.grup_nom || s.grup_id) === activeGroup.value) : allSlots.value);

const fetchData = async () => {
    try {
        const res = await fetch(`${backendUrl}/tria/state`);
        const states = await res.json();
        allStates.value = states;
        // Sync rename inputs with loaded specialties
        Object.keys(states).forEach(k => {
            if (!(k in renameInputs.value)) renameInputs.value[k] = k;
        });

        const resSlots = await fetch(`${backendUrl}/horaris/`);
        allSlots.value = await resSlots.json();
        
        fetchUsers();
        fetchGroups();
        if(!activeGroup.value && availableGroups.value.length > 0) activeGroup.value = availableGroups.value[0];
    } catch(e) { console.error(e); }
};

const fetchGroups = async () => {
    try {
        const res = await fetch(`${backendUrl}/grups`);
        allGroups.value = await res.json();
    } catch(e) { console.error(e); }
};

const fetchUsers = async () => {
    try {
        const res = await fetch(`${backendUrl}/usuaris/`);
        allUsers.value = await res.json();
    } catch(e) { console.error(e); }
};

const createSpecialty = async () => {
    const nou = prompt("Introdueix el codi de la nova especialitat (Ex: Matemàtiques):");
    if(!nou) return;
    try {
        await fetch(`${backendUrl}/tria/admin/state/${encodeURIComponent(nou)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fase: 'PREPARACIO', torn_actual: null, ordre: [] })
        });
        renameInputs.value[nou] = nou;
        fetchData();
        alert(`Nova especialitat ${nou} donada d'alta.`);
    } catch(e) { console.error(e); }
};

const renameSpecialty = async (oldName) => {
    const newName = (renameInputs.value[oldName] || '').trim();
    if (!newName || newName === oldName) return;
    if (!confirm(`Reanomenaràs "${oldName}" a "${newName}". Continuar?`)) {
        renameInputs.value[oldName] = oldName; // Reset input
        return;
    }
    try {
        const res = await fetch(`${backendUrl}/tria/admin/rename/${encodeURIComponent(oldName)}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_name: newName })
        });
        if (!res.ok) {
            const err = await res.json();
            return alert('Error: ' + err.detail);
        }
        fetchData();
    } catch(e) { console.error(e); alert('Error de connexió'); }
};


const addDocent = (espc) => {
    const nou = prompt("Introdueix l'ID del docent (ex: profe_nou):");
    if(nou) {
        if(!allStates.value[espc].ordre) allStates.value[espc].ordre = [];
        allStates.value[espc].ordre.push(nou);
    }
};

const saveState = async (espc) => {
    try {
        await fetch(`${backendUrl}/tria/admin/state/${espc}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(allStates.value[espc])
        });
        alert(`Configuració de ${espc} arxivada amb èxit i emesa a tothom.`);
    } catch(e) { alert("Error"); }
};

const getSlotsForCell = (day, time) => filteredSlots.value.filter(s => s.dia_setmana === day && s.hora_inici === time);

const openCreateModal = () => {
    isCreating.value = true;
    selectedSlotToMove.value = null;
    editModeDesdoblament.value = false;
    newGroupName.value = '';
    editSlot.value = { 
        grup_id: activeGroup.value || (availableGroups.value.length > 0 ? availableGroups.value[0] : ''), 
        dia_setmana: 1, 
        hora_inici: '08:00', 
        modul_nom: '',
        especialitats_permises: []
    };
    showMoveModal.value = true;
};

const openMoveModal = (slot) => {
    isCreating.value = false;
    selectedSlotToMove.value = slot;
    editModeDesdoblament.value = (slot.max_docents || 1) > 1;
    editSlot.value = {
        grup_id: slot.grup_id,
        dia_setmana: slot.dia_setmana,
        hora_inici: slot.hora_inici,
        modul_nom: slot.modul_nom || slot.modul_id || '',
        especialitats_permises: slot.especialitats_permises || []
    };
    showMoveModal.value = true;
};

const submitEdit = async () => {
    if(!editSlot.value.modul_nom.trim()) return alert("El nom és obligatori");
    
    let finalGroupId = editSlot.value.grup_id;
    if (isCreating.value && finalGroupId === 'NOU_GRUP') {
        if (!newGroupName.value.trim()) return alert("Escriu el nom exacte del nou grup");
        finalGroupId = newGroupName.value.trim();
    }

    // Find end time for 1 hour duration. For real logic we'd compute properly, but simple fallback:
    const nextH = parseInt(editSlot.value.hora_inici.split(':')[0]) + 1;
    const hFi = nextH.toString().padStart(2, '0') + ':' + editSlot.value.hora_inici.split(':')[1];

    try {
        if (isCreating.value) {
             await fetch(`${backendUrl}/horaris/`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    grup_id: finalGroupId,
                    dia_setmana: editSlot.value.dia_setmana,
                    hora_inici: editSlot.value.hora_inici,
                    hora_fi: hFi,
                    modul_nom: editSlot.value.modul_nom,
                    max_docents: editModeDesdoblament.value ? 2 : 1,
                    especialitats_permises: editSlot.value.especialitats_permises || []
                })
            });
            // Force active view onto the new group so they clearly see the newly created square!
            activeGroup.value = finalGroupId; 
        } else {
            await fetch(`${backendUrl}/horaris/${selectedSlotToMove.value.id}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    dia_setmana: editSlot.value.dia_setmana,
                    hora_inici: editSlot.value.hora_inici,
                    hora_fi: hFi,
                    modul_nom: editSlot.value.modul_nom,
                    max_docents: editModeDesdoblament.value ? 2 : 1,
                    especialitats_permises: editSlot.value.especialitats_permises
                })
            });
        }
        showMoveModal.value = false;
        fetchData();
        alert(isCreating.value ? "Nova franja creada al calendari." : "Canvis en la franja desats.");
    } catch(e) { console.error(e); }
};

const deleteSlot = async () => {
    if(!selectedSlotToMove.value || !confirm("Estàs segur d'eliminar definitivament aquesta franja horària pública?")) return;
    try {
        await fetch(`${backendUrl}/horaris/${selectedSlotToMove.value.id}`, { method: 'DELETE' });
        showMoveModal.value = false;
        fetchData();
    } catch(e) { console.error(e); }
};

const openUserModal = (user = null) => {
    if (user) {
        isEditingUser.value = true;
        originalUsername.value = user.username;
        editUser.value = { ...user };
    } else {
        isEditingUser.value = false;
        originalUsername.value = '';
        editUser.value = { username: '', password: '', rol: 'DEPARTAMENT', especialitats: [] };
    }
    showUserModal.value = true;
};

const saveUser = async () => {
    if(!editUser.value.username.trim() || !editUser.value.password.trim()) return alert("Nom d'usuari i contrasenya són obligatoris.");
    try {
        // If username changed, handle rename first or delete old/create new
        if (isEditingUser.value && editUser.value.username !== originalUsername.value) {
            const renameRes = await fetch(`${backendUrl}/usuaris/rename/${originalUsername.value}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ new_username: editUser.value.username })
            });
            if (!renameRes.ok) {
                const err = await renameRes.json();
                return alert("Error al reanomenar: " + err.detail);
            }
        }

        // Save (update) user data
        await fetch(`${backendUrl}/usuaris/${editUser.value.username}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                password: editUser.value.password,
                rol: editUser.value.rol,
                especialitats: editUser.value.rol === 'ADMIN' ? [] : editUser.value.especialitats
            })
        });
        showUserModal.value = false;
        fetchUsers();
    } catch(e) { console.error(e); }
};

const openGroupModal = (group = null) => {
    if (group) {
        isEditingGroup.value = true;
        editGroup.value = { ...group };
    } else {
        isEditingGroup.value = false;
        editGroup.value = { name: '', especialitats: [] };
    }
    showGroupModal.value = true;
};

const saveGroup = async () => {
    if(!editGroup.value.name.trim()) return alert("El nom del grup és obligatori.");
    try {
        await fetch(`${backendUrl}/grups/${encodeURIComponent(editGroup.value.name)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ especialitats: editGroup.value.especialitats })
        });
        showGroupModal.value = false;
        fetchGroups();
    } catch(e) { console.error(e); }
};

const removeGroup = async (name) => {
    if (!confirm(`Estàs segur d'esborrar el grup ${name}?`)) return;
    try {
        await fetch(`${backendUrl}/grups/${encodeURIComponent(name)}`, { method: 'DELETE' });
        fetchGroups();
    } catch(e) { console.error(e); }
};

const deleteUser = async (username) => {
    if(!confirm(`Estàs completament segur d'esborrar el compte ${username}?`)) return;
    try {
        await fetch(`${backendUrl}/usuaris/${username}`, { method: 'DELETE' });
        fetchUsers();
    } catch(e) { console.error(e); }
};

const logout = () => { localStorage.removeItem('tria_session'); window.location.href = '/#/login'; };

onMounted(fetchData);
</script>
