// pages/wish/wish.js
const app = getApp()

Page({
  data: {
    type: '',
    content: '',
    contact: '',
    isPublic: true
  },

  onTypeChange(e) {
    this.setData({
      type: e.detail.value
    })
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
    const { type, content, contact, isPublic } = this.data

    if (!type) {
      wx.showToast({
        title: '请选择类型',
        icon: 'none'
      })
      return
    }

    if (!content.trim()) {
      wx.showToast({
        title: '请输入内容',
        icon: 'none'
      })
      return
    }

    // 根据类型设置不同的成功提示
    const successMessages = {
      suggestion: {
        title: '感谢你的建议！',
        content: '我们会认真考虑'
      },
      issue: {
        title: '感谢反馈！',
        content: '我们会尽快处理'
      },
      wish: {
        title: '许愿成功！',
        content: '我们会努力实现 ✨'
      },
      praise: {
        title: '谢谢你的鼓励！',
        content: '这是我们前进的动力 ❤️'
      }
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
        type: type,
        content: content.trim(),
        contact: contact.trim(),
        is_public: isPublic,
        openid: app.globalData.openid || ''
      },
      success: (res) => {
        wx.hideLoading()
        if (res.statusCode === 200 && res.data && res.data.success) {
          const message = successMessages[type] || successMessages.suggestion
          wx.showModal({
            title: message.title,
            content: message.content,
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
        console.error('提交失败:', err)
        wx.showToast({
          title: '网络连接失败，请检查网络后重试',
          icon: 'none',
          duration: 2000
        })
      }
    })
  }
})
