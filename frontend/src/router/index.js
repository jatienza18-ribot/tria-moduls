import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
    {
        path: '/',
        name: 'public',
        component: () => import('../views/PublicHorarisView.vue')
    },
    {
        path: '/login',
        name: 'login',
        component: () => import('../views/LoginView.vue')
    },
    {
        path: '/dept',
        name: 'department',
        component: () => import('../views/TriaModulsView.vue')
    },
    {
        path: '/admin',
        name: 'admin',
        component: () => import('../views/AdminGlobalView.vue')
    }
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

export default router
