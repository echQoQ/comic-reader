<template>
  <div class="breadcrumb">
		<a-breadcrumb>
			<a-breadcrumb-item> <div class="p1"> <HomeOutlined /> Home</div></a-breadcrumb-item>
		</a-breadcrumb>
	</div>
  <div class="spinning" v-if="showLoading">
    <a-spin 
      size="large" 
      tip="Loading"
      :indicator="indicator"
      />
  </div>
  <div class="container">
    <h1>There's no GOD.</h1>
    <div class="search-container">
      <a-input-search
        v-model:value="searchForm.keyword"
        v-model:loading="loading"
        enter-button="搜索"
        placeholder="输入关键词"
        size="large"
        class="input-search"
        @search="onSearch"
        >
      <template #addonBefore>
        <a-select v-model:value="searchForm.adapter">
          <a-select-option v-for="(value, key, index) in comicSources" :value="key">线路 {{ index + 1 }}</a-select-option>
        </a-select>
      </template>
      </a-input-search>
    </div>
    <div class="search-results-container" v-if="show">
      <a-list item-layout="horizontal" :data-source="data">
        <template #renderItem="{ item }">
          <a-list-item>
            <a-list-item-meta
             @click="loadChapters(item)"
            >
              <template #title>
                {{ item.title }}
              </template>
              <template #avatar>
                <a-avatar shape="square" size="large" :src="item.cover_img" />
              </template>
            </a-list-item-meta>
          </a-list-item>
        </template>
      </a-list>
    </div>
  </div>

</template>

<script setup>
import { ref, reactive, inject, h, onMounted, onBeforeMount } from 'vue'
import { useRoute, useRouter } from "vue-router";

import { useComicStore } from '@renderer/common/store.js'

const comicStore = useComicStore()

import axios from "axios"
const notify = inject('notify')
const router = useRouter()
const route = useRoute()

import { HomeOutlined, LoadingOutlined } from '@ant-design/icons-vue';

const loading = ref(false)
const show = ref(false)
const data = ref([])

const indicator = h(LoadingOutlined, {
    style: {
      fontSize: '50px',
    },
    spin: true,
});

const showLoading = ref(false)

const searchForm = reactive({
    keyword: '',
    adapter: sessionStorage.getItem('adapter')?sessionStorage.getItem('adapter'):'',
})

const onSearch = async () => {
  try {
    loading.value = true
    let res = await axios.post("search", {
      keyword: searchForm.keyword,
      adapter: searchForm.adapter,
    });
    if (res.status == 200) {
      sessionStorage.setItem('adapter', searchForm.adapter)
      data.value = res.data
      show.value = true
    }
  } catch(err) {
      notify("Error: " + err.message, 'error');
  }
  loading.value = false
}

const loadChapters = async item => {
  showLoading.value = true;
  await comicStore.loadComic(item.title, item.cover_img,item.url)
  showLoading.value = false;
  router.push({name: 'chapters'});
}

let comicSources = ref({})

const loadSources = async () => {
  let res = await window.api.readSources()
  comicSources.value = JSON.parse(res.data)
}

onMounted(async () => {
  await loadSources()
  if (!sessionStorage.getItem('adapter')) {
    searchForm.adapter = Object.keys(comicSources.value)[0]
  } else {
    console.log(sessionStorage.getItem('adapter'))
  }
})

</script>

<style lang="scss" scoped>
.breadcrumb {
	position: absolute;
	top: 20px;
	left: 50px;
    a {
        color: black;
    }
    .p1 {
        font-weight: bold;
    }
}

.spinning {
	position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
	z-index: 99;
}

.container {
  color: black;
  justify-content: center;
  align-items: center;
  .input-search {
    background-color: transparent !important;
    opacity: 0.6 !important;
    width: 40vw !important;
  }
  .search-results-container {
    margin-top: 2px;
    overflow-x: auto;
    padding: 10px;
    max-height: 60vh;
    cursor: pointer;
  }
  .search-results-container::-webkit-scrollbar {
    display: none;
  }
}
</style>
