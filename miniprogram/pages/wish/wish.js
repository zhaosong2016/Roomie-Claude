// pages/wish/wish.js
const app = getApp()

Page({
  data: {
    content: '',
    contact: '',
    isPublic: true
  },

  onContentInput(e) {
    this.setData({
      content: e.detail.value
    })
  },

  onContactInput(e) {
    this.setData({
      contact: e.detail.value
    })
  },

  onPublicChange(e) {
    this.setData({
      isPublic: e.detail.value === 'public'
    })
  },

  onSubmit() {
    const { content, contact, isPublic } = this.data

    if (!content.trim()) {
      wx.showToast({
        title: '请输入许愿内容',
        icon: 'none'
      })
      return
    }

    wx.showLoading({ title: '提交中...' })

    wx.request({
      url: `${app.globalData.apiUrl}/api/wish`,
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      timeout: 10000,
      data: {
        content: content.trim(),
        contact: contact.trim(),
        is_public: isPublic,
        openid: app.globalData.openid || ''
      },
      success: (res) => {
        wx.hideLoading()
        if (res.statusCode === 200 && res.data && res.data.success) {
          wx.showModal({
            title: '许愿成功！',
            content: '感谢你的建议，我们会认真对待每一个许愿 💫',
            showCancel: false,
            confirmText: '返回首页',
            success: () => {
              wx.redirectTo({
                url: '/pages/index/index'
              })
            }
          })
        } else {
          wx.showToast({
            title: res.data && res.data.message ? res.data.message : '提交失败，请重试',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('提交许愿失败:', err)
        wx.showToast({
          title: '网络连接失败，请检查网络后重试',
          icon: 'none',
          duration: 2000
        })
      }
    })
  }
})
