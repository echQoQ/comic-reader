<template>
	<div>
		<div class="breadcrumb">
			<a-breadcrumb>
				<a-breadcrumb-item> <a @click="router.push({name: 'index'})"> <HomeOutlined /> Home</a></a-breadcrumb-item>
				<a-breadcrumb-item><div class="p1"><DownloadOutlined /> 我的下载</div></a-breadcrumb-item>
			</a-breadcrumb>
		</div>
		
		<div class="spinning" v-if="showLoading">
			<a-spin 
			size="large" 
			tip="Loading"
			:indicator="indicator"
			/>
		</div>

		<div class="modal">
			<a-drawer v-model:open="open1">
				<template #title>
					<div>
						<div class="title">删除漫画</div>
					</div>
				</template>
				<div>
					<a-checkbox v-model:checked="chooseAll" @change="chooseAllComics">
						全选
					</a-checkbox>
				</div>
				<div class="checkbox-list-container">
					<div v-for="(item,index) in options" :key="index" class="checkbox-list">
						<div class="checkbox">
							<a-checkbox v-model:checked="item.checked" :disabled="item.state !== 0">
								{{item.title}}
								<LoadingOutlined v-if="item.state == 1"/>
								<div v-if="item.state == 2">已删除</div>
							</a-checkbox>
						</div>
					</div>
				</div>

				<div v-if="options.length === 0">
					<a-empty></a-empty>
				</div>

				<a-divider></a-divider>
				
				<div class="content">
					<div class="delete-btn">
						<a-button :disabled="dis" @click="deleteComics" :icon="h(DeleteTwoTone)" :loading="doing">
							删除
						</a-button>
					</div>
				</div>
			</a-drawer>
		</div>

		<div class="container">
			<div class="setting">
				<a-button @click="openModal1" :icon="h(DeleteTwoTone)">
				</a-button>
			</div>
			<a-divider style="margin: 5px;"></a-divider>
			<div class = "comic-list-container">
				<div v-for="item in comics" class="comic-list">
					<a-button style="background-color: blue;color: white;" @click="loadChapters(item)">
						{{ item }}
					</a-button>
				</div>
				<div v-if="comics.length === 0">
					<a-empty></a-empty>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, reactive, inject, onMounted, h, computed } from 'vue'
import { useRoute, useRouter } from "vue-router";
import { storeToRefs } from 'pinia'

import { useComicStore } from '@renderer/common/store.js'

const comicStore = useComicStore()
import axios from "axios"
const notify = inject('notify')
const router = useRouter()
const route = useRoute()

import { DownloadOutlined, HomeOutlined, LoadingOutlined, DeleteTwoTone } from '@ant-design/icons-vue';

const indicator = h(LoadingOutlined, {
    style: {
      fontSize: '50px',
    },
    spin: true,
});

const showLoading = ref(false)

const comics = ref([])

const loadChapters = async name => {
	showLoading.value = true
	await comicStore.loadDownloadedComic(name)
	showLoading.value = false
	router.push({name: 'downloaded_chapters'})
}

onMounted(async () => {
	try {
		let res = await axios.post('/load_downloaded_comics')
		if (res.status == 200) {
			comics.value = res.data.data
		}
		await loadOptions()
	} catch (e) {
		console.log(e)
	}
})

const chooseAll = ref(false)
const doing = ref(false)
const open1 = ref(false)
const options = ref([])
const loadOptions = async () => {
	options.value = comics.value.map((item, index) => ({ 
		title: item,
		checked: false,
		state: 0,
		index: index
	}))
}
const openModal1 = async () => {
    open1.value = true
}
const chooseAllComics = () => {
	for (let i = 0; i < options.value.length; i++) {
		options.value[i].checked = chooseAll.value
	}
}
const dis = computed(() => {
	if (doing.value) {
		return true
	}
	for (let i = 0; i < options.value.length; i++) {
		if (options.value[i].state === 0 && options.value[i].checked) {
            return false;
        }
	}
	return true;
})

const deleteComics = async () => {
	try {
		doing.value = true
		for (let i = 0; i < options.value.length; i++) {
			if (options.value[i].checked) {
				options.value[i].state = 1
				let res = await axios.post('delete_comic', {
					comic_name: options.value[i].title
				})
				options.value[i].state = 2
				comics.value.splice(comics.value.findIndex(item => item === options.value[i].title), 1)
			}
		}
	} catch (err) {
		console.error(err)
	}
	doing.value = false
}




</script>

<style scoped lang="scss">
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
.comic-list-container {
	display: flex;
	flex-wrap: wrap;
	justify-content:safe;
    overflow-x: auto;
	max-width: min(600px, 100vw);
	max-height: 80vh;
	min-width: 40vw;
	min-height: 50vh;
	.comic-list {
		padding: 10px;
	}
}
.container {
	color: white;
	margin-top: 80px;
	display: flex;
	flex-direction: column;
	.setting {
		float: right;
		padding: 5px;
	}
}

.comic-list-container::-webkit-scrollbar {
	display: none;
}

.checkbox-list-container {
	display: flex;
    flex-wrap: wrap;
	.checkbox-list {
		margin-left: 20px;
		width: 40%;
	}
}

</style>