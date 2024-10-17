import { defineStore } from 'pinia'
import { inject } from 'vue'
import axios from 'axios'

export const useComicStore = defineStore('comic', {
  state: () => {
    return {
      name: '',
      url: '',
      cover_img: '',
      chapterList: [],
      imageList: [],
      currentChapterIndex: 0,
    }
  },
  getters: {
    currentChapterHref: (state) => {
      return state.chapterList[state.currentChapterIndex].href
    },
    currentChapterTitle: (state) => {
      return state.chapterList[state.currentChapterIndex].title ? state.chapterList[state.currentChapterIndex].title: state.chapterList[state.currentChapterIndex]
    },
    totalChapterCount: (state) => {
      return state.chapterList.length
    }
  },
  actions: {
    async loadComic (name, cover_img, url) {
      this.name = name
      this.cover_img = cover_img
      this.url = url
      try {
        const response = await axios.post('load_chapters', {
          comic_url: this.url,
          adapter: sessionStorage.getItem('adapter')
        })

        if (response.status === 200) {
          this.chapterList = response.data
        }
        
      } catch(err) {
        console.error(err)
      }
    },
    async loadDownloadedComic (name) {
      this.name = name
      try {
        const res = await axios.post('load_downloaded_chapters', {
          'comic_name': this.name
        })

        if (res.status === 200) {
          this.chapterList = res.data.data
          console.log(this.chapterList)
        }
      } catch(err) {
        console.error(err)
      }
    },
    async loadImages (chapter_index) {
      this.currentChapterIndex = chapter_index
      let chapter_href = this.currentChapterHref
      try {
        const response = await axios.post('load_images', {
          chapter_href,
          adapter: sessionStorage.getItem('adapter')
        })

        if (response.status === 200) {
          this.imageList = response.data
        }
      } catch(err) {
        console.error(err)
      }
    },
    async loadDownloadedImages(chapter_index) {
      this.currentChapterIndex = chapter_index
      let chapter_name = this.chapterList[this.currentChapterIndex]
      try {
        const response = await axios.post('load_downloaded_images', {
          comic_name: this.name,
          chapter_name: chapter_name
        })

        if (response.status === 200) {
          this.imageList = response.data.data
          for (let i = 0; i < this.imageList.length; i++) {
            this.imageList[i] = import.meta.env.VITE_SERVER_URL + this.imageList[i]
          }
          console.log(this.imageList)
        }
      } catch(err) {
        console.error(err)
      }
    }
  }
})
