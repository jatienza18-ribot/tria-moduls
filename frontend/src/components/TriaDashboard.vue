<template>
  <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h2 class="text-xl font-bold text-slate-800">El teu tauler de tria</h2>
        <p class="text-sm text-slate-500 mt-1">
          Torn actual:
          <span 
            class="font-semibold px-2 py-0.5 rounded"
            :class="isMyTurn ? 'bg-brand-blue/10 text-brand-blue' : 'bg-slate-100 text-slate-700'"
          >
            {{ currentTurnName || 'Esperant...' }}
          </span>
        </p>
      </div>

      <div class="flex flex-col gap-3 w-full md:w-1/2">
        <!-- Lectives -->
        <div>
          <div class="flex justify-between text-sm mb-1">
            <span class="font-medium text-slate-700">Hores Lectives (Objectiu: 18h)</span>
            <span class="font-bold text-brand-blue">{{ selectedHours }}h / 18h</span>
          </div>
          <div class="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
            <div 
              class="h-full transition-all duration-500"
              :class="lectivesColor"
              :style="{ width: Math.min(100, (selectedHours / 18) * 100) + '%' }"
            ></div>
          </div>
        </div>

        <!-- Permanència -->
        <div>
          <div class="flex justify-between text-sm mb-1">
            <span class="font-medium text-slate-700">Permanència (Objectiu: 24h)</span>
            <span class="font-bold text-emerald-600">{{ selectedHours + 6 }}h / 24h</span>
          </div>
          <div class="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
            <div 
              class="h-full transition-all duration-500"
              :class="(selectedHours + 6) >= 24 ? 'bg-emerald-500' : 'bg-emerald-400'"
              :style="{ width: Math.min(100, ((selectedHours + 6) / 24) * 100) + '%' }"
            ></div>
          </div>
          <p class="text-xs text-slate-400 mt-1">* Inclou 6 hores automàtiques de reunions i guàrdies</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  selectedHours: { type: Number, default: 0 },
  currentTurnName: { type: String, default: '' },
  isMyTurn: { type: Boolean, default: false }
});

const lectivesColor = computed(() => {
  if (props.selectedHours >= 18) return 'bg-brand-blue';
  if (props.selectedHours >= 12) return 'bg-blue-400';
  return 'bg-blue-300';
});
</script>
