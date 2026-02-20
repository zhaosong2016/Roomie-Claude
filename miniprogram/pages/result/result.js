// pages/result/result.js
const app = getApp()

Page({
  data: {
    status: '', // 'matched', 'waiting', 'partial', or 'already_matched'
    match: null,
    partialMatches: [],
    isAlreadyMatched: false,  // 是否是重复提交已匹配用户
    dateMatchType: 'full'  // 日期匹配类型：'full' 或 'partial'
  },

  onLoad() {
    const userInfo = app.globalData.userInfo
    if (!userInfo) {
      wx.showToast({ title: '数据错误', icon: 'none' })
      setTimeout(() => {
        wx.redirectTo({ url: '/pages/index/index' })
      }, 1500)
      return
    }

    // 根据返回的数据判断状态
    if (userInfo.matched && userInfo.match_info) {
      // 检查是否是重复提交（message包含"已匹配成功"）
      const isAlreadyMatched = userInfo.message && userInfo.message.includes('已匹配成功')

      this.setData({
        status: 'matched',
        match: userInfo.match_info,
        isAlreadyMatched: isAlreadyMatched,
        dateMatchType: userInfo.date_match_type || 'full'
      })
    } else if (userInfo.partial_matches && userInfo.partial_matches.length > 0) {
      this.setData({
        status: 'partial',
        partialMatches: userInfo.partial_matches
      })
    } else {
      this.setData({
        status: 'waiting'
      })
    }
  },

  // 复制微信号
  onCopyWechat() {
    const { match } = this.data
    wx.setClipboardData({
      data: match.wechat_id,
      success: () => {
        wx.showToast({
          title: '微信号已复制',
          icon: 'success'
        })
      }
    })
  },

  // 重新匹配
  onRematch() {
    wx.showModal({
      title: '确认重新匹配',
      content: '解除当前匹配后，对方也会被解绑。确定继续吗？',
      confirmText: '确定',
      cancelText: '取消',
      success: (res) => {
        if (res.confirm) {
          this.doUnmatch()
        }
      }
    })
  },

  // 执行解除匹配
  doUnmatch() {
    const app = getApp()
    const { match } = this.data
    wx.showLoading({ title: '解除中...' })

    // 使用匹配对象的微信号（因为是对方要解绑）
    // 实际上应该传当前用户的微信号，从userInfo获取
    const currentWechatId = app.globalData.userInfo.wechat_id

    if (!currentWechatId) {
      wx.hideLoading()
      wx.showToast({ title: '获取用户信息失败', icon: 'none' })
      return
    }

    wx.request({
      url: `${app.globalData.apiUrl}/api/unmatch`,
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      timeout: 10000,
      data: {
        wechat_id: currentWechatId,
        group_code: app.globalData.groupCode,
        openid: app.globalData.openid || ''
      },
      success: (res) => {
        wx.hideLoading()
        if (res.data.success) {
          wx.showToast({
            title: '已解除匹配',
            icon: 'success',
            duration: 2000
          })
          setTimeout(() => {
            wx.redirectTo({ url: '/pages/index/index' })
          }, 10000)
        } else {
          wx.showToast({
            title: res.data.message || '解除失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('解除匹配失败:', err)
        wx.showToast({
          title: '网络连接失败，请重试',
          icon: 'none'
        })
      }
    })
  },

  onBackHome() {
    wx.redirectTo({
      url: '/pages/index/index'
    })
  }
})
