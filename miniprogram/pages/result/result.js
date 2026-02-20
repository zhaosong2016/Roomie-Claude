// pages/result/result.js
const app = getApp()

Page({
  data: {
    status: '', // 'matched', 'waiting', 'partial', or 'already_matched'
    match: null,
    partialMatches: [],
    isAlreadyMatched: false,  // 是否是重复提交已匹配用户
    dateMatchType: 'full',  // 日期匹配类型：'full' 或 'partial'
    countdown: 60,  // 倒计时秒数
    isPending: false  // 是否是 pending 状态（新匹配）
  },

  countdownTimer: null,  // 倒计时定时器

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
      // 使用后端返回的 is_pending 字段判断是否是新匹配
      const isPending = userInfo.is_pending === true
      const isAlreadyMatched = !isPending

      this.setData({
        status: 'matched',
        match: userInfo.match_info,
        isAlreadyMatched: isAlreadyMatched,
        dateMatchType: userInfo.date_match_type || 'full',
        isPending: isPending
      })

      // 如果是新匹配（pending 状态），启动倒计时
      if (isPending) {
        this.startCountdown()
      }
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

  onHide() {
    // 页面隐藏时（包括关闭小程序），如果是 pending 状态且未确认，自动拒绝匹配
    const { isPending, isAlreadyMatched } = this.data
    if (isPending && !isAlreadyMatched) {
      const userInfo = app.globalData.userInfo
      wx.request({
        url: `${app.globalData.apiUrl}/api/reject`,
        method: 'POST',
        header: {
          'content-type': 'application/json'
        },
        data: {
          wechat_id: userInfo.wechat_id,
          group_code: userInfo.group_code,
          openid: app.globalData.openid || ''
        }
      })
      // 标记为已处理，防止重复调用
      this.setData({
        isPending: false
      })
    }
  },

  onUnload() {
    // 清除倒计时
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer)
    }
  },

  // 启动倒计时
  startCountdown() {
    this.countdownTimer = setInterval(() => {
      const { countdown } = this.data
      if (countdown > 0) {
        this.setData({
          countdown: countdown - 1
        })
      } else {
        // 倒计时结束，自动拒绝匹配
        clearInterval(this.countdownTimer)
        this.autoRejectAndRedirect()
      }
    }, 1000)
  },

  // 自动拒绝匹配并返回首页
  autoRejectAndRedirect() {
    wx.showToast({
      title: '匹配已超时',
      icon: 'none'
    })

    const userInfo = app.globalData.userInfo
    wx.request({
      url: `${app.globalData.apiUrl}/api/reject`,
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: {
        wechat_id: userInfo.wechat_id,
        group_code: userInfo.group_code,
        openid: app.globalData.openid || ''
      },
      complete: () => {
        setTimeout(() => {
          wx.redirectTo({
            url: '/pages/index/index'
          })
        }, 1500)
      }
    })
  },

  // 静默拒绝匹配（页面卸载时调用）
  autoReject() {
    const userInfo = app.globalData.userInfo
    wx.request({
      url: `${app.globalData.apiUrl}/api/reject`,
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: {
        wechat_id: userInfo.wechat_id,
        group_code: userInfo.group_code,
        openid: app.globalData.openid || ''
      }
    })
  },

  // 复制微信号并确认匹配
  onCopyWechat() {
    const { match, isAlreadyMatched } = this.data

    // 如果是已经匹配过的，直接复制
    if (isAlreadyMatched) {
      wx.setClipboardData({
        data: match.wechat_id,
        success: () => {
          wx.showToast({
            title: '微信号已复制',
            icon: 'success'
          })
        }
      })
      return
    }

    // 清除倒计时
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer)
    }

    // 如果是新匹配，需要先确认匹配
    wx.showLoading({ title: '确认中...' })

    const userInfo = app.globalData.userInfo
    wx.request({
      url: `${app.globalData.apiUrl}/api/confirm`,
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: {
        wechat_id: userInfo.wechat_id,
        group_code: userInfo.group_code,
        openid: app.globalData.openid || ''
      },
      success: (res) => {
        wx.hideLoading()
        if (res.statusCode === 200 && res.data && res.data.success) {
          // 确认成功，复制微信号
          wx.setClipboardData({
            data: match.wechat_id,
            success: () => {
              wx.showToast({
                title: '微信号已复制',
                icon: 'success'
              })
              // 更新状态为已匹配
              this.setData({
                isAlreadyMatched: true,
                isPending: false
              })
            }
          })
        } else {
          wx.showToast({
            title: res.data && res.data.message ? res.data.message : '确认失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('确认匹配失败:', err)
        wx.showToast({
          title: '网络连接失败',
          icon: 'none'
        })
      }
    })
  },

  // 重新匹配（拒绝当前匹配或解除已有匹配）
  onRematch() {
    const { isAlreadyMatched } = this.data

    if (isAlreadyMatched) {
      // 如果是已经匹配过的，调用 unmatch 接口
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
    } else {
      // 如果是新匹配（pending 状态），调用 reject 接口
      wx.showModal({
        title: '确认拒绝',
        content: '拒绝此匹配后，将不会再匹配到此人。确定继续吗？',
        confirmText: '确定',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            this.doReject()
          }
        }
      })
    }
  },

  // 执行拒绝匹配（pending -> active）
  doReject() {
    // 清除倒计时
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer)
    }

    // 标记为已处理，防止 onUnload 重复调用
    this.setData({
      isPending: false
    })

    wx.showLoading({ title: '处理中...' })

    const userInfo = app.globalData.userInfo
    wx.request({
      url: `${app.globalData.apiUrl}/api/reject`,
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: {
        wechat_id: userInfo.wechat_id,
        group_code: userInfo.group_code,
        openid: app.globalData.openid || ''
      },
      success: (res) => {
        wx.hideLoading()
        if (res.statusCode === 200 && res.data && res.data.success) {
          wx.showToast({
            title: '已拒绝此匹配',
            icon: 'success'
          })
          setTimeout(() => {
            wx.redirectTo({
              url: '/pages/index/index'
            })
          }, 1500)
        } else {
          wx.showToast({
            title: res.data && res.data.message ? res.data.message : '操作失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('拒绝匹配失败:', err)
        wx.showToast({
          title: '网络连接失败',
          icon: 'none'
        })
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
  },

  goToWish() {
    wx.navigateTo({
      url: '/pages/wish/wish'
    })
  }
})
