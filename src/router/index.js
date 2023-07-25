import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '@/components/HelloWorld'
import Login from '@/components/Login.vue';
import Signup from '@/components/SignUp.vue';
import FileManager from '@/components/FileManager.vue';

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'index',
      component: FileManager
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/signup',
      name: 'SignUp',
      component: Signup
    },
    {
      path: '/demo',
      name: 'HelloWorld',
      component: HelloWorld
    },
    {
      path: '/file',
      name: 'FileManager',
      component: FileManager
    },
  ]
})
