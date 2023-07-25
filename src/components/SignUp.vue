<template>
    <div>
  <h1>GMAI-LABEL DEMO</h1>
    GMAI-LABEL 是由 GMAI 团队提供的医学3d数据可视化编辑和标注工具。<br><br>
    此页面为试用界面，支持功能：<br>
    1.对输入的CT影像进行100+类别的器官分割 <br>
    2.在 <a href="http://10.122.21.16:10010/" target="_blank"> GMAI-LABEL Viewer </a>界面进行可视化和编辑。<br>
    （demo仅作research用途）<br><br>

      <h2>注册</h2>
      <form @submit.prevent="signup">
        <label for="username">用户名：</label>
        <input type="text" id="username" v-model="username" required>
        <br>
        <label for="password">密码：</label>
        <input type="password" id="password" v-model="password" required>
        <br>
        <button type="submit">注册</button>
        <p>已有账号？<router-link to="/login">登录</router-link></p>
      </form>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        username: '',
        password: ''
      };
    },
    methods: {
      signup() {
        console.log('正在注册...');
        console.log('用户名：', this.username);
        console.log('密码：', this.password);
      }
    }
  };
  </script>
  