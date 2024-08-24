<template>
  <div class="flex h-screen">
    <Nav @page-changed="handlePageChange" />

    <!-- 音樂主頁 -->
    <div
      class="flex flex-col items-center max-sm:w-full flex-grow pb-8 rounded shadow-4xl"
    >
      <div
        class="bg-bule2 w-128 h-44 mt-11 max-lg:w-full flex flex-row shadow-4xl"
      >
        <div class="music-control w-full ml-10 pr-10">
          <!-- 音樂按鈕 -->
          <div class="button-container mt-2">
            <!-- 音樂按鈕 -->
            <div class="button-control flex text-white">
              <!-- 重複播放 -->
              <span
                class="cursor-pointer px-2 mb-5"
                :class="{ 'text-lightred': repeatButtonActive }"
                @click="toggleRepeat"
              >
                <i
                  class="fa-solid fa-arrow-rotate-left p-2 bg-gray-800 rounded-xl"
                ></i>
              </span>
            </div>
          </div>
          <div class="container mx-auto">
            <div class="flex flex-col items-center py-4">
              <!-- 歌曲標題 -->
              <div class="text-gray-800 text-lg font-medium mb-2">
                <template v-if="currentSong.title">{{
                  currentSong.title
                }}</template>
                <template v-else>請選擇歌曲</template>
              </div>
              <!-- 歌手名稱 -->
              <div class="text-gray-600 text-sm font-medium mb-4">
                <template v-if="currentSong.artist">{{
                  currentSong.artist
                }}</template>
                <template v-else>快點選</template>
              </div>

              <!-- 拉動條 -->
              <div
                class="pull w-full bg-slate-100 h-1 mt-2 relative"
                ref="progress"
                @mousedown="handleDragStart"
                @mousemove="handleDrag"
                @mouseup="handleDragEnd"
                @touchstart="handleDragStart"
                @touchmove="handleDrag"
                @touchend="handleDragEnd"
              >
                <div
                  class="push bg-blue4 h-full bg-black"
                  :style="{ width: progressBarWidth + '%' }"
                ></div>
                <div
                  class="slider-handle"
                  :style="{ left: progressBarWidth + '%' }"
                  @mousedown="handleDragStart"
                  @touchstart="handleDragStart"
                ></div>
                <div class="flex justify-between text-gray-600 text-sm mt-4">
                  <!-- 音樂時間 -->
                  <span>{{ formatTime(currentTime) }}</span>
                  <span>{{ formatTime(duration) }}</span>
                </div>
              </div>

              <div class="flex justify-center items-center mt-4 ml-2 pt-1">
                <!-- 上一首 -->
                <span
                  class="bg-transparent rounded-full px-2 py-1 mr-2"
                  @click="playPreviousSong"
                >
                  <i class="fas fa-backward"></i>
                </span>

                <!-- 播放和暫停 -->
                <span
                  class="bg-transparent rounded-full px-2 py-1 p-5 m-2"
                  @click="togglePlay"
                >
                  <span v-if="!isPlaying" class="icon">
                    <i class="fa fa-play" aria-hidden="true"></i>
                  </span>
                  <span v-else class="icon">
                    <i class="fa fa-pause" aria-hidden="true"></i>
                  </span>
                </span>

                <!-- 下一首 -->
                <span
                  class="bg-transparent rounded-full px-2 py-1 ml-2"
                  @click="playNextSong"
                >
                  <i class="fas fa-forward"></i>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- 音樂列表 -->
      <div
        class="bg-bule2 w-128 scroll-container max-lg:w-full max-sm:h-full pt-6 list overflow-y-auto shadow-2xl"
        v-show="currentPage === 'music'"
      >
        <div
          v-for="(item, index) in musicList"
          :key="item.id"
          class="flex items-center"
          @click="playMusic(item)"
        >
          <!-- 歌曲編號 -->
          <span class="text-gray-800 text-lg p-6">{{
            getNextNumber(index)
          }}</span>
          <!-- 歌曲封面圖片 -->
          <img
            class="h-9 w-9"
            :src="decodeURI(item.imageURL)"
            :alt="item.title"
          />
          <div class="ml-4">
            <!-- 歌曲標題 -->
            <div class="text-gray-900 font-medium text-lg">
              {{ item.title }}
            </div>
            <!-- 專輯名稱 -->
            <div class="text-lightred text-lg">{{ item.album }}</div>
          </div>
          <div class="ml-auto text-right">
            <!-- 歌曲時長 -->
            <span class="text-gray-500 text-sm p-4">{{ item.duration }}</span>
          </div>
        </div>
      </div>
      <!-- 歌词列表 -->
      <div
        class="bg-bule2 w-128 p-10 max-lg:w-full pt-6 scroll-container lyrics lyrics-container show-lyrics list overflow-hidden text-left pl-12 max-md:pl-6 lyrics"
        v-show="currentPage === 'lyrics'"
      >
        <template v-if="lrcParser && lrcParser.lines && lrcParser.lines.length">
          <div
            v-for="(line, index) in lrcParser.lines"
            :key="index"
            class="py-2 text-2xl"
            :class="[
              {
                'text-white': audioPlayer.currentTime * 1000 >= line.time,
                'text-black': audioPlayer.currentTime * 1000 < line.time,
              },
              { 'fade-in': audioPlayer.currentTime * 1000 >= line.time },
            ]"
            style="text-shadow: 3px 3px 8px rgba(0, 0, 0, 0.3)"
            :ref="`line-${index}`"
          >
            {{ line.text }}
          </div>
        </template>
        <div
          class="flex h-full items-center justify-center pb-20 text-2xl"
          v-else
        >
          <p>暫無歌詞</p>
        </div>
      </div>
    </div>
    <div></div>
  </div>
