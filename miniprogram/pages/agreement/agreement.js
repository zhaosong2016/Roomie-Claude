// pages/agreement/agreement.js
Page({
  data: {
    type: 'user' // 'user' 或 'privacy'
  },

  onLoad(options) {
    // 从页面参数获取类型
    if (options.type) {
      this.setData({
        type: options.type
      })
    }
  }
})
