import { createRouter, createWebHistory } from 'vue-router'

import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import SixTracks from '../views/SixTracks.vue'
import ContestDetail from '../views/ContestDetail.vue'
import ProblemsList from '../views/ProblemsList.vue'
import UserCenter from '../views/UserCenter.vue'
import TrainingPlan from '../views/TrainingPlan.vue'

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
  },
  {
    path: '/user-center',
    component: UserCenter
  },
  {
    path: '/training-plan',
    component: TrainingPlan
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router