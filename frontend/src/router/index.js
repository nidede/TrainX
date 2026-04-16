import { createRouter, createWebHistory } from 'vue-router'

import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import SixTracks from '../views/SixTracks.vue'
import ContestDetail from '../views/ContestDetail.vue'
import ProblemsList from '../views/ProblemsList.vue'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/login',
    component: Login
  },
  {
    path: '/register',
    component: Register
  },
  {
    path: '/home',
    component: Home
  },
  {
    path: '/six-tracks',
    component: SixTracks
  },
  {
    path: '/problems',
    component: ProblemsList
  },
  {
    path: '/contests/:id',
    component: ContestDetail,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router