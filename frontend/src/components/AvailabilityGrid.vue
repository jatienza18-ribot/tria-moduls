<template>
  <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden flex flex-col h-full">
    <!-- Header -->
    <div class="p-4 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
      <div>
        <h3 class="font-bold text-slate-800 flex items-center gap-2">
          Disponibilitat (Les "X")
        </h3>
        <p class="text-xs text-slate-500 mt-0.5">Fes clic per marcar hores no disponibles</p>
      </div>
      
      <div class="bg-white px-3 py-1.5 rounded-lg border border-slate-200 text-sm font-medium">
        Límit: <span :class="xCount > maxLimit ? 'text-red-500' : 'text-slate-700'">{{ xCount }}</span> / {{ maxLimit }}
      </div>
    </div>

    <!-- Grid -->
    <div class="flex-1 overflow-auto p-4">
      <table class="w-full text-sm border-collapse">
        <thead>
          <tr>
            <th class="border border-slate-200 bg-slate-50 p-2 w-16 text-slate-500 font-medium">Hora</th>
            <th v-for="day in days" :key="day" class="border border-slate-200 bg-slate-50 p-2 text-slate-600 font-medium w-1/5">
              {{ day }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(slot, i) in timeSlots" :key="i">
            <td class="border border-slate-200 p-2 text-center text-xs text-slate-500 font-medium bg-slate-50">
              {{ slot.label }}
            </td>
            <td 
              v-for="(day, dIndex) in days" :key="dIndex"
              class="border border-slate-200 p-0 relative group cursor-pointer transition-colors"
              :class="{
                'bg-red-50': isSelected(`${dIndex + 1}_${slot.id}`)
              }"
              @click="toggleSlot(`${dIndex + 1}_${slot.id}`)"
            >
              <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-red-100/50" v-if="!isSelected(`${dIndex + 1}_${slot.id}`)">
                <span class="text-red-400">X</span>
              </div>
              <div class="h-10 w-full flex items-center justify-center pointer-events-none">
                <span v-if="isSelected(`${dIndex + 1}_${slot.id}`)" class="text-red-500 font-bold text-lg">X</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="p-4 border-t border-slate-100 bg-slate-50 flex justify-end">
      <button 
        @click="$emit('save', selectedSlots)"
        class="bg-slate-900 text-white px-4 py-2 rounded-lg font-medium hover:bg-slate-800 transition-colors flex items-center gap-2"
        :disabled="xCount > maxLimit"
        :class="{'opacity-50 cursor-not-allowed': xCount > maxLimit}"
      >
        Desar Disponibilitat
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  initialSlots: { type: Array, default: () => [] },
  isFullTime: { type: Boolean, default: true }
});

const emit = defineEmits(['save']);

const days = ['Dilluns', 'Dimarts', 'Dimecres', 'Dijous', 'Divendres'];
const timeSlots = [
  { id: '08:00', label: '08:00 - 09:00' },
  { id: '09:00', label: '09:00 - 10:00' },
  { id: '10:00', label: '10:00 - 11:00' },
  { id: '11:00', label: '11:00 - 11:30' },
  { id: '11:30', label: '11:30 - 12:30' },
  { id: '12:30', label: '12:30 - 13:30' },
  { id: '13:30', label: '13:30 - 14:30' },
  { id: '15:00', label: '15:00 - 16:00' },
  { id: '16:00', label: '16:00 - 17:00' },
  { id: '17:00', label: '17:00 - 18:00' },
  { id: '18:30', label: '18:30 - 19:30' },
  { id: '19:30', label: '19:30 - 20:30' },
  { id: '20:30', label: '20:30 - 21:30' }
];

const selectedSlots = ref([...props.initialSlots]);

watch(() => props.initialSlots, (newVal) => {
  selectedSlots.value = [...newVal];
});

const maxLimit = computed(() => props.isFullTime ? 4 : 2);
const xCount = computed(() => selectedSlots.value.length);

const isSelected = (slotId) => selectedSlots.value.includes(slotId);

const toggleSlot = (slotId) => {
  const idx = selectedSlots.value.indexOf(slotId);
  if (idx > -1) {
    selectedSlots.value.splice(idx, 1);
  } else {
    if (selectedSlots.value.length >= maxLimit.value) {
      alert(`Has assolit el límit màxim de ${maxLimit.value} hores no disponibles.`);
      return;
    }
    selectedSlots.value.push(slotId);
  }
};
</script>