</template>

<script>
import "../index.css";
import Nav from "./Nav.vue";
import axios from "axios";
import Lyric from "lrc-file-parser";

export default {
  components: {
    Nav,
  },

  data() {
    return {
      currentSong: {
        title: "",
      },
      musicList: [], //歌單
      currentSongLyrics: [], //歌詞
      nextNumber: 1,
      startX: 0,
      isDragging: false,
      currentTime: 0,
      duration: 0,
      audioPlayer: null,
      progressBarWidth: 0,
      isPlaying: false,
      rewindSeconds: 5,
      fastForwardSeconds: 5,
      currentPage: "music",
      isRepeat: false, // 是否為重複播放模式
      repeatButtonActive: false, // 重複播放按鈕是否激活
      lrcParser: null, // 歌詞解析實例
      currentLineIndex: 0,
    };
  },

  computed: {
    getNextNumber() {
      return (index) => {
        const number = (index + 1).toString().padStart(2, "0");
        return number;
      };
    },
    isPaused() {
      return this.audioPlayer && this.audioPlayer.paused;
    },
  },

  mounted() {
    axios
      .get("")
      .then((response) => {
        // 成功獲取資料後，將歌曲列表資料存儲到 `musicList` 陣列中
        this.musicList = response.data;

        // 在 "lrc-file-parser" 的初始化中
        this.lrcParser = new Lyric({
          onPlay: (line, text, index) => {
            this.currentLyricLine = text;

            this.$nextTick(() => {
              const lyricContainer =
                this.$el.querySelector(".lyrics-container");
              if (
                this.$refs[`line-${index}`] &&
                this.$refs[`line-${index}`].length > 0
              ) {
                const targetLine = this.$refs[`line-${index}`][0];

                if (targetLine && lyricContainer) {
                  const containerCenter = lyricContainer.clientHeight / 2;
                  const offset =
                    targetLine.offsetTop +
                    targetLine.clientHeight / 2 -
                    containerCenter;
                  lyricContainer.scrollTop = offset;
                }
              }
            });
          },

          onSetLyric: (lines) => {
            // ...
          },
          offset: 150,
        });
      })
      .catch((error) => {
        console.error("Error fetching songs:", error);
      });
    // 確保audioPlayer存在，然後添加事件監聽器
    if (this.audioPlayer) {
      this.audioPlayer.addEventListener("timeupdate", this.updateLyricPosition);
    }
    // 空白鍵
    document.addEventListener("keydown", this.handleKeyDown);
    // 創建無聲音頻對象
    this.silentAudio = new Audio("/nomusic.mp3");
    this.silentAudio.loop = true;

    // 設置用戶交互事件監聽器
    document.addEventListener("click", this.userInteracted);
    document.addEventListener("touchstart", this.userInteracted);
    document.addEventListener("keydown", this.userInteracted);

    // 使用定時器定期重啟無聲音頻
    setInterval(() => {
      if (this.silentAudio.paused) {
        this.playSilentAudio();
      }
    }, 30000); // 每30秒檢查一次
  },

  beforeUnmount() {
    // 移除滑鼠移動事件的綁定
    this.$refs.progress.removeEventListener("mousemove", this.handleDrag);
    // 移除滑鼠放開事件的綁定
    document.removeEventListener("mouseup", this.handleDragEnd);
    document.removeEventListener("touchend", this.handleDragEnd);
    document.removeEventListener("keydown", this.handleKeyDown);
  },

  methods: {
    playSilentAudio() {
      this.silentAudio.play().catch((error) => {
        console.error("Error playing silent audio:", error);
      });
    },

    userInteracted() {
      this.playSilentAudio();
      document.removeEventListener("click", this.userInteracted);
      document.removeEventListener("touchstart", this.userInteracted);
      document.removeEventListener("keydown", this.userInteracted);
    },
    toggleRepeat() {
      this.isRepeat = !this.isRepeat;
      this.repeatButtonActive = this.isRepeat;
    },

    handlePageChange(page) {
      this.currentPage = page;
    },
    handleKeyDown(event) {
      switch (event.keyCode) {
        case 32: // 空白鍵
          event.preventDefault(); // 防止空白鍵滾動頁面
          this.togglePlay(); // 切換播放和暫停

          if (this.isPlaying) {
            this.lrcParser.play(); // 播放歌詞
          } else {
            this.lrcParser.pause(); // 暫停歌詞
          }
          break;
        case 37: // 左鍵
          event.preventDefault();
          this.rewind(5); // 往後跳5秒
          this.lrcParser.pause(); // 快轉時暫停歌詞
          break;
        case 39: // 右鍵
          event.preventDefault();
          this.fastForward(5); // 往前跳5秒
          this.lrcParser.pause(); // 倒轉時暫停歌詞
          break;
        default:
          break;
      }
    },
    rewind(seconds) {
      if (this.audioPlayer) {
        this.audioPlayer.currentTime = Math.max(
          0,
          this.audioPlayer.currentTime - seconds
        );
        this.lrcParser.play(this.audioPlayer.currentTime * 1000); // 保持歌詞與音樂同步
      }
    },

    fastForward(seconds) {
      if (this.audioPlayer) {
        this.audioPlayer.currentTime = Math.min(
          this.audioPlayer.duration,
          this.audioPlayer.currentTime + seconds
        );
        this.lrcParser.play(this.audioPlayer.currentTime * 1000); // 保持歌詞與音樂同步
      }
    },

    // 設置媒體會話的快退和快進動作
    setupMediaSession() {
      navigator.mediaSession.setActionHandler("previoustrack", this.rewind);
      navigator.mediaSession.setActionHandler("nexttrack", this.fastForward);
      navigator.mediaSession.setActionHandler("play", () =>
        this.audioPlayer.play()
      );
      navigator.mediaSession.setActionHandler("pause", () =>
        this.audioPlayer.pause()
      );
    },

    togglePlay() {
      // 切換播放和暫停狀態
      if (this.audioPlayer) {
        if (this.audioPlayer.paused) {
          this.audioPlayer.play();
          this.isPlaying = true;
          this.lrcParser.play(this.audioPlayer.currentTime * 1000); // 啟動歌詞播放
          this.updateProgress(); // 手動調用更新播放進度條的方法
        } else {
          this.audioPlayer.pause();
          this.isPlaying = false;
          // 不再在這裡調用 lrcParser.seek
        }
      }
    },

    updatePlayButtonIcon(isPlaying) {
      // 更新播放按鈕圖標顯示
      const playButtonIcon = document.querySelector(".fa-play");
      const pauseButtonIcon = document.querySelector(".fa-pause");
      if (playButtonIcon && pauseButtonIcon) {
        if (isPlaying) {
          playButtonIcon.style.display = "none";
          pauseButtonIcon.style.display = "inline-block";
        } else {
          playButtonIcon.style.display = "inline-block";
          pauseButtonIcon.style.display = "none";
        }
      }
    },
    clearAudioListeners() {
      if (this.audioPlayer) {
        this.audioPlayer.removeEventListener(
          "timeupdate",
          this.updateLyricPosition
        );
        this.audioPlayer.removeEventListener("timeupdate", this.updateProgress);
        this.audioPlayer.removeEventListener("ended", this.playNextSong);
      }
    },
    playMusic(song) {
      // 如果此歌曲還沒有 Audio 對象，則建立之
      if (!song.audioPlayer) {
        song.audioPlayer = new Audio(song.url);
        song.audioPlayer.addEventListener("loadedmetadata", () => {
          song.duration = this.formatTime(song.audioPlayer.duration);
        });
      }

      if (this.audioPlayer && !this.audioPlayer.paused) {
        this.audioPlayer.pause();
      }

      this.clearAudioListeners();

      if (this.currentSong === song) {
        this.audioPlayer.currentTime = 0;
        if (!this.isPlaying) {
          this.audioPlayer.play();
          this.isPlaying = true;
          this.updateProgress(); // 手動調用更新播放進度條的方法
        }
      } else {
        this.audioPlayer = song.audioPlayer;
        this.audioPlayer.addEventListener(
          "timeupdate",
          this.updateLyricPosition
        );

        // 開始新的歌曲
        this.currentSong = song;
        const audioPlayer = song.audioPlayer;
        audioPlayer.addEventListener("timeupdate", () => {
          // console.log('Time updated:', audioPlayer.currentTime);
          this.updateProgress();
        }); // 添加時間更新事件監聽器
        audioPlayer.addEventListener("ended", this.playNextSong);
        audioPlayer.currentTime = 0;
        song.number = this.getNextNumber(this.musicList.indexOf(song));
        audioPlayer.play();
        this.audioPlayer = audioPlayer;
        this.isPlaying = true;

        axios
          .get(song.lyrics)
          .then((response) => {
            this.lrcParser.setLyric(response.data);

            this.lrcParser.onPlay = (line, text) => {
              // 如果當前播放的歌詞與上一行相同，則直接返回
              if (text === this.currentLyricLine) return;

              // 如果歌曲不在播放狀態，則不進行滾動
              if (!this.isPlaying) return;

              this.currentLyricLine = text;

              this.$nextTick(() => {
                const lyricContainer =
                  this.$el.querySelector(".lyrics-container");
                const targetLine = this.$refs[`line-${line}`][0];

                if (targetLine && lyricContainer) {
                  // 計算歌詞容器的中心位置
                  const containerCenter = lyricContainer.clientHeight / 1.4;

                  // 計算將目標歌詞行移至容器中心所需的偏移量
                  const offset =
                    targetLine.offsetTop +
                    targetLine.clientHeight / 3 -
                    containerCenter;
                  lyricContainer.scrollTop = offset;
                }
              });
            };

            this.lrcParser.play(0);
          })
          .catch((error) => {
            console.error("Error fetching lyrics:", error);
            this.currentSongLyrics = [];
          });
      }

      setTimeout(() => {
        const mediaMetadata = new window.MediaMetadata({
          title: song.title,
          artist: song.artist,
          album: song.album,
          artwork: [
            { src: song.imageURL, sizes: "512x512", type: "image/png" },
          ],
        });

        navigator.mediaSession.setActionHandler("seekto", (details) => {
          if (details.fastSeek && "fastSeek" in this.audioPlayer) {
            this.audioPlayer.fastSeek(details.seekTime);
          } else {
            this.audioPlayer.currentTime = details.seekTime;
          }
        });

        navigator.mediaSession.setActionHandler("nexttrack", this.playNextSong);
        navigator.mediaSession.setActionHandler(
          "previoustrack",
          this.playPreviousSong
        );
        navigator.mediaSession.setActionHandler("play", () =>
          this.togglePlay()
        );
        navigator.mediaSession.setActionHandler("pause", () =>
          this.togglePlay()
        );

        navigator.mediaSession.metadata = mediaMetadata;
      }, 100);
    },

    scrollLyricToCurrentTime() {
      const currentTimeMs = this.audioPlayer.currentTime * 1000;
      const index = this.lrcParser.lines.findIndex(
        (line) => line.time > currentTimeMs
      );

      const lyricContainer = this.$el.querySelector(".lyrics-container");
      const targetLine = this.$refs[`line-${index - 1}`]
        ? this.$refs[`line-${index - 1}`][0]
        : null;

      if (targetLine && lyricContainer) {
        const containerCenter = lyricContainer.clientHeight / 1.4;
        const offset =
          targetLine.offsetTop + targetLine.clientHeight / 7 - containerCenter; // 調整這裡的分母
        lyricContainer.scrollTop = offset;
      }
    },

    playNextSong() {
      const currentIndex = this.musicList.findIndex(
        (item) => item === this.currentSong
      );
      let nextIndex;
      if (this.isRepeat) {
        // 如果處於重複播放模式，將下一首歌曲索引設置為當前索引，這樣將重新播放當前歌曲。
        nextIndex = currentIndex;
        this.audioPlayer.currentTime = 0;
        // 在循環播放模式下，更新播放時間並啟動歌詞播放
        this.updateProgress();
        this.lrcParser.play(this.audioPlayer.currentTime * 1000);
        // 手動調用更新播放進度條的方法
        this.updateProgress();
      } else {
        // 否則，切換到下一首歌曲。
        nextIndex = (currentIndex + 1) % this.musicList.length;
      }
      const nextSong = this.musicList[nextIndex];

      // 播放音樂
      this.playMusic(nextSong);

      if (this.isRepeat) {
        this.audioPlayer.play(); // 在重播模式下自動播放
      }
    },

    playPreviousSong() {
      const currentIndex = this.musicList.findIndex(
        (item) => item === this.currentSong
      );
      let previousIndex;
      if (this.isRepeat) {
        // 如果处于重复播放模式，将上一首歌曲索引设置为当前索引，这样将重新播放当前歌曲。
        previousIndex = currentIndex;
        this.audioPlayer.currentTime = 0;
      } else {
        // 否则，按照常规逻辑计算上一首歌曲的索引。
        previousIndex = currentIndex - 1;
        if (previousIndex < 0) {
          previousIndex = this.musicList.length - 1;
        }
      }
      const previousSong = this.musicList[previousIndex];

      // 播放上一首歌曲
      this.playMusic(previousSong);
      if (this.isRepeat) {
        this.audioPlayer.play(); // 在重播模式下自动播放
      }
    },

    updateProgress() {
      // 更新播放进度条
      const audioPlayer = this.audioPlayer;
      this.currentTime = audioPlayer.currentTime;
      this.duration = audioPlayer.duration;
      this.progressBarWidth = (this.currentTime / this.duration) * 100;

      // 使用 lrcParser.play 方法来同步播放歌词
      this.lrcParser.play(this.currentTime * 1000); // 将秒数转换为毫秒数
    },

    formatTime(time) {
      // 格式化時間為分:秒的形式
      const minutes = Math.floor(time / 60);
      const seconds = Math.floor(time % 60);
      return `${minutes}:${seconds.toString().padStart(2, "0")}`;
    },

    handleDrag(event) {
      // 拖動進度條事件
      if (this.isDragging) {
        event.preventDefault();
        const progressContainerWidth = this.$refs.progress.offsetWidth;
        const progressContainerLeft =
          this.$refs.progress.getBoundingClientRect().left;
        const currentX = event.clientX || event.touches[0].clientX;
        const offsetX = currentX - progressContainerLeft;
        const progressBarWidth = Math.max(
          0,
          Math.min((offsetX / progressContainerWidth) * 100, 100)
        );
        this.progressBarWidth = progressBarWidth;
        const seekTime = (progressBarWidth / 100) * this.duration;
        this.audioPlayer.currentTime = seekTime;
      }
    },

    handleDragStart(event) {
      // 开始拖动进度条事件
      event.preventDefault();
      this.isDragging = true;
      this.startX = event.clientX || event.touches[0].clientX;
      if ("ontouchstart" in window) {
        // 如果是触摸设备
        document.addEventListener("touchmove", this.handleDrag, {
          passive: true,
        });
        document.addEventListener("touchend", this.handleDragEnd, {
          passive: true,
        });
      } else {
        // 如果不是触摸设备
        document.addEventListener("mousemove", this.handleDrag);
        document.addEventListener("mouseup", this.handleDragEnd);
      }

      // 在拖动前记录音乐的播放状态和歌词播放状态
      this.wasPlayingBeforeDrag = this.isPlaying;
      this.wasLrcPlayingBeforeDrag = this.lrcParser.isPlaying;
      this.lrcParser.pause();
      this.isLrcPlaying = false;
    },
    handleDragEnd() {
      if (this.isDragging) {
        this.isDragging = false;
        const progressContainerWidth = this.$refs.progress.offsetWidth;
        const seekTime = (this.progressBarWidth / 100) * this.duration;
        this.audioPlayer.currentTime = seekTime;

        // 將歌詞滾動到對應位置
        this.scrollLyricToCurrentTime();

        // 根據拖動前的音樂播放狀態決定是否繼續播放
        if (this.wasPlayingBeforeDrag) {
          this.audioPlayer.play();
          this.lrcParser.play(this.audioPlayer.currentTime * 1000); // 啟動歌詞播放
        }
        document.removeEventListener("mousemove", this.handleDrag);
        document.removeEventListener("touchmove", this.handleDrag);
        document.removeEventListener("mouseup", this.handleDragEnd);
        document.removeEventListener("touchend", this.handleDragEnd);

        // 創建新的 mediaMetadata 物件
        const mediaMetadata = new window.MediaMetadata({
          title: this.currentSong.title,
          artist: this.currentSong.artist,
          album: this.currentSong.album,
          artwork: [
            {
              src: this.currentSong.imageURL,
              sizes: "512x512",
              type: "image/png",
            },
          ],
        });

        navigator.mediaSession.metadata = mediaMetadata;
      }
    },
  },
};
</script>

