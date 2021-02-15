import Vue from 'vue'
import ViewUI from 'view-design';
import 'view-design/dist/styles/iview.css';

import cytoscape from "cytoscape";
Vue.use(cytoscape)

import VueCytoscape from 'vue-cytoscape'
Vue.use(VueCytoscape)

Vue.use(ViewUI);
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
Vue.use(ElementUI);
import App from './App.vue'
import './styles/index.less'

Vue.config.productionTip = false

import VueiClient from '@supermap/vue-iclient-mapboxgl';
Vue.use(VueiClient)


new Vue({
  render: h => h(App),
}).$mount('#app')
