<template>
  <div class="hello">
  <h1>GMAI-LABEL DEMO</h1>
    GMAI-LABEL 是由 GMAI 团队提供的医学3d数据可视化编辑和标注工具。<br><br>
    此页面为试用界面，支持功能：<br>
    1.对输入的CT影像进行100+类别的器官分割 <br>
    2.在 <a href="http://10.122.21.16:10010/" target="_blank"> GMAI-LABEL Viewer </a>界面进行可视化和编辑。<br>
    （demo仅作research用途）

  <h2>CT影像上传</h2>
  <form id="uploadForm" enctype="multipart/form-data">
  <p>
    <!-- <input type="file" id="fileInput" accept=".nii.gz, .zip"> -->
    <input type="file" id="fileInput" accept=".nii.gz">
  
    <b>模型选择</b>
    <select id="modelSelect" name="Model" >
      <option value="STUNetTrainer_small">STU-Net-small</option>
      <option value="STUNetTrainer_base" selected>STU-Net-base</option>
      <option value="STUNetTrainer_large">STU-Net-large</option>
      <option value="STUNetTrainer_huge">STU-Net-huge</option>
    </select>
  </p>
  
  
  <p>
    <input type="button" value="提交" @click="uploadFile">
    
    <input type="button" value="清除缓存" @click="clearLocal">
  </p>
  </form>
  <div class="uploaded-files">
    <h2>上传状态</h2>
    <div id="messageContainer"></div>
    <br>
    <h2>分割结果下载</h2>
    <div id="responsesContainer"></div>
    <br>
    <h3>其他链接</h3>
    <!-- （请耐心等待上传数据处理为可视化格式） -->
    <ul>
      <li>
        <a
          href="http://10.122.21.16:10010/"
          target="_blank"
        >
        影像可视化工具 GMAI-LABEL Viewer 
        </a>
      </li>
    </ul>
  </div>
</div>
</template>

<script>
export default {
  methods: {
    uploadFile() {
      handleUpload()
      console.log("call handleUpload()")
    },
    clearLocal() {
      clearLocalStorage()
        console.log("clear local")
    }
  }
}

function clearLocalStorage() {
    var responses = JSON.parse(localStorage.getItem('responses')) || [];
    localStorage.clear();
    displayResponses(responses);
}

function handleVisulization(uuid, fname) {
  var formData = new FormData();
  formData.append('uuid', uuid);
  formData.append('fname', fname);
  formData.append('name', uuid);
  formData.append('id', fname.replace(".nii.gz", ""));

  var responsesContainer = document.getElementById('responsesContainer');
  messageContainer.innerHTML = fname + '正在解析以提供可视化';
  
  var xhr = new XMLHttpRequest();
  xhr.open('POST', 'http://10.122.21.16:10030/visualization', true);
  xhr.onload = function () {
    if (xhr.status === 200) {
      messageContainer.innerHTML = fname + '解析完成';
    } else {
      messageContainer.innerHTML = fname + '解析失败，请检查数据';
    }
  };
  xhr.onerror = function () {
    messageContainer.innerHTML = fname + '解析失败，请检查数据';
  };
  xhr.send(formData);
  
}


function handleUpload() {
  var form = document.getElementById('uploadForm');
  var fileInput = document.getElementById('fileInput');
  var messageContainer = document.getElementById('messageContainer');
  var modelSelect = document.getElementById('modelSelect');

  var file = fileInput.files[0];
  if (!file) {
    messageContainer.innerHTML = '请选择要上传的文件';
    return;
  }
  var fileName = file.name;
  console.log("try to upload ", fileName);
  console.log("select trainer ", modelSelect.value);

  var formData = new FormData();
  formData.append('file', file);
  formData.append('trainer', modelSelect.value);

  var xhr = new XMLHttpRequest();
  xhr.open('POST', 'http://10.122.21.16:10030/upload', true);
  
  var responsesContainer = document.getElementById('responsesContainer');
  messageContainer.innerHTML = '正在上传';

  messageContainer.innerHTML = '正在处理';
  xhr.onload = function () {
    console.log('status', xhr.status)
    console.log('response', xhr.response)
    if (xhr.status === 200) {
      var responses = JSON.parse(localStorage.getItem('responses')) || [];
      responses.push(xhr.response);
      localStorage.setItem('responses', JSON.stringify(responses));

      messageContainer.innerHTML = fileName + ' 上传成功';
      
      var uuid2filename = new Map(JSON.parse(localStorage.getItem('uuid2filename'))) || new Map();
      uuid2filename.set(xhr.response, fileName);
      localStorage.setItem('uuid2filename', JSON.stringify(Array.from(uuid2filename.entries())));
      
      setTimeout(function() {
        displayResponses(responses);
      }, 3000);

    } else {
      messageContainer.innerHTML = '上传失败';
    }
  };
  xhr.onerror = function () {
    messageContainer.innerHTML = '上传失败';
  };
  xhr.send(formData);
}

function checkAndDownloadFile(uuid, fname) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', 'http://10.122.21.16:10030/download?uuid=' + uuid + "&fname=" + fname, true);
  xhr.onload = function() {
    if (xhr.status === 404) {
      alert(fname + '未处理好，请耐心等待');
    } else {
      const link = document.createElement('a');
      link.setAttribute('href', 'http://10.122.21.16:10030/download?uuid=' + uuid + "&fname=" + fname); //设置下载文件的url地址
      //link.setAttribute('download', 'download'); //用于设置下载文件的文件名
      link.click();
    }
  }
  xhr.onerror = function() {
    // 处理请求错误的逻辑
    alert(fname + '未处理好，请耐心等待');
  };
  xhr.send();
  
}

function displayResponses(responses) {
  var responsesContainer = document.getElementById('responsesContainer');
  var uuid2filename = new Map(JSON.parse(localStorage.getItem('uuid2filename'))) || new Map();
  responsesContainer.innerHTML = '';
  responses.forEach(function (response) {
    // var downloadLink = document.createElement('a');
    var fname = uuid2filename.get(response);
    if(!fname) {
      console.log("undefined uuid "+response)
      return; // like `continue`
    }
    // 创建容器元素
    var containerElement = document.createElement('div');
    containerElement.style.display = 'inline'; // 设置容器元素为行内显示

    var textElement = document.createElement('span');
    textElement.textContent = uuid2filename.get(response)+" (uuid:"+response+")"+"\t";
    containerElement.appendChild(textElement);
    
    // 创建按钮元素
    var buttonElement = document.createElement('button');
    buttonElement.textContent = '下载';
    buttonElement.addEventListener('click', function() {
      checkAndDownloadFile(response, uuid2filename.get(response));
    });
    containerElement.appendChild(buttonElement);
    
    // 创建按钮元素
    var buttonElement = document.createElement('button');
    buttonElement.textContent = '可视化';
    buttonElement.addEventListener('click', function() {
      handleVisulization(response, uuid2filename.get(response));
    });
    containerElement.appendChild(buttonElement);
    
    containerElement.appendChild(document.createElement('br'));
    // 将文本元素和按钮元素添加到容器元素中
    
    // 将容器元素添加到目标容器中
    responsesContainer.appendChild(containerElement);
  });
}

window.addEventListener('DOMContentLoaded', function () {
  var responses = JSON.parse(localStorage.getItem('responses')) || [];
  displayResponses(responses);
});
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
h3 {
  color: #099f5b;
}
</style>
