// pages/create/create.js
const app = getApp()

Page({
  data: {
    event_name: '',
    city: '',
    date: '',
    custom_suffix: '',
    group_code: ''
  },

  onEventNameInput(e) {
    this.setData({ event_name: e.detail.value })
  },

  onCityInput(e) {
    this.setData({ city: e.detail.value })
  },

  onDateChange(e) {
    this.setData({ date: e.detail.value })
  },

  onSuffixInput(e) {
    this.setData({ custom_suffix: e.detail.value.trim().toUpperCase() })
  },

  onCreate() {
    const { event_name, city, date, custom_suffix } = this.data

    // 验证必填项
    if (!event_name) {
      wx.showToast({ title: '请输入活动名称', icon: 'none' })
      return
    }
    if (!city) {
      wx.showToast({ title: '请输入城市', icon: 'none' })
      return
    }
    if (!date) {
      wx.showToast({ title: '请选择日期', icon: 'none' })
      return
    }

    wx.showLoading({ title: '生成中...' })

    wx.request({
      url: `${app.globalData.apiUrl}/api/create_activity`,
      method: 'POST',
      data: {
        event_name,
        city,
        date,
        custom_suffix
      },
      success: (res) => {
        wx.hideLoading()
        if (res.statusCode === 200 && res.data.success) {
          this.setData({
            group_code: res.data.group_code
          })
          wx.showToast({ title: '生成成功', icon: 'success' })
        } else {
          wx.showToast({ title: res.data.message || '生成失败', icon: 'none' })
        }
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({ title: '网络错误', icon: 'none' })
      }
    })
  },

  onCopy() {
    wx.setClipboardData({
      data: this.data.group_code,
      success: () => {
        wx.showToast({ title: '已复制', icon: 'success' })
      }
    })
  },

  onBackHome() {
    wx.redirectTo({
      url: '/pages/index/index'
    })
  }
})
