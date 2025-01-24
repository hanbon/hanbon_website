<template>
  <div id="app">
    <ThreeBackground />
    <SearchComponent />
  </div>
</template>

<script>
import SearchComponent from './components/SearchComponent.vue';
import ThreeBackground from './components/ThreeBackground.vue';
export default {
  name: 'App',
  components: {
    SearchComponent,
    ThreeBackground
  }
}
</script>

<style>
body {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Icons", "Helvetica Neue", Helvetica, Arial, sans-serif;
  margin: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f5f7;
  color: #1d1d1f;
}

#app {
  font-family: inherit;
  text-align: center;
  position: relative;
  z-index: 1;
}

/* 添加深色模式支持 */
@media (prefers-color-scheme: dark) {
  body {
    background-color: #000000;
    color: #f5f5f7;
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  body {
    font-size: 16px;
  }
}
</style>