<style scoped>
p,
input,
label,
div {
  font-family: CUBIC;
  user-select: none;
}

.pull {
  position: relative;
  cursor: pointer;
}

.push {
  position: absolute;
  top: 0;
  left: 0;
}

.slider-handle {
  position: absolute;
  top: -10px;
  left: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: white;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  transform: translateX(-50%);
}

.button-container {
  position: absolute;
  top: 1px;
  left: 80px;
  /* 距離左側的距離 */
  display: flex;
  flex-direction: row;
}

.button-control {
  display: flex;
  align-items: center;
}

.button-control span {
  margin-right: 10px;
}

@media (max-width: 640px) {
  /* 在手機上將按鈕置於左上角 */
  .button-container {
    top: -2px;
    left: 1rem;
  }
}

::-webkit-scrollbar {
  /*隐藏滚轮*/
  display: none;
}

.lyrics-container {
  height: 200px;
  /* Set a fixed height for the container */
  overflow-y: hidden;
  /* Hide overflow */
}

.lyric-line {
  margin-bottom: 20px;
  opacity: 0;
  /* Initially hide the lines */
  transform: translateY(100%);
  /* Move lines offscreen */
  transition: opacity 0.5s ease, transform 0.5s ease;
  /* Add transition effect */
}

/* Apply animation when lines are in view */
.lyrics-container.show-lyrics .lyric-line {
  opacity: 1;
  transform: translateY(0);
  animation: fade-in 0.5s ease forwards;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(100%);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.scroll-container {
  height: 48vh;
  /* 設定容器高度 */
  transition: scroll-behavior 0.5s;
  /* 添加滑動過渡效果，持續時間為0.5秒 */
  scroll-behavior: smooth;
  /* 使用平滑的滾動行為 */
}
</style>
