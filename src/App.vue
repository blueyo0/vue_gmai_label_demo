<template>
  <div id="app">
    <!-- <img src="./assets/logo.png"> -->
    <!-- <img src="./assets/logo_gmai_cutout.png" style="width: 100px; height: 150px"> -->
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
