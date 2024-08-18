import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs/promises';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();

app.use(cors());
app.use(express.json());

// 設置靜態文件服務
app.use('/music', express.static(path.join(__dirname, '../public/music')));
app.use('/images', express.static(path.join(__dirname, '../public/512x512')));
app.use('/lyrics', express.static(path.join(__dirname, '../public/lyrics')));

// 讀取音樂數據的函數
async function readMusicData() {
  const dataPath = path.join(__dirname, 'musicData.json');
  try {
    const data = await fs.readFile(dataPath, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('Error reading music data:', error);
    throw error; // 將錯誤拋出，以便在路由處理中捕獲
  }
}

// 獲取音樂列表
app.get('/music', async (req, res) => {
  try {
    const musicData = await readMusicData();
    res.json(musicData);
  } catch (error) {
    console.error('Error in /music route:', error);
    res.status(500).json({ error: 'Error fetching music data', details: error.message });
  }
});

const PORT = process.env.PORT || 3548;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
