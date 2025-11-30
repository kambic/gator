<template>
  <div>
    <vue-finder
      id="my_vuefinder"
      :driver="driver"
      :config="{
        initialPath: 'local://public',
        persist: true,
      }"
    />

  </div>
</template>

<script setup>
import { RemoteDriver, VueFinder } from 'vuefinder'

const driver = new RemoteDriver({
  baseURL: '/files',
  url: {
    list: '/files',
    upload: '/upload',
    delete: '/delete',
    rename: '/rename',
    archive: '/archive',
    unarchive: '/unarchive',
    createFile: '/create-file',
    createFolder: '/create/',
    search: '/search',
    preview: '/preview',
    copy: '/copy',
    move: '/move',
    save: '/save',
    download: '/download',
  },
})
</script>
