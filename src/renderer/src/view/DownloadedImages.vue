<template>
	<div class="breadcrumb">
		<a-breadcrumb>
			<a-breadcrumb-item> <a @click="router.push({name: 'index'})"> <HomeOutlined /> Home</a></a-breadcrumb-item>
			<a-breadcrumb-item> <a @click="router.push({name: 'downloaded_comics'})"> <DownloadOutlined /> 我的下载 </a> </a-breadcrumb-item>
			<a-breadcrumb-item><a @click="router.push({name: 'downloaded_chapters'})">{{ name }}</a></a-breadcrumb-item>
			<a-breadcrumb-item><div class="p1">{{ chapterName }}</div></a-breadcrumb-item>
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
		<div class="images-container" ref="box">
			<img
				v-for="(item, index) in imageList"
				class="single-image"
			    v-lazy="item"
				:key="item"
				/>
		</div>
		<a-pagination @change="onChangeChapter" :pageSize="1" v-model:current="current" :total="total" size="large" show-quick-jumper />
	</div>

</template>

<script setup>
import { ref, reactive, inject, onMounted, computed, h } from 'vue'
import { useRoute, useRouter } from "vue-router";
import { storeToRefs } from 'pinia'

import { useComicStore } from '@renderer/common/store.js'

const comicStore = useComicStore()
import axios from "axios"
const notify = inject('notify')
const router = useRouter()
const route = useRoute()

import { HomeOutlined, LoadingOutlined, DownloadOutlined } from '@ant-design/icons-vue';

const indicator = h(LoadingOutlined, {
    style: {
      fontSize: '50px',
    },
    spin: true,
});
let box = ref(null)

const showLoading = ref(false)

let chapterName = storeToRefs(comicStore).currentChapterTitle
let name = storeToRefs(comicStore).name
let imageList = storeToRefs(comicStore).imageList
let total = ref(comicStore.totalChapterCount)

let current = ref(0)

onMounted(() => {
	current.value = comicStore.currentChapterIndex + 1
	box.value.scrollTop = 0
})

const onChangeChapter = async index => {
	showLoading.value = true
	await comicStore.loadDownloadedImages(index-1)
	showLoading.value = false
	box.value.scrollTop = 0
}

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

.images-container {
	margin-top: 12vh;
    overflow-x: auto !important;
	max-width: min(600px, 100vw);
	height: 90vh;
}

.images-container::-webkit-scrollbar {
	display: none;
}

.single-image {
	width: 100%;
}
</style>