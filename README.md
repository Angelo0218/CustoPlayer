# 自定義音樂播放器

這是一個使用 Node.js 和 Vue 3 搭建的自定義音樂播放器，允許用戶上傳音樂和歌詞。

## 技術棧

- **後端**: Node.js
- **前端**: Vue 3

## 功能

- 上傳音樂文件
- 上傳對應的歌詞文件
- 播放音樂
- 在 PWA 中保持活動，避免被系統刪除

## 文件結構

- `public/music`：存放音樂文件
- `public/lyrics`：存放歌詞文件
- `musicData.json`：存放音樂數據的 JSON 文件

## 後端說明

後端使用 Node.js 搭建，包含了靜態文件服務和音樂數據的讀取功能。

## PWA 音樂播放限制解決方案

為了解決 iOS PWA 音樂播放的限制，我們使用無聲音樂來保持 PWA 活動。



## 前端設置

在 `mounted` 方法中，請修改 Axios 請求：
請確保將 axios.get 中的空字符串替換為你的音樂 API URL。
```javascript
axios
  .get("")  // 在這裡填入你的音樂 API URL
  .then((response) => {
    this.musicList = response.data;
  })
  .catch((error) => {
    console.error("Error fetching songs:", error);
    alert("請檢查您的音樂 API URL 是否正確，並確保伺服器正在運行。");
  });
  


