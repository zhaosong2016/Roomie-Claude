// pages/index/index.js
const app = getApp()

Page({
  data: {
    showCodeInput: false,  // 是否显示输入口令区域
    groupCode: '',         // 群口令
    totalUsers: 0,         // 累计用户数
    isSubmitting: false    // 是否正在提交（防止重复点击）
  },

  onLoad() {
    this.loadStats()
  },

  // 加载统计数据
  loadStats() {
    wx.request({
      url: `${app.globalData.apiUrl}/api/stats`,
      timeout: 10000,
      success: (res) => {
        if (res.data.success) {
          // 使用后端返回的真实用户总数
          const totalUsers = res.data.stats.total_users || 0
          this.setData({
            totalUsers: totalUsers
          })
        }
      },
      fail: (err) => {
        console.error('加载统计失败:', err)
        this.setData({ totalUsers: 0 })
      }
    })
  },

  // 点击"我要拼房"
  onStartMatch() {
    this.setData({
      showCodeInput: true
    })
  },

  // 输入口令
  onCodeInput(e) {
    this.setData({
      groupCode: e.detail.value.trim().toUpperCase()
    })
  },

  // 提交口令
  onSubmitCode() {
    const { groupCode, isSubmitting } = this.data

    // 防止重复提交
    if (isSubmitting) {
      return
    }

    if (!groupCode) {
      wx.showToast({
        title: '请输入口令',
        icon: 'none'
      })
      return
    }

    // 标记为提交中
    this.setData({ isSubmitting: true })

    wx.showLoading({ title: '验证中...' })

    // 检查口令是否存在
    wx.request({
      url: `${app.globalData.apiUrl}/api/check_code`,
      method: 'GET',
      data: {
        group_code: groupCode,
        openid: app.globalData.openid || ''
      },
      timeout: 10000,
      success: (res) => {
        wx.hideLoading()

        if (res.data.success) {
          const { exists, active_count, matched_count } = res.data

          if (exists) {
            // 口令有效，显示统计信息并跳转
            const totalCount = active_count + matched_count
            console.log('准备显示弹窗，exists=true, active_count=', active_count, 'matched_count=', matched_count)

            // 保存口令到全局
            app.globalData.groupCode = groupCode

            // 显示提示信息
            wx.showToast({
              title: `口令验证成功\n等待${active_count}人 已匹配${matched_count}人`,
              icon: 'none',
              duration: 3000
            })

            // 延迟跳转
            setTimeout(() => {
              wx.navigateTo({
                url: '/pages/form/form',
                complete: () => {
                  // 跳转完成后重置状态
                  this.setData({ isSubmitting: false })
                }
              })
            }, 3000)
          } else {
            // 口令下暂无用户
            setTimeout(() => {
              wx.showModal({
                title: '⚠️ 此口令下暂无其他用户',
                content: '可能原因：\n- 口令输入错误\n- 您是第一个使用此口令的人',
                confirmText: '仍然继续',
                cancelText: '重新输入',
                success: (modalRes) => {
                  if (modalRes.confirm) {
                    // 继续
                    app.globalData.groupCode = groupCode
                    wx.navigateTo({
                      url: '/pages/form/form',
                      complete: () => {
                        this.setData({ isSubmitting: false })
                      }
                    })
                  } else {
                    // 重新输入
                    this.setData({ groupCode: '', isSubmitting: false })
                  }
                }
              })
            }, 300)
          }
        } else {
          wx.showToast({
            title: res.data.message || '验证失败',
            icon: 'none'
          })
          this.setData({ isSubmitting: false })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        })
        console.error('检查口令失败:', err)
        this.setData({ isSubmitting: false })
      }
    })
  },

  // 跳转到创建活动页
  goToCreate() {
    wx.navigateTo({
      url: '/pages/create/create'
    })
  },

  // 跳转到许愿页
  goToWish() {
    wx.navigateTo({
      url: '/pages/wish/wish'
    })
  }
})
