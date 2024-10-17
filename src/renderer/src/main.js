import './assets/main.css'
import 'ant-design-vue/dist/reset.css'

import Antd from 'ant-design-vue'
import { notification } from 'ant-design-vue';
import { router } from "@renderer/common/router"
import axios from "axios"
import { createPinia } from "pinia";
import VueLazyLoad from 'vue-lazyload'
import Codemirror from 'vue-codemirror';
import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App);
const pinia = createPinia();

app.use(pinia)
app.use(Antd)
app.use(router)
app.use(Codemirror)

import loadimage from '@renderer/assets/images/loading.gif'
import errorimage from '@renderer/assets/images/fail.jpg'

app.use(VueLazyLoad, {
  preLoad: 1.3,
  error: errorimage,
  loading: loadimage,
  attempt: 1,
})

axios.defaults.baseURL = import.meta.env.VITE_SERVER_URL

axios.interceptors.request.use((config) => {
  config.headers['Content-Type'] = 'application/json'
  return config
})

const notify = (msg) => {
  notification.open({
      message: msg,
      duration: 1,
  });
};

app.provide('notify', notify)

app.mount('#app');
