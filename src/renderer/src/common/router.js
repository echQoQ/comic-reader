import { createRouter, createWebHashHistory } from "vue-router"


let routes = [
    {
        path: "/",
        name: "index",
        component: () => import("@renderer/view/Home.vue"),
        meta: {
            title: "主页"
        }
    }, {
        path: "/chapters",
        name: "chapters",
        component: () => import("@renderer/view/Chapters.vue")
    }, {
        path: "/watch",
        name: "watch",
        component: () => import("@renderer/view/Watch.vue")
    }, {
        path: '/downloaded_comics',
        name: 'downloaded_comics',
        component: () => import('@renderer/view/DownloadedComics.vue')
    }, {
        path: '/downloaded_chapters',
        name: 'downloaded_chapters',
        component: () => import('@renderer/view/DownloadedChapters.vue')
    }, {
        path: '/downloaded_images',
        name: 'downloaded_images',
        component: () => import('@renderer/view/DownloadedImages.vue')
    }
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

export { router,routes }
