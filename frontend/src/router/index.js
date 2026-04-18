import { createRouter, createWebHistory } from 'vue-router'

import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import SixTracks from '../views/SixTracks.vue'
import ContestDetail from '../views/ContestDetail.vue'
import ProblemsList from '../views/ProblemsList.vue'
import UserCenter from '../views/UserCenter.vue'
import TrainingPlan from '../views/TrainingPlan.vue'
import BlogList from '../views/BlogList.vue'
import BlogDetail from '../views/BlogDetail.vue'
import BlogEditor from '../views/BlogEditor.vue'

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
    component: UserCenter,
    meta: { requiresAuth: true }
  },
  {
    path: '/training-plan',
    component: TrainingPlan,
    meta: { requiresAuth: true }
  },
  {
    path: '/blog',
    component: BlogList
  },
  {
    path: '/blog/create',
    component: BlogEditor,
    meta: { requiresAuth: true }
  },
  {
    path: '/blog/:id',
    component: BlogDetail,
    props: true
  },
  {
    path: '/blog/:id/edit',
    component: BlogEditor,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：未登录用户访问需认证页面时跳转登录
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !localStorage.getItem('trainx_token')) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
