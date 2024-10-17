<template>
	<div class="breadcrumb">
		<a-breadcrumb>
			<a-breadcrumb-item> <a @click="router.push({name: 'index'})"> <HomeOutlined /> Home</a></a-breadcrumb-item>
			<a-breadcrumb-item><div class="p1">{{ name }}</div></a-breadcrumb-item>
		</a-breadcrumb>
	</div>
	<div class="modal">
		<a-drawer v-model:open="open1">
			<template #title>
                <div>
                    <div class="title">下载漫画</div>
                </div>
            </template>
			<div>
				<a-checkbox v-model:checked="chooseAll" @change="chooseAllChapters">
					全选
				</a-checkbox>
			</div>
			<div class="checkbox-list-container">
				<div v-for="(item,index) in options" :key="index" class="checkbox-list">
					<div class="checkbox">
						<a-checkbox v-model:checked="item.checked" :disabled="item.state !== 0">
							{{item.title}}
							<CheckOutlined v-if="item.state == 2" />
							<LoadingOutlined  v-if="item.state == 1"/>
						</a-checkbox>
					</div>
				</div>
			</div>

			<a-empty v-if="options.length === 0"></a-empty>

			<a-divider></a-divider>
			
			<div class="content">
				<div class="download-btn">
					<a-button :disabled="dis" @click="downloadChapters" :icon="h(DownloadOutlined)" :loading="doing">
						下载
					</a-button>
					<PauseCircleTwoTone style="font-size: 20px;margin: 10px;" v-if="doing" @click="stopDownload" />
				</div>
			</div>
		</a-drawer>
	</div>
	<div class="spinning" v-if="showLoading">
		<a-spin 
		size="large" 
		tip="Loading"
		:indicator="indicator"
		/>
	</div>
	<div class="container">
		<div class="download">
			<a-button @click="openModal1" :icon="h(DownloadOutlined)">
			</a-button>
			<a-button @click="swapChapters" style="margin-left: 10px;" :icon="h(SwapOutlined)">
			</a-button>
		</div>
		<a-divider style="margin: 5px; border-color: black;"></a-divider>
		<div style="display: flex;">
			<div class="chapter-list-container">
				<a-button class="single-chapter" v-for="(item, index) in chapterList" @click="goToWatch(index)">{{ item.title }}</a-button>
				<a-empty v-if="chapterList.length === 0"></a-empty>
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

import { DownloadOutlined, HomeOutlined, LoadingOutlined, CheckOutlined, PauseCircleTwoTone, SwapOutlined } from '@ant-design/icons-vue';

let chapterList = storeToRefs(comicStore).chapterList
let name = storeToRefs(comicStore).name

const indicator = h(LoadingOutlined, {
    style: {
      fontSize: '50px',
    },
    spin: true,
});

const showLoading = ref(false)
const chooseAll = ref(true)

const returnToHome = async () => {
    router.push('/')
}

const goToWatch = async (index) => {
	showLoading.value = true
	await comicStore.loadImages(index)
	showLoading.value = false
	router.push({ path: '/watch' })
}

const open1 = ref(false)
const options = ref([])
const loadOptions = async () => {
	options.value = chapterList.value.map((item, index) => ({ 
		title: item.title,
		href: item.href,
		checked: true,
		state: 0,
		index: index
	}))
	//console.log(options.value)
	try {
        const res = await axios.post('load_downloaded_chapters', {
          'comic_name': comicStore.name
        })

        if (res.status === 200) {
          let loadedChapterList = res.data.data
		  console.log(res.data.data)
          for (let i = 0; i < options.value.length; i++) {
			    for (let j=0; j < loadedChapterList.length; j++) {
					if (options.value[i].title === loadedChapterList[j]) {
                        options.value[i].state = 2
						break;
                    }
				}
			}
        }
      } catch(err) {
        console.error(err)
      }
}

const openModal1 = async () => {
    open1.value = true
}

let stopFlag = false; // 中止标志

const doing = ref(false)

const downloadChapters = async () => {
    stopFlag = false; // 在开始下载前重置中止标志
    doing.value = true;
    for (let i = 0; i < options.value.length; i++) {
        if (stopFlag) {
            console.log('下载中止');
            doing.value = false;
            notify('下载中止');
            return;
        }

        if (options.value[i].checked && options.value[i].state === 0) {
            options.value[i].state = 1;
            try {
                let res = await axios.post('download_chapter', {
                    comic_name: comicStore.name,
                    chapter_name: options.value[i].title,
                    chapter_href: options.value[i].href,
                    adapter: sessionStorage.getItem('adapter'),
                });
                options.value[i].state = 2;
            } catch (error) {
                console.error('下载失败:', error);
            }
        }
    }
    doing.value = false;
    notify('下载成功');
};

// 停止任务的函数
const stopDownload = () => {
    stopFlag = true; 
	notify('下一话将停止下载')
};

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

const swapChapters = () => {
	chapterList.value.reverse()
}

onMounted( async () => {
	await loadOptions()
})

const chooseAllChapters = () => {
	for (let i = 0; i < options.value.length; i++) {
		options.value[i].checked = chooseAll.value
	}
}

</script>

<style scoped lang="scss">
.breadcrumb {
	position: absolute;
	top: 20px;
	left: 50px;
    a {
        color: rgb(0, 0, 0);
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
}

.container {
	color: white;
	margin-top: 120px;
	display: flex;
	flex-direction: column;
	.download {
		float: right;
		padding: 0px;
	}
}

.chapter-list-container {
	display: flex;
    flex-wrap: wrap;
	justify-content:safe;
    overflow-x: auto;
	max-width: 60vw;
	max-height: 80vh;
	min-width: 40vw;
	min-height: 50vh;
	.single-chapter {
		margin: 3px;
		background-color: blueviolet;
        cursor: pointer;
        &:hover {
            background-color: #556;
        }
	}
}

.chapter-list-container::-webkit-scrollbar {
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