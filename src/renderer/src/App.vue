<script setup>
import { ref, reactive, inject, onMounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from "vue-router";
import { useComicStore } from '@renderer/common/store.js'
const comicStore = useComicStore()

import { HomeOutlined, LoadingOutlined, DownloadOutlined, RightCircleTwoTone, FileTextOutlined } from '@ant-design/icons-vue';

const notify = inject('notify')
const router = useRouter()
const route = useRoute()

const openMenu = ref(false)
const openModal = ref(false)

onMounted(async () => {
})

const rotate = computed(() => {
  if (openMenu.value) {
    console.log(90)
    return 90
  } else {
    console.log(0)
    return 0
  }
})

const code = ref('');

const editorOptions = {
  mode: 'javascript',
  theme: 'material-darker',
  lineNumbers: true,
  tabSize: 2, // 缩进大小
  lineWrapping: true,
  matchBrackets: true,
  autoCloseBrackets: true,
};

const loadSources = async () => {
  let res = await window.api.readSources()
  code.value = res.data
  openModal.value = true
}

const confirmLoading = ref(false)

const handleOk = async () => {
  confirmLoading.value = true
  await window.api.writeSources(code.value)
  notify("修改成功")
  reloadPage()
  openModal.value = false
  confirmLoading.value = false
  code.value = ""
}

const isRefreshFlag = ref(true)
function reloadPage() {
  isRefreshFlag.value = false
  nextTick(() => {
    isRefreshFlag.value = true
  })
}

const turnTo = name => {
  router.push({ name })
}

</script>

<template>
  <div class="main-container">
    <div class="lt">
      <a-dropdown :trigger="['click']" v-model:open="openMenu">
        <div class="dd-icon">
          <RightCircleTwoTone two-tone-color="#52c41a"  :rotate="rotate"  />
        </div>
        <template #overlay>
          <a-menu>
            <a-menu-item key="0" @click="loadSources">
              <FileTextOutlined />
              <span> 漫画源文件 </span>
            </a-menu-item>
            <a-menu-item key="1" @click="turnTo('downloaded_comics')">
              <DownloadOutlined />
              <span> 我的下载 </span>
            </a-menu-item>
            <!--
            <a-menu-divider />
            -->
          </a-menu>
        </template>
      </a-dropdown>
    </div>
    <div class="modal">
      <a-modal
        width="100%"
        v-model:open="openModal" 
        title="sources.json" 
        wrap-class-name="full-modal"
        @ok="handleOk"
        cancelText="取消"
        :confirm-loading="confirmLoading"
        okText="修改"
        >
        <div class="codemirror-container">
          <codemirror 
            class="codemirror"
            v-model="code" 
            :options="editorOptions"
          />
        </div>
      </a-modal>
    </div>
    <div>
      <router-view  v-if="isRefreshFlag"></router-view>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.lt {
  position: absolute;
  left: 12px;
  top: 12px;
}
.dd-icon {
  cursor: pointer;
  font-size: 25px;
  color: blueviolet;
}
.modal {
  max-height: 500px !important;
  .codemirror-container {
    max-height: 500px !important;
  }
}
</style>
