<template>
  <div>
    <!-- Desktop navigation -->
    <div class="desktop-nav">
      <div class="w-20 py-2 px-2 text-white bg-neutral-900 text-center shadow-lg h-screen">
        <img src="/img/logo/la.jpg" alt="alt placeholder" class="w-8 h-8 mx-auto mb-5 mt-5">
        <span class="cursor-pointer hover:text-lightred px-2 block mb-5" @click="changePage('music')">
          <i class="fa-solid fa-music p-2 bg-gray-800 rounded-xl"></i>
        </span>
        <span class="cursor-pointer hover:text-lightred px-2 block mb-5" @click="changePage('lyrics')">
          <i class="fa-solid fa-t p-2 bg-gray-800 rounded-xl"></i>
        </span>
      </div>
    </div>
    <!-- Mobile navigation -->
    <div class="mobile-nav">
      <div class="nav-buttons">
        <span class="nav-button cursor-pointer hover:bg-gray-800" @click="changePage('music')">
          <i class="fa-solid fa-music text-white text-2xl"></i>
        </span>
        <span class="nav-button cursor-pointer hover:bg-gray-800" @click="changePage('lyrics')">
          <i class="fa-solid fa-t text-white text-2xl"></i>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import '../index.css';

export default {
  data() {
    return {
      isNavOpen: false,
    };
  },
  methods: {
    changePage(page) {
      this.$emit('page-changed', page);
    },
  },
};
</script>

<style scoped>
.desktop-nav {
  display: none;
}

@media (min-width: 640px) {

  /* Apply styles for screens with a minimum width of 769px (desktop) */
  .desktop-nav {
    display: block;

  }

  .mobile-nav {
    display: none;
  }
}

@media (max-width: 640px) {

  /* Apply styles for screens with a maximum width of 768px (mobile) */
  .desktop-nav {
    display: none;
  }

  .mobile-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: #333;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 15px;
    z-index: 1000;
    /* 增加 z-index 以確保導航欄位於最上層 */
    box-shadow: 0px -2px 4px rgba(0, 0, 0, 0.1);
    /* 添加陰影效果 */
  }

  .nav-buttons {
    display: flex;
    gap: 20px;
  }

  .nav-button {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background-color: transparent;
    transition: background-color 0.3s;
  }

  .nav-button:hover {
    background-color: #444;
  }
}</style>
