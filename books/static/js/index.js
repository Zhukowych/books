window.$ = window.jQuery = require('jquery');
require('bootstrap-sass');

import Vue from 'vue';
import Bookpages from  "./components/BooksPagesManager.vue"
window.Vue = Vue;

const app = new Vue({
    el: '.pages_block',
    components:{
        'book-pages' :Bookpages
    }
});